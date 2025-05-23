from adrf.serializers import ModelSerializer
from rest_framework.serializers import (
    HyperlinkedIdentityField, EmailField, 
    PrimaryKeyRelatedField, CharField
)
from django_countries.serializer_fields import CountryField

from rozumity.mixins.serialization_mixins import (
    CountryFieldMixin, ReadOnlySerializerMixin
)

from educations.serializers import EducationSerializer

from accounts.models import *
from educations.models import Education

# --- Profile

class UserSerializer(ModelSerializer):
    email = EmailField()

    class Meta:
        model = User
        fields = ["id", "email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields.copy()


class ProfileSerializerBase(CountryFieldMixin, ModelSerializer):
    email = PrimaryKeyRelatedField(
        queryset=User.objects.select_related('clientprofile','expertprofile').all()
    )
    country = CountryField()
    gender = CharField(source='get_gender_display')
    custom_id = "email"


class ClientProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "email")


class ExpertProfileReadOnlySerializer(
    ReadOnlySerializerMixin, ProfileSerializerBase
):
    education = EducationSerializer(many=True)
    countries_allowed = CountryField()

    class Meta:
        model = ExpertProfile
        fields = "__all__"


class ExpertProfileSerializer(ProfileSerializerBase):
    education = PrimaryKeyRelatedField(
        queryset = Education.objects.select_related(
            'university','speciality'
        ).all(), 
        many=True
    )
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
    owner_type = CharField(source='get_owner_type_display')

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
