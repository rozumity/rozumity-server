from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.views_mixins import (
    AsyncModelViewSet, AsyncReadOnlyModelViewSet, Owned
)

from accounts.permissions import IsExpert

from educations.models import *
from educations.serializers import *


class UniversityReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    """
    API view to retrieve a list of all universities.
    API view to retrieve a single university by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityReadOnlyViewSet(AsyncReadOnlyModelViewSet):
    """
    API view to retrieve a list of all specialities.
    API view to retrieve a single speciality by its ID.
    Only accessible to users with expert permissions.
    """
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class EducationViewSet(Owned, AsyncModelViewSet):
    """
    API view to retrieve a list of all educations or create one.
    API view to retrieve or update a single education by its ID.
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
