from adrf.generics import (
    ListAPIView, RetrieveUpdateAPIView,
    RetrieveAPIView, CreateAPIView
)
from rozumity.throttling import UserRateAsyncThrottle

from rozumity.mixins.caching_mixins import (
    CacheRUMixin, CacheListMixin, 
    CacheRetrieveMixin, CacheCreateMixin
)

from accounts.permissions import IsExpert
from educations.permissions import IsEducationOwner

from educations.models import *
from educations.serializers import *


class UniversityListView(
    CacheListMixin, ListAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class UniversityRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityListView(
    CacheListMixin, ListAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class SpecialityRetrieveView(
    CacheRetrieveMixin, RetrieveAPIView
):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class EducationCreateView(
    CacheCreateMixin, CreateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsExpert,)


class EducationRetrieveUpdateView(
    CacheRUMixin, RetrieveUpdateAPIView
):
    queryset = Education.objects.select_related(
        "university", "speciality"
    ).all()
    serializer_class = EducationReadOnlySerializer
    serializer_class_write = EducationSerializer
    throttle_classes = (UserRateAsyncThrottle,)
    permission_classes = (IsEducationOwner,)
