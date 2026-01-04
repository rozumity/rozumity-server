from rozumity.throttling import ThrottleRateLogged

from rozumity.mixins.caching_mixins.viewsets import (
    ModelViewSetCached, ReadOnlyModelViewSetCached
)

from accounts.permissions import IsExpert

from educations.models import *
from educations.serializers import *


class UniversityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    """
    Universities Read Only API.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)


class SpecialityReadOnlyViewSet(ReadOnlyModelViewSetCached):
    """
    Specialities Read Only API.
    """
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)


class EducationViewSet(ModelViewSetCached):
    """
    Education Read and Write API.
    Only accessible to users with expert permissions.
    """
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (ThrottleRateLogged,)
    permission_classes = (IsExpert,)

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return EducationReadOnlySerializer
        return EducationSerializer
