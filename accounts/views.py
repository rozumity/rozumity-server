from drf_spectacular.utils import extend_schema
from rozumity.throttling import ThrottleRateLogged
from adrf_caching.viewsets import ReadOnlyModelViewSetCached
from adrf_caching.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rozumity.permissions import IsAdmin, IsUser
from .permissions import IsExpert
from .models import *
from .serializers import *

class UserViewSet(ReadOnlyModelViewSetCached):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    @extend_schema(summary="Get list of users")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Get user details")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class RetrieveUpdateClientProfileView(RetrieveUpdateAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (ThrottleRateLogged,)

    @extend_schema(summary="Retrieve one client profile by ID", description="Permissions: owner, admin")
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(summary="Update one client profile by ID", description="Permissions: owner, admin")
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(summary="Partial update one client profile by ID", description="Permissions: owner, admin")
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)


class RetrieveUpdateExpertProfileView(RetrieveUpdateAPIView):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    throttle_classes = (ThrottleRateLogged,)

    @extend_schema(summary="Retrieve one expert profile by ID", description="Permissions: owner, admin")
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(summary="Update one expert profile by ID", description="Permissions: owner, admin")
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(summary="Partial update one expert profile by ID", description="Permissions: owner, admin")
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)
    permission_classes = (IsExpert,)


class SubscriptionPlanViewSet(ReadOnlyModelViewSetCached):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)

    @extend_schema(summary="Retrieve a list of all subscription plans", description="Permissions: auth")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary="Retrieve a single subscription plan by its ID", description="Permissions: auth")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class RetrieveUpdateTherapyContractView(RetrieveUpdateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)

    @extend_schema(summary="Retrieve therapy contract by the ID", description="Permissions: owner, admin")
    async def get(self, request, *args, **kwargs):
        return await super().get(request, *args, **kwargs)

    @extend_schema(summary="Update therapy contract by the ID", description="Permissions: owner, admin")
    async def put(self, request, *args, **kwargs):
        return await super().put(request, *args, **kwargs)

    @extend_schema(summary="Partial update therapy contract by the ID", description="Permissions: owner, admin")
    async def patch(self, request, *args, **kwargs):
        return await super().patch(request, *args, **kwargs)


class CreateTherapyContractView(CreateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)

    @extend_schema(summary="Create new therapy contract", description="Permissions: auth")
    async def post(self, request, *args, **kwargs):
        return await super().post(request, *args, **kwargs)

class UniversityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)


class SpecialityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)

class EducationRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)
