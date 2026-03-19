
import pytest
import pytest_asyncio
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.views import EducationViewSet # Update import to your ViewSet
from rozumity.factories.accounts import (
    ExpertProfileFactory, EducationFactory, 
    ClientProfileFactory, UniversityFactory, SpecialityFactory
)

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestEducationAPI:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.factory = APIRequestFactory()
        
        # Create two experts to verify data isolation
        self.expert_profile = await ExpertProfileFactory.acreate(select_related=['user'])
        self.expert_user = self.expert_profile.user
        
        self.other_expert = await ExpertProfileFactory.acreate(select_related=['user'])
        self.other_user = self.other_expert.user

        # Map ViewSet actions to the corresponding async methods
        self.view_list = EducationViewSet.as_view({'get': 'alist', 'post': 'acreate'})
        self.view_detail = EducationViewSet.as_view({
            'get': 'aretrieve', 
            'put': 'aupdate', 
            'patch': 'partial_aupdate', 
            'delete': 'adestroy'
        })

    # --- CRUD & Functional Tests ---

    async def test_expert_can_create_education(self):
        """POST Check: Expert can successfully create an education record"""
        uni = await UniversityFactory.acreate()
        spec = await SpecialityFactory.acreate()
        
        payload = {
            "university": uni.id,
            "speciality": spec.id,
            "degree": 3, # Master
            "date_start": "2015-09-01",
            "date_end": "2020-06-30"
        }
        
        request = self.factory.post("/accounts/educations/", payload)
        force_authenticate(request, user=self.expert_user)
        response = await self.view_list(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Check that the expert is automatically assigned to the requester
        assert response.data["expert"] == self.expert_profile.pk

    async def test_expert_sees_only_own_education(self):
        """GET (list) Check: get_queryset filters records by the current expert user"""
        await EducationFactory.acreate(expert=self.expert_profile)
        await EducationFactory.acreate(expert=self.other_expert)

        request = self.factory.get("/accounts/educations/")
        force_authenticate(request, user=self.expert_user)
        response = await self.view_list(request)

        assert response.status_code == status.HTTP_200_OK
        # results might be in a list or paginated object
        results = response.data.get("results", response.data)
        assert len(results) == 1 

    async def test_expert_can_retrieve_own_education(self):
        """GET (retrieve) Check: Expert can view their own education detail with nested data"""
        edu = await EducationFactory.acreate(
            expert=self.expert_profile,
            select_related=['university', 'speciality']
        )
        
        request = self.factory.get(f"/accounts/educations/{edu.id}/")
        force_authenticate(request, user=self.expert_user)
        response = await self.view_detail(request, pk=edu.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == edu.id
        # Verify the custom to_representation logic (nested objects instead of IDs)
        assert isinstance(response.data["university_detail"], dict)
        assert isinstance(response.data["speciality_detail"], dict)

    async def test_expert_cannot_retrieve_others_education(self):
        """GET (retrieve) Check: Requesting another expert's record returns 404 due to get_queryset"""
        others_edu = await EducationFactory.acreate(expert=self.other_expert)

        request = self.factory.get(f"/accounts/educations/{others_edu.id}/")
        force_authenticate(request, user=self.expert_user)
        response = await self.view_detail(request, pk=others_edu.id)

        # Since get_queryset filters by user, this record is invisible to others
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_expert_can_update_own_education(self):
        """PATCH Check: Owner can successfully edit their own record"""
        edu = await EducationFactory.acreate(expert=self.expert_profile)
        
        request = self.factory.patch(f"/accounts/educations/{edu.id}/", {"degree": 5})
        force_authenticate(request, user=self.expert_user)
        response = await self.view_detail(request, pk=edu.id)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["degree"] == 5

    async def test_expert_can_delete_own_education(self):
        """DELETE Check: Owner can successfully delete their own record"""
        edu = await EducationFactory.acreate(expert=self.expert_profile)
        
        request = self.factory.delete(f"/accounts/educations/{edu.id}/")
        force_authenticate(request, user=self.expert_user)
        response = await self.view_detail(request, pk=edu.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    # --- Permissions Tests ---

    async def test_client_cannot_access_education_api(self):
        """Permissions Check: A user with a ClientProfile is blocked by IsExpert"""
        client_profile = await ClientProfileFactory.acreate(select_related=['user'])
        
        request = self.factory.get("/accounts/educations/")
        force_authenticate(request, user=client_profile.user)
        response = await self.view_list(request)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_anonymous_cannot_access_education(self):
        """Permissions Check: Unauthenticated users are blocked"""
        edu = await EducationFactory.acreate(expert=self.expert_profile)

        request = self.factory.get(f"/accounts/educations/{edu.id}/")
        response = await self.view_detail(request, pk=edu.id)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
