from adrf.serializers import ModelSerializer, Serializer
from asgiref.sync import sync_to_async, async_to_sync

from rest_framework.serializers import CharField, HyperlinkedIdentityField

from .models import *


# --- Education

class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'


class UniversitySerializer(ModelSerializer):
    country = CharField(max_length=2, allow_blank=False)

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
    class Meta:
        model = User
        fields = ["email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields.copy()


class ClientProfileSerializer(ModelSerializer):
    user = HyperlinkedIdentityField(view_name="accounts:user")
    country = CharField(max_length=2, allow_blank=False)

    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('date_birth', 'user')


class ExpertProfileSerializer(ModelSerializer):
    user = HyperlinkedIdentityField(view_name="accounts:user")
    education = HyperlinkedIdentityField(view_name="accounts:education")

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', 'user')


class StaffProfileSerializer(ModelSerializer):
    user = HyperlinkedIdentityField(view_name="accounts:user")

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', 'user')

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
