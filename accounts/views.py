from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rozumity.throttling import ThrottleRateLogged
from adrf_caching.viewsets import ReadOnlyModelViewSetCached, ModelViewSetCached
from adrf_caching.generics import RetrieveUpdateAPIView
from rozumity.permissions import (
    IsAuthenticatedAsync, IsOwner, IsExpert
)
from .permissions import IsProfileOwner
from .models import *
from .serializers import *


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
    permission_classes = (IsProfileOwner,)
    throttle_classes = (ThrottleRateLogged,)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedAsync()]
        return [IsProfileOwner()]

    @extend_schema(summary="Retrieve expert profile", description="Permissions: owner, admin")
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(summary="Update expert profile", description="Permissions: owner, admin")
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(summary="Partial update expert profile", description="Permissions: owner, admin")
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


class TherapyContractViewSet(ModelViewSetCached):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    queryset = TherapyContract.objects.select_related(
        "client", "expert"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsOwner,)

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(
            Q(client_id=user.id) | Q(expert_id=user.id)
        )

    @extend_schema(
        summary="Retrieve a list of all user's therapy contracts",
        description="Permissions: owners"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve therapy contract by the ID",
        description="Permissions: owners"
    )
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new therapy contract",
        description="Permissions: client, expert"
    )
    async def acreate(self, request, *args, **kwargs):
        return await super().acreate(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update therapy contract by the ID",
        description="Permissions: owners"
    )
    async def partial_aupdate(self, request, *args, **kwargs):
        return await super().partial_aupdate(request, *args, **kwargs)


class UniversityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)
    
    @extend_schema(
        summary="Retrieve a list of all universities",
        description="Permissions: expert"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single university by its ID",
        description="Permissions: expert"
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
        description="Permissions: expert"
    )
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a single speciality by its ID",
        description="Permissions: expert"
    )
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)


class EducationViewSet(ModelViewSetCached):
    queryset = Education.objects.select_related(
        "university", "speciality", "expert"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsOwner, IsExpert)

    def get_queryset(self):
        user_id = self.request.user.id
        return Education.objects.filter(
            expert__user_id=user_id
        ).select_related('university', 'speciality')

    @extend_schema(summary="List educations", description="Permissions: expert")
    async def alist(self, request, *args, **kwargs):
        return await super().alist(request, *args, **kwargs)

    @extend_schema(summary="Retrieve education", description="Permissions: expert owner")
    async def aretrieve(self, request, *args, **kwargs):
        return await super().aretrieve(request, *args, **kwargs)

    @extend_schema(summary="Create own education", description="Permissions: expert")
    async def acreate(self, request, *args, **kwargs):
        return await super().acreate(request, *args, **kwargs)

    @extend_schema(summary="Update education", description="Permissions: expert owner")
    async def aupdate(self, request, *args, **kwargs):
        return await super().aupdate(request, *args, **kwargs)

    @extend_schema(summary="Partial update education", description="Permissions: expert owner")
    async def partial_aupdate(self, request, *args, **kwargs):
        return await super().partial_aupdate(request, *args, **kwargs)
    
    @extend_schema(summary="Delete education", description="Permissions: expert owner")
    async def adestroy(self, request, *args, **kwargs):
        return await super().adestroy(request, *args, **kwargs)
