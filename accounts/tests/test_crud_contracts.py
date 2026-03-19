import pytest
import pytest_asyncio
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.views import TherapyContractViewSet
from rozumity.factories.accounts import (
    ExpertProfileFactory, ClientProfileFactory,
    TherapyContractFactory
)

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestTherapyContractAPI:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.factory = APIRequestFactory()
        self.expert_profile = await ExpertProfileFactory.acreate(select_related=['user'])
        self.client_profile = await ClientProfileFactory.acreate(select_related=['user'])
        self.client_user = self.client_profile.user
        self.client_user.client_profile = self.client_profile
        self.expert_user = self.expert_profile.user
        self.expert_user.expert_profile = self.expert_profile
        self.view_list = TherapyContractViewSet.as_view({
            'get': 'alist', 
            'post': 'acreate'
        })
        self.view_detail = TherapyContractViewSet.as_view({
            'get': 'aretrieve', 
            'put': 'aupdate', 
            'patch': 'partial_aupdate',
        })

    # --- CRUD & Functional Tests ---

    async def test_client_can_create_contract(self):
        """POST: Verify automatic client assignment from request context"""
        payload = {
            "invite_email": self.expert_user.email,
        }
        
        request = self.factory.post("/accounts/contracts/", payload)
        force_authenticate(request, user=self.client_user)
        
        # Async call to acreate
        response = await self.view_list(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Check that client object is returned via to_representation logic
        assert str(response.data["client_details"]["id"]) == str(self.client_profile.pk)
        assert str(response.data["expert_details"]["id"]) == str(self.expert_profile.pk)

    async def test_client_can_create_contract_no_expert(self):
        """POST: Verify automatic client assignment from request context"""
        request = self.factory.post("/accounts/contracts/", {})
        force_authenticate(request, user=self.client_user)
        
        # Async call to acreate
        response = await self.view_list(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Check that client object is returned via to_representation logic
        assert str(response.data["client_details"]["id"]) == str(self.client_profile.pk)
        assert response.data["expert_details"] is None

    async def test_expert_cannot_create_contract_no_client(self):
        """POST: Verify automatic client assignment from request context"""
        request = self.factory.post("/accounts/contracts/", {})
        force_authenticate(request, user=self.expert_user)
        
        # Async call to acreate
        response = await self.view_list(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    async def test_user_sees_only_own_contracts(self):
        """GET (list): Verify get_queryset filters by participant"""
        # Contract for current client
        await TherapyContractFactory.acreate(client=self.client_profile, expert=self.expert_profile)
        # Foreign contract
        other_client = await ClientProfileFactory.acreate()
        await TherapyContractFactory.acreate(client=other_client)

        request = self.factory.get("/accounts/contracts/")
        force_authenticate(request, user=self.client_user)
        
        # Async call to alist
        response = await self.view_list(request)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1 

    async def test_expert_can_retrieve_contract(self):
        """GET (retrieve): Verify nested representation logic"""
        contract = await TherapyContractFactory.acreate(
            client=self.client_profile, 
            expert=self.expert_profile
        )
        
        request = self.factory.get(f"/accounts/contracts/{contract.pk}/")
        force_authenticate(request, user=self.expert_user)
        
        # Async call to aretrieve
        response = await self.view_detail(request, pk=contract.pk)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data["client_details"], dict)
        assert isinstance(response.data["expert_details"], dict)

    async def test_cannot_hijack_contract_via_patch(self):
        """PATCH: Verify client/expert fields are ignored in validation for non-owners"""
        contract = await TherapyContractFactory.acreate(
            client=self.client_profile, 
            expert=self.expert_profile
        )
        random_expert = await ExpertProfileFactory.acreate()
        
        # Attempt to change expert to a different one
        payload = {"expert": random_expert.pk}
        
        request = self.factory.patch(f"/accounts/contracts/{contract.pk}/", payload)
        force_authenticate(request, user=self.client_user)
        
        # Async call to partial_aupdate
        response = await self.view_detail(request, pk=contract.pk)

        assert response.status_code == status.HTTP_200_OK
        # Days updated, but expert remained unchanged (validate popped it from attrs)
        assert str(response.data["expert_details"]["id"]) == str(self.expert_profile.pk)

    async def test_can_exit_contract_setting_null(self):
        """PATCH: Verify ability to 'exit' by setting client to null"""
        contract = await TherapyContractFactory.acreate(
            client=self.client_profile, 
            expert=self.expert_profile
        )
        
        request = self.factory.patch(
            f"/accounts/contracts/{contract.pk}/", 
            {"client": None}, 
            format="json"
        )
        force_authenticate(request, user=self.client_user)
        
        response = await self.view_detail(request, pk=contract.pk)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["client_details"] is None

    async def test_destroy_is_blocked(self):
        """DELETE Check: Verify http_method_names constraint"""
        contract = await TherapyContractFactory.acreate(client=self.client_profile)
        
        request = self.factory.delete(f"/accounts/contracts/{contract.pk}/")
        force_authenticate(request, user=self.client_user)
        
        # Even if adestroy is defined, http_method_names returns 405
        response = await self.view_detail(request, pk=contract.pk)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # --- Permissions ---

    async def test_unauthorized_access_forbidden(self):
        """Permissions Check: Unauthorized user receives 404"""
        contract = await TherapyContractFactory.acreate(expert=self.expert_profile)
        stranger = await ClientProfileFactory.acreate(select_related=['user'])

        request = self.factory.get(f"/accounts/contracts/{contract.pk}/")
        force_authenticate(request, user=stranger.user)
        
        response = await self.view_detail(request, pk=contract.pk)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_client_activation_invalidates_expert_cache(self):
        """
        Cache Invalidation Check: Verify that the expert sees updates made by the client 
        in subsequent requests.
        """
        # 1. Create a contract with is_active set to False
        contract = await TherapyContractFactory.acreate(
            client=self.client_profile, 
            expert=self.expert_profile,
            is_active=False
        )
        
        # 2. Expert makes the first request (data should be cached now)
        request_get = self.factory.get(f"/accounts/contracts/{contract.pk}/")
        force_authenticate(request_get, user=self.expert_user)
        
        response_1 = await self.view_detail(request_get, pk=contract.pk)
        assert response_1.status_code == status.HTTP_200_OK
        assert response_1.data["is_active"] is False
        
        # 3. Client activates the contract
        payload = {"is_active": True}
        request_patch = self.factory.patch(
            f"/accounts/contracts/{contract.pk}/", 
            payload, 
            format="json"
        )
        force_authenticate(request_patch, user=self.client_user)
        
        patch_response = await self.view_detail(request_patch, pk=contract.pk)
        assert patch_response.status_code == status.HTTP_200_OK
        
        # 4. Expert makes a second request
        # If the cache is NOT invalidated, the expert will receive the stale response (is_active=False)
        request_get_2 = self.factory.get(f"/accounts/contracts/{contract.pk}/")
        force_authenticate(request_get_2, user=self.expert_user)
        
        response_2 = await self.view_detail(request_get_2, pk=contract.pk)
        
        # 5. KEY ASSERTION
        assert response_2.status_code == status.HTTP_200_OK
        assert response_2.data["is_active"] is True, "Cache invalidation failed: expert sees stale status."
