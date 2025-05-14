from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rozumity.throttling import UserRateAsyncThrottle, AnonRateAsyncThrottle

from rozumity.mixins.caching_mixins import (
    CacheRUDMixin, CacheRUMixin, 
    CacheLCMixin, CacheListMixin
)
from rozumity.permissions import *
from accounts.permissions import (
    IsContractSignerPermission, IsProfileOwnerPermission, IsStaffReadPermission
)

from .models import *
from .serializers import *


class UserListView(
    CacheListMixin, ListAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsStaffPermission,)


class UserRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsStaffPermission,)


class UniversityListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class UniversityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class SpecialityListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class SpecialityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class EducationListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class EducationRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class ClientProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (IsStaffPermission,)


class ClientProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (IsStaffPermission|IsProfileOwnerPermission,)


class ExpertProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (IsStaffPermission,)


class ExpertProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (IsStaffPermission|IsProfileOwnerPermission,)


class SubscriptionPlanListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class SubscriptionPlanRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)


class TherapyContractCreateListView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_subscription_id", 
        "expert_subscription_id"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsStaffReadPermission|IsUserWritePermission,)


class TherapyContractRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_subscription_id", 
        "expert_subscription_id"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsStaffPermission|IsContractSignerPermission,)


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
