from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView, 
    RetrieveAPIView, UpdateAPIView
)
from rest_framework.permissions import IsAdminUser
from rozumity.throttling import (
    UserRateAsyncThrottle, AnonRateAsyncThrottle
)

from rozumity.mixins.serialization_mixins import ReadWriteDiffMixin
from rozumity.mixins.caching_mixins import (
    CacheRUDMixin, CacheRUMixin, CacheLCMixin, 
    CacheListMixin, CacheRetrieveMixin,
)

from rozumity.permissions import *
from accounts.permissions import (
    IsContractSigner, IsProfileOwner, IsExpert,
    IsEducationOwner, IsAdminListCreateExpertCreate
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


class UniversityListView(
    CacheListMixin, ListAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsExpert,)


class UniversityRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsExpert,)


class SpecialityListView(
    CacheListMixin, ListAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsExpert,)


class SpecialityRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsExpert,)


class EducationListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsAdminListCreateExpertCreate,)


class EducationRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsEducationOwner,)


class ClientProfileRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (IsProfileOwner,)


class ExpertProfileRetrieveUpdateView(
    CacheRUMixin, ReadWriteDiffMixin, RetrieveUpdateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    permission_classes = (IsProfileOwner,)
    serializer_class = (
        ExpertProfileReadSerializer, 
        ExpertProfileWriteSerializer
    )


class SubscriptionPlanListView(
    CacheListMixin, ListAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class SubscriptionPlanRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    throttle_classes = (AnonRateAsyncThrottle, UserRateAsyncThrottle)
    permission_classes = (IsUser,)


class TherapyContractCreateListView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsAdminListUserCreate,)


class TherapyContractRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "client_plan", "expert_plan"
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
