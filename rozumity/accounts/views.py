from adrf.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)

from rozumity.mixins.caching_mixins import (
    CacheRDMixin, CacheRUDMixin, CacheRUMixin, 
    CacheLCMixin, CacheListMixin, 
)
from rozumity.permissions import StaffReadWritePermission

from .models import *
from .serializers import *


class UserListView(
    CacheListMixin, ListAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (StaffReadWritePermission,)


class UserRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (StaffReadWritePermission,)


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


class TherapyContractListCreateView(
    CacheLCMixin, ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", 
        "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer


class TherapyContractRetrieveUpdateDestroyView(
    CacheRUDMixin, RetrieveUpdateDestroyAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", 
        "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer


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
