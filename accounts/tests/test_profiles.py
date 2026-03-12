import pytest
from django.db import IntegrityError
from accounts.models import ClientProfile, ExpertProfile, StaffProfile
from rozumity.factories.accounts import UserFactory

@pytest.mark.django_db(transaction=True)  # Required for on_commit hooks
@pytest.mark.asyncio
class TestProfilesWithLifecycle:
    """
    Tests for profile creation via overridden save/asave 
    utilizing transaction.on_commit.
    """

    async def test_creates_correct_profile_type_asave(self):
        """
        Verify asave(): correct profile type is created after transaction commit.
        """
        # 1. Expert
        expert_user = await UserFactory.acreate(is_staff=False, is_expert=True)
        # In transaction=True tests, on_commit triggers immediately after acreate
        assert await ExpertProfile.objects.filter(user=expert_user).aexists()

        # 2. Staff (is_staff=True is the model default)
        staff_user = await UserFactory.acreate(is_staff=True, is_expert=False)
        assert await StaffProfile.objects.filter(user=staff_user).aexists()

        # 3. Client
        client_user = await UserFactory.acreate(is_staff=False, is_expert=False)
        assert await ClientProfile.objects.filter(user=client_user).aexists()

    async def test_manual_profile_creation_fails(self):
        """
        Verify get_or_create logic inside _create_profile_sync.
        Even if a profile is created manually before commit, the method 
        should not crash, but uniqueness by user must be enforced.
        """
        # Create user; asave() schedules the on_commit task
        user = await UserFactory.acreate(is_staff=False, is_expert=False)
        
        # Profile is already created by the on_commit hook
        assert await ClientProfile.objects.filter(user=user).acount() == 1
        
        with pytest.raises(IntegrityError):
            # Second manual creation attempt should trigger a DB-level IntegrityError
            await ClientProfile.objects.acreate(user=user)

    async def test_profile_not_created_on_update(self):
        """
        Verify is_new flag: profiles should not attempt re-creation on update.
        """
        user = await UserFactory.acreate(email="test@test.com")
        initial_profile_id = (await ClientProfile.objects.aget(user=user)).pk
        
        # Trigger asave() via field update
        user.is_active = False
        await user.asave()
        
        # Verify profile ID remains identical (no re-creation occurred)
        current_profile = await ClientProfile.objects.aget(user=user)
        assert current_profile.pk == initial_profile_id

    async def test_cascade_delete_user_deletes_profile(self):
        """
        Verify DB-level CASCADE: deleting a user must remove the profile.
        """
        user = await UserFactory.acreate()
        user_id = user.id
        
        await user.adelete()
        
        # Check existence via filter to avoid DoesNotExist exceptions
        assert not await ClientProfile.objects.filter(user_id=user_id).aexists()

    async def test_is_filled_with_strip_logic(self):
        """
        Verify that a single space " " is treated as an empty field by .strip().
        """
        user = await UserFactory.acreate(is_staff=False, is_expert=False)
        profile = await ClientProfile.objects.aget(user=user)
        
        profile.first_name = " "  # Space instead of actual name
        profile.country = "UA"
        await profile.asave()
        
        # is_filled logic should return False due to .strip()
        assert await profile.is_filled is False

    async def test_expert_countries_allowed_list(self):
        """
        Verify storage and retrieval of the countries list.
        Uses sorted comparison to avoid ordering issues.
        """
        user = await UserFactory.acreate(is_expert=True, is_staff=False)
        expert = await ExpertProfile.objects.aget(user=user)
        
        # Original list
        countries = ["UA", "DE", "PL"]
        expert.countries_allowed = countries
        await expert.asave()
        
        refreshed = await ExpertProfile.objects.aget(user=user)
        
        # Convert Country objects to strings
        result_codes = [str(c) for c in refreshed.countries_allowed]
        
        # Compare sorted versions because the field may normalize order alphabetically
        assert sorted(result_codes) == sorted(countries)
