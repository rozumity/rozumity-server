from rest_framework.permissions import IsAdminUser
from adrf.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rozumity.paginations import LimitOffsetPagination
from rozumity.permissions import AuthReadStaffWritePermission
from rozumity.mixins import (
    AsyncCacheListCreateMixin, 
    AsyncCacheRetrieveUpdateDestroyMixin
)

from .models import *
from .serializers import *


class UserListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = LimitOffsetPagination


class UserRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UniversityListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class UniversityRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (AuthReadStaffWritePermission,)


class SpecialityListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class SpecialityRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = (AuthReadStaffWritePermission,)


class EducationListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = Education.objects.select_related("university", "speciality").all()
    serializer_class = EducationSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class EducationRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = Education.objects.select_related("university", "speciality").all()
    serializer_class = EducationSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class ClientProfileListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class ClientProfileRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class ExpertProfileListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class ExpertProfileRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = ExpertProfile.objects.prefetch_related("education").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class SubscriptionPlanListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class SubscriptionPlanRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class TherapyContractListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class TherapyContractRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class DiaryListCreateView(
    AsyncCacheListCreateMixin, 
    ListCreateAPIView
):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class DiaryRetrieveUpdateDestroyView(
    AsyncCacheRetrieveUpdateDestroyMixin, 
    RetrieveUpdateDestroyAPIView
):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = DiarySerializer
    permission_classes = (AuthReadStaffWritePermission,)
