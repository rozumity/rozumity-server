from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import IsAdminUser
from rozumity.throttling import (
    UserRateAsyncThrottle, AnonRateAsyncThrottle
)

from rozumity.mixins.caching_mixins import (
    CacheRUDMixin, CacheRUMixin, 
    CacheLCMixin, CacheListMixin
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


class UserRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


class UniversityListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsAdminCreateUserList,)


class UniversityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsAdminUpdateDeleteUserRead,)


class SpecialityListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsAdminCreateUserList,)


class SpecialityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class EducationListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class EducationRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class ClientProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (IsAdmin,)


class ClientProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (IsAdminUser|IsProfileOwner,)


class ExpertProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (IsAdmin,)


class ExpertProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (IsAdminUser|IsProfileOwner,)


class SubscriptionPlanListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class SubscriptionPlanRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class TherapyContractCreateListView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsAdminListUserCreate,)


class TherapyContractRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsAdminUser|IsContractSigner,)


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
