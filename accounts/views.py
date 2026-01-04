from rozumity.throttling import ThrottleRateLogged

from rozumity.mixins.caching_mixins import (
    RetrieveModelMixin, UpdateModelMixin, GenericViewSet,
    CachedModelReadOnlyViewSet, CachedModelViewSet,
)

from rozumity.permissions import AsyncJWTAuthentication, IsAdmin, IsUser

from .models import *
from .serializers import *


class UserReadOnlyViewSet(CachedModelReadOnlyViewSet):
    """
    Retrieve users. Only accessible to admin users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    authentication_classes = (AsyncJWTAuthentication,)


class ClientProfileViewSet(
    UpdateModelMixin, RetrieveModelMixin, GenericViewSet
):
    """
    Retrieve or update a client profile by user ID.
    Only accessible to the profile owner for updates, and to authenticated users for read access.
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    authentication_classes = (AsyncJWTAuthentication,)


class ExpertProfileViewSet(CachedModelViewSet):
    """
    Base Base for all client profile views
    """
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    authentication_classes = (AsyncJWTAuthentication,)
    
    def get_serializer_class(self):
        if self.request.method.lower() != 'get':
            return ExpertProfileSerializer
        return ExpertProfileSerializer


class SubscriptionPlanReadOnlyViewSet(CachedModelReadOnlyViewSet):
    """
    API view to retrieve a list of all subscription plans or 
    to retrieve a single subscription plan by its ID.
    Only accessible to authenticated users.
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)
    authentication_classes = (AsyncJWTAuthentication,)


class TherapyContractViewSet(CachedModelViewSet):
    """
    API view to create a new therapy contract or
    to retrieve & update a therapy contract by its ID.
    Only accessible to users who are signers of the contract.
    """
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsUser,)
    authentication_classes = (AsyncJWTAuthentication,)
