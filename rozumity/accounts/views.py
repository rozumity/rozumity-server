from rest_framework.permissions import IsAdminUser
#from rest_framework.authentication import SessionAuthentication
from adrf.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rozumity.paginations import LimitOffsetPagination
from rozumity.permissions import AuthReadStaffWritePermission

from .models import *
from .serializers import *


class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = LimitOffsetPagination


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UniversityListCreateView(ListCreateAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class UniversityRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (AuthReadStaffWritePermission,)


class SpecialityListCreateView(ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class SpecialityRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes = (AuthReadStaffWritePermission,)


class EducationListCreateView(ListCreateAPIView):
    queryset = Education.objects.select_related("university", "speciality").all()
    serializer_class = EducationSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class EducationRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Education.objects.select_related("university", "speciality").all()
    serializer_class = EducationSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class ClientProfileListCreateView(ListCreateAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class ClientProfileRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class ExpertProfileListCreateView(ListCreateAPIView):
    queryset = ExpertProfile.objects.prefetch_related("education", "countries_allowed").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class ExpertProfileRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ExpertProfile.objects.prefetch_related("education", "countries_allowed").all()
    serializer_class = ExpertProfileSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class SubscriptionPlanListCreateView(ListCreateAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class SubscriptionPlanRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class TherapyContractListCreateView(ListCreateAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class TherapyContractRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = TherapyContract.objects.select_related(
        "client", "expert", "subscriptionClient", "subscriptionExpert"
    ).all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)


class DiaryListCreateView(ListCreateAPIView):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = TherapyContractSerializer
    permission_classes = (AuthReadStaffWritePermission,)
    pagination_class = LimitOffsetPagination


class DiaryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Diary.objects.select_related("client").all()
    serializer_class = DiarySerializer
    permission_classes = (AuthReadStaffWritePermission,)
