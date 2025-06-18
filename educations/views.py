from adrf.generics import (
    ListAPIView, RetrieveUpdateAPIView,
    RetrieveAPIView, ListCreateAPIView
)
from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.caching_mixins import (
    ReadUpdateMixin, ListModelMixin, 
    RetrieveMixin, ListCreateMixin,
    ReadOnlyModelViewSet, CachedModelViewSet
)
from rozumity.mixins.filtering_mixins import Owned

from accounts.permissions import IsExpert
from educations.permissions import IsEducationOwner

from educations.models import *
from educations.serializers import *


class UniversityReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all universities.
    API view to retrieve a single university by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityReadOnlyViewSet(ReadOnlyModelViewSet):
    """
    API view to retrieve a list of all specialities.
    API view to retrieve a single speciality by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class EducationViewSet(Owned, CachedModelViewSet):
    """
    API view to retrieve a list of all educations or create one.
    API view to retrieve or update a single education by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    throttle_classes = (UserRateAsyncThrottle,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return EducationReadOnlySerializer
        return EducationSerializer
