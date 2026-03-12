import pytest
import pytest_asyncio
from datetime import date, timedelta
from django.db import IntegrityError
from rozumity.factories.accounts import UserFactory
from django.urls import reverse
from rest_framework import status

from accounts.models import User, ClientProfile, ExpertProfile, StaffProfile
from adrf.test import AsyncAPIRequestFactory
from accounts.views import EducationRetrieveUpdateDestroyView
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
        Проверяем реально пришедшие юзеру данные (JSON response)
        """
        # 1. Используем клиент вместо фабрики
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        url = reverse("accounts:education-detail", kwargs={"pk": education_instance.pk})
        new_degree = 3
        
        # 2. Выполняем реальный запрос
        response = await client.patch(url, data={"degree": new_degree}, format='json')
        
        # 3. Сравниваем сырые данные из ответа
        assert response.status_code == 200
        # Проверяем, что в JSON ответе поле degree обновилось
        assert response.data["degree"] == new_degree
        # Проверяем, что ID объекта тот же самый
        assert response.data["id"] == education_instance.id
        await education_instance.arefresh_from_db()
        assert education_instance.degree == new_degree

    async def test_delete_returns_no_content(self, admin_user, education_instance):
        """
        Проверяем статус и отсутствие данных при удалении
        """
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse("accounts:education-detail", kwargs={"pk": education_instance.pk})
        
        response = await client.delete(url)
        
        assert response.status_code == 204
        assert response.data is None

    async def test_patch_triggers_cache_invalidation(self, admin_user, education_instance):
        """
        Этот тест УПАДЕТ, если убрать CacheInvalidationMixin из вьюхи.
        """
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse("accounts:education-detail", kwargs={"pk": education_instance.pk})
        
        # Патчим утилиту, которая вызывается ТОЛЬКО в миксине
        with patch("adrf_caching.utils.CacheUtils.incr_user_version", new_callable=AsyncMock) as mock_incr:
            response = await client.patch(url, data={"degree": 3}, format='json')
            
            assert response.status_code == 200
            
            # БЕЗ миксина этот assert выдаст ошибку, так как никто не вызовет инкремент
            assert mock_incr.call_count >= 1
            mock_incr.assert_any_call(education_instance.expert_id)
            mock_incr.assert_any_call(admin_user.id)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestTherapyContractInvalidation:

    @pytest_asyncio.fixture
    async def contract_instance(self, db):
        """Создаем контракт с клиентом и экспертом."""
        u_client = await User.objects.acreate(email="client@test.com", password="password")
        u_expert = await User.objects.acreate(email="expert@test.com", password="password")
        
        client_profile = await ClientProfile.objects.acreate(user=u_client)
        expert_profile = await ExpertProfile.objects.acreate(user=u_expert)
        
        # Добавляем обязательную цену (и валюту, если она есть в модели)
        plan = await SubscriptionPlan.objects.acreate(
            title="Premium", 
            has_ai=True,
            price=100.00  # <--- Добавь это поле
        )
        
        contract = await TherapyContract.objects.acreate(
            client=client_profile,
            expert=expert_profile,
            client_plan_days=0
        )
        return contract, expert_profile, u_expert, u_client, plan

    async def test_expert_update_contract_invalidates_client_cache(self, contract_instance):
        """
        Verifies that an update by one participant (expert) correctly 
        triggers cache invalidation for related participants (client).
        """
        contract, expert_profile, u_expert, u_client, new_plan = contract_instance
        
        client = APIClient()
        # Authenticate as the expert to modify the shared contract
        client.force_authenticate(user=u_expert)
        
        url = reverse("accounts:therapy-contract-detail", kwargs={"pk": contract.pk})
        
        # Payload: transition the expert to a new subscription plan
        payload = {
            "expert_plan": new_plan.id,
            "expert_plan_days": 30
        }

        # Patch the utility to capture async invalidation calls
        with patch("adrf_caching.utils.CacheUtils.incr_user_version", new_callable=AsyncMock) as mock_incr:
            response = await client.patch(url, data=payload, format='json')
            
            assert response.status_code == status.HTTP_200_OK
            
            # EXPECTATION: At least 2 invalidation calls must occur:
            # 1. For the requester (expert)
            # 2. For the related user ID defined in 'invalidate_user_fields' (client)
            
            # Extract all user IDs that were triggered for version increment
            called_user_ids = [call.args[0] for call in mock_incr.call_args_list]
            
            assert u_client.id in called_user_ids, "Client cache was NOT invalidated after expert update!"
            assert u_expert.id in called_user_ids, "Expert cache (requester) was NOT invalidated!"
            
            # Verify data persistence in the database
            await contract.arefresh_from_db()
            assert contract.expert_plan_id == new_plan.id
