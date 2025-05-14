from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)

from rozumity.mixins.caching_mixins import (
    CacheRDMixin, CacheRUDMixin, CacheRUMixin, 
    CacheLCMixin, CacheListMixin, CacheCreateMixin
)
from rozumity.permissions import *
from accounts.permissions import IsContractSigner

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


class UniversityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer


class SpecialityListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer


class SpecialityRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer


class EducationListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer


class EducationRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer


class ClientProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer


class ClientProfileRetrieveUpdateView(
    CacheRDMixin, RetrieveUpdateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer


class ExpertProfileListView(
    CacheListMixin, ListAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer


class ExpertProfileRetrieveUpdateView(
    CacheRUDMixin, RetrieveUpdateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer


class SubscriptionPlanListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class SubscriptionPlanRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class TherapyContractListView(
    CacheListMixin, ListAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_subscription_id", 
        "expert_subscription_id"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsStaffPermission,)


class TherapyContractCreateView(
    CacheCreateMixin, ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_subscription_id", 
        "expert_subscription_id"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsUserWritePermission,)


class TherapyContractRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client_email", "expert_email", "client_subscription_id", 
        "expert_subscription_id"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (IsStaffPermission|IsContractSigner,)


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
