import pytest
import pytest_asyncio
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.views import RetrieveUpdateClientProfileView, RetrieveUpdateExpertProfileView
from rozumity.factories.accounts import ClientProfileFactory, ExpertProfileFactory

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestProfileAPI:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.factory = APIRequestFactory()
        
        # Setup Client
        self.client_profile = await ClientProfileFactory.acreate(select_related=['user'])
        self.client_user = self.client_profile.user
        
        # Setup Expert
        self.expert_profile = await ExpertProfileFactory.acreate(select_related=['user'])
        self.expert_user = self.expert_profile.user

        # Views
        self.client_view = RetrieveUpdateClientProfileView.as_view()
        self.expert_view = RetrieveUpdateExpertProfileView.as_view()

    # --- Client Profile Tests ---

    async def test_client_can_retrieve_own_profile(self):
        """GET Check: Client can retrieve their own profile data"""
        request = self.factory.get(f"/accounts/profiles/client/{self.client_profile.id}/")
        force_authenticate(request, user=self.client_user)
        response = await self.client_view(request, pk=self.client_profile.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == self.client_profile.first_name

    async def test_client_can_patch_own_profile(self):
        """PATCH Check: Client can update their first name"""
        payload = {"first_name": "UpdatedName"}
        request = self.factory.patch(f"/accounts/profiles/client/{self.client_profile.id}/", payload)
        force_authenticate(request, user=self.client_user)
        response = await self.client_view(request, pk=self.client_profile.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "UpdatedName"

    # --- Expert Profile Tests ---

    async def test_expert_can_retrieve_own_profile(self):
        """GET Check: Expert can retrieve their own profile data"""
        request = self.factory.get(f"/accounts/profiles/expert/{self.expert_profile.id}/")
        force_authenticate(request, user=self.expert_user)
        response = await self.expert_view(request, pk=self.expert_profile.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["education_extra"] == self.expert_profile.education_extra

    # --- Cross-Role & Security Tests ---

    async def test_client_cannot_update_expert_profile(self):
        """Permissions Check: Client is forbidden from updating an Expert profile"""
        payload = {"education_extra": "I am an expert now"}
        request = self.factory.patch(f"/accounts/profiles/expert/{self.expert_profile.id}/", payload)
        force_authenticate(request, user=self.client_user)
        response = await self.expert_view(request, pk=self.expert_profile.id)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_expert_cannot_update_client_profile(self):
        """Permissions Check: Expert is forbidden from updating a Client profile"""
        payload = {"first_name": "ExpertTryingToHack"}
        request = self.factory.patch(f"/accounts/profiles/client/{self.client_profile.id}/", payload)
        force_authenticate(request, user=self.expert_user)
        response = await self.client_view(request, pk=self.client_profile.id)

        # Should be 403 Forbidden due to IsProfileOwner
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_anonymous_cannot_access_profiles(self):
        """Permissions Check: Unauthorized access is denied for profiles"""
        request = self.factory.get(f"/accounts/profiles/client/{self.client_profile.id}/")
        response = await self.client_view(request, pk=self.client_profile.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_client_can_retrieve_expert_profile(self):
        """GET Check: Client can retrieve expert profile data"""
        request = self.factory.get(f"/accounts/profiles/expert/{self.expert_profile.id}/")
        force_authenticate(request, user=self.client_user)
        response = await self.expert_view(request, pk=self.expert_profile.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["education_extra"] == self.expert_profile.education_extra

    async def test_expert_cannot_retrieve_client_profile(self):
        """GET Check: Expert can not retrieve their client profile data"""
        request = self.factory.get(f"/accounts/profiles/client/{self.client_profile.id}/")
        force_authenticate(request, user=self.expert_user)
        response = await self.expert_view(request, pk=self.client_profile.id)

        assert response.status_code == status.HTTP_404_NOT_FOUND
