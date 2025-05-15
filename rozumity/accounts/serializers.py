from adrf.serializers import ModelSerializer
from rest_framework.serializers import (
    HyperlinkedIdentityField, EmailField, 
    PrimaryKeyRelatedField, CharField
)
from django_countries.serializer_fields import CountryField

from rozumity.mixins.serialization_mixins import CountryFieldMixin

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
    university = PrimaryKeyRelatedField(queryset=University.objects.all())
    speciality = PrimaryKeyRelatedField(queryset=Speciality.objects.all())

    class Meta:
        model = Education
        fields = "__all__"
        read_only_fields = ('university', "speciality")

# Education ---
# --- Profile

class UserSerializer(ModelSerializer):
    email = EmailField()

    class Meta:
        model = User
        fields = ["id", "email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields.copy()


class ProfileSerializerBase(CountryFieldMixin, ModelSerializer):
    country = CountryField()
    gender = CharField(source='get_gender_display')
    custom_id = "email"


class ClientProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "email")


class ExpertProfileSerializer(ProfileSerializerBase):
    education = EducationSerializer(many=True)
    countries_allowed = CountryField()

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "email")


class StaffProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "id")

# --- Profile
# Subscription ---

class SubscriptionPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"
        read_only_fields = ('owner_type',)


class TherapyContractSerializer(ModelSerializer):
    client = PrimaryKeyRelatedField(queryset=ClientProfile.objects.all(), required=False)
    expert = PrimaryKeyRelatedField(queryset=ExpertProfile.objects.all(), required=False)
    client_plan = PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all(), required=False)
    expert_plan = PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all(), required=False)

    class Meta:
        model = TherapyContract
        fields = "__all__"
        read_only_fields = ('client', 'expert', "contract_start_date")

# --- Subscription
# --- Diary

class DiarySerializer(ModelSerializer):
    client = HyperlinkedIdentityField(view_name="accounts:client-profile")

    class Meta:
        model = Diary
        fields = "__all__"
        read_only_fields = ('client', 'date_start')

# Diary ---
