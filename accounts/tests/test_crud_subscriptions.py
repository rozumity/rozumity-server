import pytest
import pytest_asyncio
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.views import SubscriptionPlanViewSet
from rozumity.factories.accounts import SubscriptionPlanFactory, UserFactory

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestSubscriptionPlanAPI:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.factory = APIRequestFactory()
        self.user = await UserFactory.acreate()
        
        # Viewset actions mapping for DRF
        self.view_list = SubscriptionPlanViewSet.as_view({'get': 'alist'})
        self.view_detail = SubscriptionPlanViewSet.as_view({'get': 'aretrieve'})

    # --- Read Operations ---

    async def test_authenticated_user_can_list_plans(self):
        """GET (list) Check: Authenticated user can see all available subscription plans"""
        await SubscriptionPlanFactory.acreate_batch(3)

        request = self.factory.get("/accounts/subscriptions/")
        force_authenticate(request, user=self.user)
        response = await self.view_list(request)

        assert response.status_code == status.HTTP_200_OK
        # Assuming your serializer returns a list or standard DRF pagination
        assert len(response.data) >= 3

    async def test_authenticated_user_can_retrieve_plan(self):
        """GET (retrieve) Check: User can view details of a specific plan"""
        plan = await SubscriptionPlanFactory.acreate(title="Premium Plan")

        request = self.factory.get(f"/accounts/subscriptions/{plan.id}/")
        force_authenticate(request, user=self.user)
        response = await self.view_detail(request, pk=plan.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Premium Plan"

    # --- Permissions & Restrictions ---

    async def test_anonymous_user_cannot_access_plans(self):
        """Permissions Check: Unauthenticated user is denied access to plans"""
        request = self.factory.get("/accounts/subscriptions/")
        # No authentication
        response = await self.view_list(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
