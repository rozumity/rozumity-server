import pytest
import pytest_asyncio
from datetime import date
from django.urls import reverse
from rest_framework import status
from django.core.cache import cache
from rozumity.factories.accounts import (
    ExpertProfileFactory, UniversityFactory, SpecialityFactory
)

from accounts.models import User, ClientProfile, ExpertProfile
from unittest.mock import AsyncMock, patch
from datetime import date
from accounts.models import Education, ExpertProfile, University, Speciality, TherapyContract, SubscriptionPlan
from adrf.test import AsyncAPIClient as APIClient

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestEducationInvalidationIntegration:

    @pytest_asyncio.fixture
    async def education_instance(self, db):
        """
        Create a valid Education instance with all required fields.
        Ensures dependencies exist in the test database.
        """
        # 1. Create dependencies first
        user, _ = await User.objects.aget_or_create(
            email="test_expert@rozumity.com",
            defaults={"is_active": True}
        )
        expert, _ = await ExpertProfile.objects.aget_or_create(user=user)
        
        university, _ = await University.objects.aget_or_create(
            title="Kyiv National University"
        )
        
        speciality, _ = await Speciality.objects.aget_or_create(
            title="Psychology"
        )
        
        # 2. Create the instance
        return await Education.objects.acreate(
            expert=expert,
            university=university,
            speciality=speciality,
            degree=1,
            date_start=date(2020, 9, 1),
            date_end=date(2024, 6, 30)
        )

    async def test_patch_returns_correct_data(self, admin_user, education_instance):
        """
        Verify the actual data received by the user (JSON response).
        """
        # 1. Use client instead of factory
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        url = reverse("accounts:education-detail", kwargs={"pk": education_instance.pk})
        new_degree = 3
        
        # 2. Perform the actual request
        response = await client.patch(url, data={"degree": new_degree}, format='json')
        
        # 3. Compare raw data from the response
        assert response.status_code == 200
        # Check that the degree field is updated in the JSON response
        assert response.data["degree"] == new_degree
        # Check that the object ID remains the same
        assert response.data["id"] == education_instance.id
        await education_instance.arefresh_from_db()
        assert education_instance.degree == new_degree

    async def test_delete_returns_no_content(self, admin_user, education_instance):
        """
        Verify status code and absence of data upon deletion.
        """
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse("accounts:education-detail", kwargs={"pk": education_instance.pk})
        
        response = await client.delete(url)
        
        assert response.status_code == 204
        assert response.data is None


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestTherapyContractInvalidation:

    @pytest_asyncio.fixture
    async def contract_instance(self, db):
        """Create a contract with a client and an expert."""
        u_client = await User.objects.acreate(email="client@test.com", password="password")
        u_expert = await User.objects.acreate(email="expert@test.com", password="password")
        
        client_profile = await ClientProfile.objects.acreate(user=u_client)
        expert_profile = await ExpertProfile.objects.acreate(user=u_expert)
        
        plan = await SubscriptionPlan.objects.acreate(
            title="Premium", 
            has_ai=True,
            price=100.00
        )
        
        contract = await TherapyContract.objects.acreate(
            client=client_profile,
            expert=expert_profile,
            client_plan_days=0
        )
        return contract, expert_profile, u_expert, u_client, plan

    async def test_expert_update_contract_triggers_dual_invalidation(self, contract_instance):
        """
        Verify that a contract update by an expert invalidates cache for both the expert and the client.
        """
        contract, expert_profile, u_expert, u_client, new_plan = contract_instance
        
        client = APIClient()
        client.force_authenticate(user=u_expert)
        
        url = reverse("accounts:therapy-contract-detail", kwargs={"pk": contract.pk})
        
        payload = {"expert_plan": new_plan.id, "expert_plan_days": 30}

        with patch("adrf_caching.utils.CacheUtils.incr_user_version", new_callable=AsyncMock) as mock_incr:
            response = await client.patch(url, data=payload, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            
            called_user_ids = [call.args[0] for call in mock_incr.call_args_list]
            
            assert u_client.id in called_user_ids, "Client cache was NOT invalidated!"
            assert u_expert.id in called_user_ids, "Expert cache was NOT invalidated!"
            assert mock_incr.call_count >= 2

            await contract.arefresh_from_db()
            assert contract.expert_plan_id == new_plan.id

    async def test_post_create_triggers_cross_invalidation_only_with_mixin(self, db):
        # 1. Create two DIFFERENT users
        u_expert = await User.objects.acreate(email="expert@test.com", password="password")
        u_client = await User.objects.acreate(email="client@test.com", password="password")
        
        # Profiles
        e_profile = await ExpertProfile.objects.acreate(user=u_expert)
        c_profile = await ClientProfile.objects.acreate(user=u_client)
        
        plan = await SubscriptionPlan.objects.acreate(title="Test", price=100)

        client = APIClient()
        client.force_authenticate(user=u_expert)
        url = reverse("accounts:therapy-contract-create")

        payload = {
            "client": c_profile.id,
            "expert": e_profile.id,
            "expert_plan": plan.id,
            "expert_plan_days": 30
        }

        with patch("adrf_caching.utils.CacheUtils.incr_user_version", new_callable=AsyncMock) as mock_incr:
            response = await client.post(url, data=payload, format='json')
            assert response.status_code == 201

            called_ids = [call.args[0] for call in mock_incr.call_args_list]
            
            # Expert (author) is invalidated by the base CreateModelMixin.
            assert u_expert.id in called_ids
            
            # Client WITHOUT CacheInvalidationMixin is NOT invalidated.
            # This test will fail if the mixin is removed from ListCreateTherapyContractView.
            assert u_client.id in called_ids, "Client cache not cleared upon contract creation by expert!"
    
    async def test_patch_triggers_cache_invalidation_call(self, db):
        """
        Test without fixtures. Verifies user version increment call during PATCH.
        """
        # 1. Create all necessary data inline
        u_client = await User.objects.acreate(email="patch_client@test.com")
        u_expert = await User.objects.acreate(email="patch_expert@test.com")
        
        c_profile = await ClientProfile.objects.acreate(user=u_client)
        e_profile = await ExpertProfile.objects.acreate(user=u_expert)
        
        plan = await SubscriptionPlan.objects.acreate(
            title="Standard", price=50.00, has_ai=False
        )
        
        contract = await TherapyContract.objects.acreate(
            client=c_profile,
            expert=e_profile,
            expert_plan_days=0
        )

        client = APIClient()
        client.force_authenticate(user=u_expert)
        url = reverse("accounts:therapy-contract-detail", kwargs={"pk": contract.pk})
        
        # Use valid IntegerChoices (14 = WEEK2)
        payload = {"expert_plan_days": 14}
    
        # 2. Patch and verify
        with patch("adrf_caching.utils.CacheUtils.incr_user_version", new_callable=AsyncMock) as mock_incr:
            response = await client.patch(url, data=payload, format='json')
            
            assert response.status_code == 200, f"Backend returned {response.status_code}: {response.data}"
            
            # Verify that calls were made for both contract participants
            assert mock_incr.call_count >= 2
            mock_incr.assert_any_call(u_client.id)
            mock_incr.assert_any_call(u_expert.id)


@pytest.mark.django_db
class TestEducationFullCacheCycle:
    @pytest.mark.asyncio
    async def test_education_crud_cycle_with_acreate(self):
        # 0. Setup
        cache.clear()
        client = APIClient()
        
        # Create profile with user preloading via custom acreate
        expert_profile = await ExpertProfileFactory.acreate(select_related=['user'])
        university = await UniversityFactory.acreate()
        speciality = await SpecialityFactory.acreate()
        
        user = expert_profile.user
        client.force_authenticate(user=user)
        
        # In DRF, List and Create are typically handled by the same URL
        list_url = reverse("accounts:education-create") 
        
        # --- 1. CREATE ---
        payload = {
            "university": university.id,
            "speciality": speciality.id,
            "date_start": "2015-09-01",
            "date_end": "2019-06-30",
            "degree": 3  # MASTER
        }
        res = await client.post(list_url, data=payload, format='json')
        assert res.status_code == status.HTTP_201_CREATED, f"Errors: {res.data}"
        
        edu_id = res.data['id']
        detail_url = reverse("accounts:education-detail", kwargs={"pk": edu_id})

        # --- 2. GET LIST ---
        res_list = await client.get(list_url)
        assert res_list.status_code == 200
        assert len(res_list.data['results']) == 1
        assert res_list.data['results'][0]['degree'] == 3

        # --- 3. CACHE HIT VERIFICATION ---
        # Delete directly from DB. ADRF should return data from cache.
        await Education.objects.filter(id=edu_id).adelete()
        
        res_cached = await client.get(list_url)
        assert len(res_cached.data['results']) == 1, "Data should be in cache"
        assert res_cached.data['results'][0]['degree'] == 3

        # --- 4. UPDATE / PATCH (Invalidation) ---
        # Restore in DB with correct fields
        await Education.objects.acreate(
            id=edu_id, 
            university=university, 
            speciality=speciality,
            date_start="2015-09-01", 
            date_end="2019-06-30", 
            degree=3, 
            expert=expert_profile # Pass the profile instance as expected by the model
        )
        
        # Change degree to Doctor (5)
        patch_res = await client.patch(detail_url, data={"degree": 5}, format='json')
        assert patch_res.status_code == status.HTTP_200_OK

        # --- 5. INVALIDATION VERIFICATION ---
        # Cache should be cleared; expecting new data (Doctor)
        res_fresh = await client.get(list_url)
        assert res_fresh.data['results'][0]['degree'] == 5, "Cache not cleared, received old value"

        # --- 6. DELETE ---
        await client.delete(detail_url)
        res_final = await client.get(list_url)
        
        # Check the results list specifically
        assert len(res_final.data['results']) == 0
