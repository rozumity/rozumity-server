import pytest
import uuid
from datetime import date, timedelta
from django.core.exceptions import SynchronousOnlyOperation
from django.db import IntegrityError
from accounts.models import User, AbstractProfile
from rozumity.factories.accounts import UserFactory, ClientProfileFactory, ExpertProfileFactory, TherapyContractFactory


import pytest
from django.db import IntegrityError
from accounts.models import User, ClientProfile, ExpertProfile, StaffProfile

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestProfilesWithSignals:
    """
    Detailed tests for profiles accounting for post_save and post_delete signals.
    """

    async def test_signal_creates_correct_profile_type(self):
        """
        Verify that create_user_profile signal picks the right model 
        based on User flags.
        """
        # 1. Test Staff creation
        staff_user = await UserFactory.acreate(is_staff=True, is_expert=False)
        assert await StaffProfile.objects.filter(user=staff_user).aexists()
        assert not await ClientProfile.objects.filter(user=staff_user).aexists()

        # 2. Test Expert creation
        expert_user = await UserFactory.acreate(is_staff=False, is_expert=True)
        assert await ExpertProfile.objects.filter(user=expert_user).aexists()

        # 3. Test Client creation (default)
        client_user = await UserFactory.acreate(is_staff=False, is_expert=False)
        assert await ClientProfile.objects.filter(user=client_user).aexists()

    async def test_manual_profile_creation_fails_due_to_signal(self):
        """
        Verify that we can't manually create a profile if signal already did it.
        This covers your IntegrityError from previous run.
        """
        user = await UserFactory.acreate() # Signal creates ClientProfile here
        
        with pytest.raises(IntegrityError):
            # Attempt to create another one manually
            await ClientProfile.objects.acreate(user=user)

    async def test_delete_profile_signal_deletes_user(self):
        """
        Test the post_delete signal: deleting a profile should delete the associated user.
        """
        user = await UserFactory.acreate()
        profile = await ClientProfile.objects.aget(user=user)
        
        # Deleting profile should trigger delete_profile signal
        await profile.adelete()
        
        # Verify user is gone
        assert not await User.objects.filter(id=user.id).aexists()

    async def test_cascade_delete_user_deletes_profile(self):
        """
        Verify Django's native CASCADE. 
        We use ID explicitly because instance loses its PK after delete.
        """
        user = await UserFactory.acreate()
        user_id = user.id # Save UUID before it's gone
        assert await ClientProfile.objects.filter(user_id=user_id).aexists()
        
        await user.adelete()
        
        # Filter by ID, not by the object instance
        assert not await ClientProfile.objects.filter(user_id=user_id).aexists()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestProfileCalculationsDetailed:
    """
    Detailed check of fields and edge cases for properties.
    """

    async def test_gender_choices_all_values(self):
        """
        Iterate through all gender choices to ensure they render correctly.
        """
        user = await UserFactory.acreate()
        profile = await ClientProfile.objects.aget(user=user)
        
        for choice_value, label in ClientProfile.GenderChoices.choices:
            profile.gender = choice_value
            await profile.asave()
            assert await profile.gender_verbose == label

    async def test_is_filled_extreme_cases(self):
        """
        Since you added .strip(), space " " is now considered empty.
        The test should reflect this improved logic.
        """
        user = await UserFactory.acreate()
        profile = await ClientProfile.objects.aget(user=user)
        
        # Test 1: Blank names + Country (Should be False because of .strip())
        profile.first_name = " "
        profile.last_name = ""
        profile.country = "UA"
        await profile.asave()
        assert await profile.is_filled is False # Correct behavior with .strip()

        # Test 2: Actual name + Country
        profile.first_name = "Alex"
        await profile.asave()
        assert await profile.is_filled is True

    async def test_expert_specific_fields(self):
        """
        Test education_extra and multiple countries.
        """
        user = await UserFactory.acreate(is_expert=True, is_staff=False)
        expert = await ExpertProfile.objects.aget(user=user)
        
        expert.education_extra = "PhD in Psychology"
        expert.countries_allowed = ["UA", "US"]
        await expert.asave()
        
        refreshed = await ExpertProfile.objects.aget(user=user)
        assert refreshed.education_extra == "PhD in Psychology"
        assert len(refreshed.countries_allowed) == 2

    async def test_staff_profile_existence(self):
        """
        Set explicit birth date to avoid leap year calculation issues.
        """
        user = await UserFactory.acreate(is_staff=True)
        staff = await StaffProfile.objects.aget(user=user)
        
        assert staff.gender == StaffProfile.GenderChoices.HIDE
        
        # Set birthdate 20 years ago to be safely > 18
        staff.date_birth = date.today() - timedelta(days=20*365)
        await staff.asave()
        
        assert await staff.is_adult is True
