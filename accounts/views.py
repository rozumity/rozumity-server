from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.views_mixins import (
    AsyncModelViewSet, AsyncReadOnlyModelViewSet, Owned
)

from rozumity.permissions import *
from accounts.permissions import IsProfileOwnerWriteAuthRead


from .models import *
from .serializers import *


class UserReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    """
    API view to retrieve a list of all users.
    Only accessible to admin users.
    API view to retrieve a single user by their ID.
    Only accessible to admin users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


class ClientProfileViewSet(Owned, AsyncModelViewSet):
    """
    API view to retrieve or update a client profile.
    Only accessible to the profile owner for updates, and to authenticated users for read access.
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsProfileOwnerWriteAuthRead,)


class ExpertProfileViewSet(Owned, AsyncModelViewSet):
    """
    API view to retrieve or update an expert profile.
    Only accessible to the profile owner for updates, and to authenticated users for read access.
    """
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    permission_classes = (IsProfileOwnerWriteAuthRead,)
    throttle_classes = (UserRateAsyncThrottle,)
    serializer_class = ExpertProfileReadOnlySerializer
    
    def get_serializer_class(self):
        if self.request.method.lower() != 'get':
            return ExpertProfileSerializer
        return ExpertProfileReadOnlySerializer


class SubscriptionPlanReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    """
    API view to retrieve a list of all subscription plans or 
    to retrieve a single subscription plan by its ID.
    Only accessible to authenticated users.
    """
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsUser,)


class TherapyContractViewSet(Owned, AsyncModelViewSet):
    """
    API view to create a new therapy contract or
    to retrieve & update a therapy contract by its ID.
    Only accessible to users who are signers of the contract.
    """
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsUser,)
