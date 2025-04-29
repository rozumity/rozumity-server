from adrf.serializers import ModelSerializer
from rest_framework.serializers import HyperlinkedIdentityField, EmailField
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin

from .models import *


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
    university = UniversitySerializer()
    speciality = SpecialitySerializer()

    class Meta:
        model = Education
        fields = "__all__"
        read_only_fields = ('university', "speciality")

# Education ---
# --- Profile

class UserSerializer(ModelSerializer):
    id = EmailField(source='email')
    
    class Meta:
        model = User
        fields = ["id", "email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields.copy()


class ProfileSerializerBase(CountryFieldMixin, ModelSerializer):
    country = CountryField()
    
    async def ato_representation(self, instance):
        representation = await super().ato_representation(instance)
        representation['id'] = representation.pop('user')
        return representation


class ClientProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "id", "user")


class ExpertProfileSerializer(ProfileSerializerBase):
    education = HyperlinkedIdentityField(view_name="accounts:education")
    countries_allowed = CountryField()

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "id", "user")


class StaffProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "id", "user")

# --- Profile
# Subscription ---

class SubscriptionPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        read_only_fields = ('owner_type',)


class TherapyContractSerializer(ModelSerializer):
    user = HyperlinkedIdentityField(view_name="accounts:user")
    client = HyperlinkedIdentityField(view_name="accounts:client-profile")
    expert = HyperlinkedIdentityField(view_name="accounts:expert-profile")

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('client', 'expert', "date_start")

# --- Subscription
# --- Diary

class DiarySerializer(ModelSerializer):
    client = HyperlinkedIdentityField(view_name="accounts:client-profile")

    class Meta:
        model = Diary
        fields = "__all__"
        read_only_fields = ('client', 'date_start')

# Diary ---
