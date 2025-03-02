from rest_framework.authentication import SessionAuthentication
from adrf.generics import ListCreateAPIView

from rozumity.paginations import LimitOffsetAsyncPagination
from rozumity.permissions import AuthReadStaffWritePermission

from .models import University, Speciality
from .serializers import UniversitySerializer, SpecialitySerializer


class UniversityListCreateView(ListCreateAPIView):
    queryset = University.objects.prefetch_related('country').all()
    serializer_class = UniversitySerializer
    permission_classes=[AuthReadStaffWritePermission]
    authentication_classes = [SessionAuthentication]
    pagination_class = LimitOffsetAsyncPagination


class SpecialityListCreateView(ListCreateAPIView):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    permission_classes=[AuthReadStaffWritePermission]
    authentication_classes = [SessionAuthentication]
    pagination_class = LimitOffsetAsyncPagination
