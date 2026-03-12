from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rozumity.throttling import ThrottleRateLogged
from adrf_caching.viewsets import ReadOnlyModelViewSetCached, ModelViewSetCached
from adrf_caching.generics import (
    RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
)
from adrf_caching.mixins import CacheInvalidationMixin
from rozumity.permissions import (
    IsAuthenticatedAsync, IsAdminUserAsync, IsOwner, IsExpert
)
from .permissions import IsProfileOwner
from .models import *
from .serializers import *


class UserViewSet(ReadOnlyModelViewSetCached):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUserAsync,)

    @extend_schema(summary="Get list of users")
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(summary="Get user details")
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)


class RetrieveUpdateClientProfileView(RetrieveUpdateAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsProfileOwner,)

    @extend_schema(
        summary="Retrieve one client profile by ID",
        description="Permissions: owner, admin"
    )
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update one client profile by ID",
        description="Permissions: owner, admin"
    )
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update one client profile by ID",
        description="Permissions: owner, admin"
    )
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)


class RetrieveUpdateExpertProfileView(RetrieveUpdateAPIView):
    queryset = ExpertProfile.objects.prefetch_related("educations").all()
    serializer_class = ExpertProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsProfileOwner,)

    @extend_schema(
        summary="Retrieve expert profile",
        description="Permissions: owner, admin"
    )
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update expert profile",
        description="Permissions: owner, admin"
    )
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update expert profile",
        description="Permissions: owner, admin"
    )
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)


class SubscriptionPlanViewSet(ReadOnlyModelViewSetCached):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsAuthenticatedAsync,)

    @extend_schema(
        summary="Retrieve a list of all subscription plans",
        description="Permissions: auth"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single subscription plan by its ID",
        description="Permissions: auth"
    )
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)


class RetrieveUpdateTherapyContractView(CacheInvalidationMixin, RetrieveUpdateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsOwner,)
    invalidate_fields = ("expert_id","client_id")

    @extend_schema(
        summary="Retrieve therapy contract by the ID",
        description="Permissions: owner, admin"
    )
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update therapy contract by the ID",
        description="Permissions: owner, admin"
    )
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update therapy contract by the ID",
        description="Permissions: owner, admin"
    )
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)


class ListCreateTherapyContractView(ListCreateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsAuthenticatedAsync,)

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(
            Q(client_id=user.id) | Q(expert_id=user.id)
        )

    @extend_schema(
        summary="List therapy contracts for current user",
        description="Returns contracts where current user is either client or expert."
    )
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create new therapy contract",
        description="Permissions: auth"
    )
    async def post(self, request, *args, **kwargs):
        return await super().post(request, *args, **kwargs)


class UniversityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)
    
    @extend_schema(
        summary="Retrieve a list of all universities",
        description="Permissions: user is expert"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single university by its ID",
        description="Permissions: user is expert"
    )
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)


class SpecialityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsAuthenticatedAsync,)
    permission_classes = (IsExpert,)
    
    @extend_schema(
        summary="Retrieve a list of all specialities",
        description="Permissions: user is expert"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single speciality by its ID",
        description="Permissions: user is expert"
    )
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)


class EducationRetrieveUpdateDestroyView(CacheInvalidationMixin, RetrieveUpdateDestroyAPIView):
    queryset = Education.objects.select_related(
        "university", "speciality", "expert"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsOwner,)
    invalidate_fields = ("expert_id",)

    @extend_schema(summary="Retrieve education", description="Permissions: owner, admin")
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(summary="Update education", description="Permissions: owner, admin")
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(summary="Partial update education", description="Permissions: owner, admin")
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)

    @extend_schema(summary="Delete education", description="Permissions: owner, admin")
    async def delete(self, request, *args, **kwargs):
        return await super().delete(request, *args, **kwargs)


class EducationListCreateView(ListCreateAPIView):
    queryset = Education.objects.select_related("university", "speciality", "expert").all()
    serializer_class = EducationSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(expert_id=user.id)

    @extend_schema(summary="Create education", description="Permissions: user is expert")
    async def post(self, request, *args, **kwargs):
        return await super().post(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a list of user's educations",
        description="Permissions: user is expert"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)
