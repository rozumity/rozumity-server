from drf_spectacular.utils import extend_schema, extend_schema_view

from rozumity.throttling import ThrottleRateLogged

from rozumity.mixins.caching_mixins.viewsets import ReadOnlyModelViewSetCached
from rozumity.mixins.caching_mixins.generics import RetrieveUpdateAPIView, CreateAPIView

from rozumity.permissions import IsAdmin, IsUser

from .models import *
from .serializers import *


@extend_schema_view(
    list=extend_schema(
        summary="Get list of users",
    ),
    retrieve=extend_schema(
        summary="Get user details",
    ),
)
class UserViewSet(ReadOnlyModelViewSetCached):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve one client profile by ID",
        description="Permissions: owner, admin",
        methods=["GET"]
    ),
    put=extend_schema(
        summary="Update one client profile by ID",
        description="Permissions: owner, admin"
    ),
    patch=extend_schema(
        summary="Partial update one client profile by ID",
        description="Permissions: owner, admin"
    ),
)
class RetrieveUpdateClientProfileView(RetrieveUpdateAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (ThrottleRateLogged,)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Retrieve one expert profile by ID",
        description="Permissions: owner, admin"
    ),
    update=extend_schema(
        summary="Update one expert profile by ID",
        description="Permissions: owner, admin"
    ),
)
class RetrieveUpdateExpertProfileView(RetrieveUpdateAPIView):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    
    def get_serializer_class(self):
        if self.request.method.lower() != 'get':
            return ExpertProfileSerializer
        return ExpertProfileSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of all subscription plans",
        description="Permissions: auth"
    ),
    retrieve=extend_schema(
        summary="Retrieve a single subscription plan by its ID",
        description="Permissions: auth"
    ),
)
class SubscriptionPlanViewSet(ReadOnlyModelViewSetCached):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)


@extend_schema_view(
    create=extend_schema(
        summary="Create new therapy contract",
        description="Permissions: auth"
    ),
    retrieve=extend_schema(
        summary="Retrieve therapy contract by the ID",
        description="Permissions: owner, admin"
    ),
    update=extend_schema(
        summary="Update therapy contract by the ID",
        description="Permissions: owner, admin"
    )
)
class RetrieveUpdateTherapyContractView(RetrieveUpdateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)


@extend_schema_view(
    create=extend_schema(
        summary="Create new therapy contract",
        description="Permissions: auth"
    )
)
class CreateTherapyContractView(CreateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)
