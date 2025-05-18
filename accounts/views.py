from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, 
    RetrieveAPIView, CreateAPIView
)
from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.serialization_mixins import ReadWriteDiffMixin
from rozumity.mixins.caching_mixins import (
    CacheRUDMixin, CacheRUMixin, CacheLCMixin, 
    CacheListMixin, CacheRetrieveMixin, CacheCreateMixin
)

from rozumity.permissions import *
from accounts.permissions import (
    IsContractSigner, IsProfileOwner
)

from .models import *
from .serializers import *


class UserListView(
    CacheListMixin, ListAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


class UserRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


class ClientProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsProfileOwner,)


class ExpertProfileRetrieveUpdateView(
    CacheRUMixin, ReadWriteDiffMixin, RetrieveUpdateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    permission_classes = (IsProfileOwner,)
    throttle_classes = (UserRateAsyncThrottle,)
    serializer_class = (
        ExpertProfileReadOnlySerializer, 
        ExpertProfileSerializer
    )


class SubscriptionPlanListView(
    CacheListMixin, ListAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsUser,)


class SubscriptionPlanRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsUser,)


class TherapyContractCreateView(
    CacheCreateMixin, CreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsUser,)


class TherapyContractRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsContractSigner,)


class DiaryListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = TherapyContractSerializer


class DiaryRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = DiarySerializer
