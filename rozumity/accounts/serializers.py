from adrf.serializers import ModelSerializer
from .models import User, ClientProfile, ExpertProfile, University, Speciality, Education

# --- Education

class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = Speciality
        fields = ('title', 'code')


class UniversitySerializer(ModelSerializer):
    class Meta:
        model = University
        fields = ('name', 'country')


class EducationSerializer(ModelSerializer):
    university = UniversitySerializer()
    speciality = SpecialitySerializer()
    class Meta:
        model = Education
        fields = ('university', 'degree', 'speciality', 'date_start', 'date_end')

# Education ---
# --- Profile

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "is_staff", "is_client", "is_expert", "is_active", "date_joined")
        read_only_fields = fields.copy()


class ClientProfileSerializer(ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = ClientProfile
        fields = ('first_name', 'last_name', 'gender', 'country', 'date_birth', 'user')
        read_only_fields = ('date_birth', 'user')


class ExpertProfileSerializer(ModelSerializer):
    user = UserSerializer()
    education = EducationSerializer(many=True)
    
    class Meta:
        model = ExpertProfile
        fields = ('first_name', 'last_name', 'gender', 'country', 'date_birth', 'user', 'education', 'education_extra', 'countries_allowed')
        read_only_fields = ('date_birth', 'user')

# --- Profile
