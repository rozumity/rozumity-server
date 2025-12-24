
from adrf.serializers import ModelSerializer
from rest_framework.serializers import (
    CharField, PrimaryKeyRelatedField
)

from django_countries.serializer_fields import CountryField

from rozumity.mixins.serialization_mixins import (
    CountryFieldMixin, ReadOnlySerializerMixin
)

from educations.models import *

# --- Education

class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'


class UniversitySerializer(CountryFieldMixin, ModelSerializer):
    country = CountryField()

    class Meta:
        model = University
        fields = '__all__'


class EducationSerializer(ModelSerializer):
    university = PrimaryKeyRelatedField(queryset=University.objects.all(), required=False)
    speciality = PrimaryKeyRelatedField(queryset=Speciality.objects.all(), required=False)

    class Meta:
        model = Education
        fields = "__all__"


class EducationReadOnlySerializer(ReadOnlySerializerMixin, EducationSerializer):
    university = UniversitySerializer()
    speciality = SpecialitySerializer()
    degree_display = CharField(source='get_degree_display', read_only=True)

    class Meta:
        model = Education
        fields = '__all__'
