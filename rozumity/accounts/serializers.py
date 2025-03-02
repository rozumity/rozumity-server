from adrf.serializers import ModelSerializer
from .models import User, ClientProfile, ExpertProfile, University, Speciality


class UniversitySerializer(ModelSerializer):
    class Meta:
        model = University
        fields = ('name', 'country')


class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = Speciality
        fields = ('title', 'code')
