from rozumity.throttling import ThrottleRateLogged

from rozumity.mixins.caching_mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, 
    UpdateModelMixin, DestroyModelMixin
)

from rozumity.permissions import AsyncJWTAuthentication, IsAdmin

from .models import *
from .serializers import *


class UserBase:
    """
    Base Base for all user views
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    authentication_classes = (AsyncJWTAuthentication,)


class ProfileClientBase:
    """
    Base Base for all client profile views
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (ThrottleRateLogged,)
    authentication_classes = (AsyncJWTAuthentication,)

class ProfileExpertBase:
    """
    Base Base for all client profile views
    """
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileReadOnlySerializer
    throttle_classes = (ThrottleRateLogged,)
    authentication_classes = (AsyncJWTAuthentication,)
    
    def get_serializer_class(self):
        if self.request.method.lower() != 'get':
            return ExpertProfileSerializer
        return ExpertProfileReadOnlySerializer


class UserList(ListModelMixin, UserBase):
    """
    List users API view
    Only accessible to admin users
    """
    pass


class UserRetrieve(RetrieveModelMixin, UserBase):
    """
    Retrieve user API view
    Only accessible to admin users
    """
    pass


class ClientProfileRetrieve(RetrieveModelMixin, ProfileClientBase):
    """
    Retrieve client profile API view
    Only accessible to owners
    """
    pass


class ClientProfileUpdate(UpdateModelMixin, ProfileClientBase):
    """
    Update client profile API view
    Only accessible to owners
    """
    pass


class ExpertProfileViewSet(CachedModelViewSet):
    """
    API view to retrieve or update an expert profile.
    Only accessible to the profile owner for updates, and to authenticated users for read access.
    """
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileReadOnlySerializer
    permission_classes = (IsProfileOwnerWriteAuthRead,)
    throttle_classes = (ThrottleRateLogged,)
    authentication_classes = (AsyncJWTAuthentication,)
    
    def get_serializer_class(self):
        if self.request.method.lower() != 'get':
            return ExpertProfileSerializer
        return ExpertProfileReadOnlySerializer


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
