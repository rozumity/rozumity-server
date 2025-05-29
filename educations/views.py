from adrf.generics import (
    ListAPIView, RetrieveUpdateAPIView,
    RetrieveAPIView, ListCreateAPIView
)
from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.caching_mixins import (
    ReadUpdateMixin, ListMixin, 
    RetrieveMixin, ListCreateMixin
)
from rozumity.mixins.filtering_mixins import OwnedList

from accounts.permissions import IsExpert
from educations.permissions import IsEducationOwner

from educations.models import *
from educations.serializers import *


class UniversityListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all universities.
    Only accessible to users with expert permissions.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class UniversityRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a single university by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityListView(
    ListMixin, ListAPIView
):
    """
    API view to retrieve a list of all specialities.
    Only accessible to users with expert permissions.
    """
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityRetrieveView(
    RetrieveMixin, RetrieveAPIView
):
    """
    API view to retrieve a list of all specialities.
    Only accessible to users with expert permissions.
    """
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class EducationListCreateView(
    OwnedList, ListCreateMixin, ListCreateAPIView
):
    """
    API view to retrieve a list of all specialities.
    Only accessible to users with expert permissions.
    """
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return EducationReadOnlySerializer
        return EducationSerializer


class EducationRetrieveUpdateView(
    ReadUpdateMixin, RetrieveUpdateAPIView
):
    """
    API view to retrieve a list of all specialities.
    Only accessible to users with expert permissions.
    Uses ownership check.
    """
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsEducationOwner,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return EducationReadOnlySerializer
        return EducationSerializer