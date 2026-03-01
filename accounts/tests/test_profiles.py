import pytest
from datetime import date, timedelta
from django.db import IntegrityError
from rozumity.factories.accounts import UserFactory
from django.urls import reverse
from rest_framework import status

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


import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import ClientProfile, ExpertProfile
from rozumity.factories.accounts import UserFactory, EducationFactory 

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestProfileAPIDetailed:
    """
    In-depth testing for Profile views including field validation, 
    many-to-many relationships, and complex permissions.
    """

    # --- CLIENT PROFILE DEEP TESTS ---

#    async def test_client_cannot_update_another_client(self, adrf_client):
#       """
#        SECURITY: Verify a client cannot PATCH someone else's profile.
#        """
#        victim = await UserFactory.acreate(is_client=True)
#        attacker = await UserFactory.acreate(is_client=True)
#        url = reverse('accounts:client-profile-detail', kwargs={'pk': victim.pk})
#        
#        adrf_client.force_authenticate(user=attacker)
#        response = await adrf_client.patch(url, data={"first_name": "Hacked"})
#        
#        # Ожидаем 403 Forbidden или 404 в зависимости от твоей логики GetObject
#        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
#        
#        # Проверяем, что данные не изменились
#        profile = await ClientProfile.objects.aget(user=victim)
#        assert profile.first_name != "Hacked"

#    async def test_client_profile_full_update_put(self, adrf_client):
#        """
#        VALIDATION: Verify a full update (PUT) with all fields.
#        """
#        user = await UserFactory.acreate(is_client=True)
#        url = reverse('accounts:client-profile-detail', kwargs={'pk': user.pk})
#        adrf_client.force_authenticate(user=user)
#        
#        payload = {
#            "first_name": "Ivan",
#            "last_name": "Ivanov",
#            "gender": 1, # FEMALE из твоих IntegerChoices
#            "country": "UA",
#            "date_birth": "1995-05-20"
#        }
#        
#        response = await adrf_client.put(url, data=payload)
#        assert response.status_code == status.HTTP_200_OK
#        
#        # Проверка через модель (включая асинхронные проперти)
#        profile = await ClientProfile.objects.aget(user=user)
#        assert profile.gender == 1
#        assert await profile.name == "Ivan Ivanov"
#        assert await profile.is_adult is True

    # --- EXPERT PROFILE DEEP TESTS ---

    async def test_expert_update_education_m2m(self, adrf_client):
        """
        RELATIONSHIPS: Test ManyToMany updates for Expert education.
        """
        expert_user = await UserFactory.acreate(is_expert=True)
        # Если есть Education, создаем его (замени на свою фабрику)
        # edu = await EducationFactory.acreate() 
        
        url = reverse('accounts:expert-profile-detail', kwargs={'pk': expert_user.pk})
        adrf_client.force_authenticate(user=expert_user)
        
        # Проверяем обновление списка стран и текстового поля образования
        payload = {
            "education_extra": "Advanced Psychology Course",
            "countries_allowed": ["UA", "PL", "US"]
        }
        
        response = await adrf_client.patch(url, data=payload)
        assert response.status_code == status.HTTP_200_OK
        
        expert_profile = await ExpertProfile.objects.aget(user=expert_user)
        assert expert_profile.education_extra == "Advanced Psychology Course"
        assert len(expert_profile.countries_allowed) == 3
        assert "PL" in expert_profile.countries_allowed

    async def test_expert_profile_read_only_fields(self, adrf_client):
        """
        INTEGRITY: Verify that sensitive fields like 'user' cannot be changed via API.
        """
        expert_user = await UserFactory.acreate(is_expert=True)
        other_user = await UserFactory.acreate()
        url = reverse('accounts:expert-profile-detail', kwargs={'pk': expert_user.pk})
        
        adrf_client.force_authenticate(user=expert_user)
        # Пытаемся перепривязать профиль к другому пользователю
        payload = {"user": other_user.pk}
        
        await adrf_client.patch(url, data=payload)
        
        # Профиль все еще должен принадлежать исходному юзеру
        profile = await ExpertProfile.objects.aget(pk=expert_user.pk)
        assert profile.user_id == expert_user.pk

    # --- SHARED / EDGE CASES ---

    async def test_profile_partial_update_validation_error(self, adrf_client):
        """
        VALIDATION: Test invalid data (e.g. wrong country code).
        """
        user = await UserFactory.acreate(is_client=True)
        url = reverse('accounts:client-profile-detail', kwargs={'pk': user.pk})
        adrf_client.force_authenticate(user=user)
        
        # 'INVALID' не является валидным кодом страны по ISO
        response = await adrf_client.patch(url, data={"country": "INVALID"})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "country" in response.data

    async def test_expert_can_view_client_profile_if_admin(self, adrf_client):
        """
        PERMISSIONS: Expert with is_staff=True should access client profiles.
        """
        client = await UserFactory.acreate(is_client=True)
        admin_expert = await UserFactory.acreate(is_expert=True, is_staff=True)
        url = reverse('accounts:client-profile-detail', kwargs={'pk': client.pk})
        
        adrf_client.force_authenticate(user=admin_expert)
        response = await adrf_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
