from adrf.serializers import ModelSerializer
from rest_framework.serializers import (
    EmailField, PrimaryKeyRelatedField, CharField
)
from django_countries.serializer_fields import CountryField

from rozumity.utils import CountryFieldMixin

from accounts.models import *

# --- Profile

class UserSerializer(ModelSerializer):
    email = EmailField()

    class Meta:
        model = User
        fields = ["id", "email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields.copy()


class ProfileSerializerBase(CountryFieldMixin, ModelSerializer):
    user = PrimaryKeyRelatedField(
        queryset=User.objects.select_related('clientprofile','expertprofile').all()
    )
    country = CountryField()
    gender = CharField(source='get_gender_display')
    custom_id = "user"


class ClientProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "user")


class ExpertProfileSerializer(ProfileSerializerBase):
    countries_allowed = CountryField()
    
    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('date_birth', 'user')

    async def ato_representation(self, instance):
        representation = await super().ato_representation(instance)
        representation['education'] = await EducationSerializer(
            instance.education.all(), many=True
        ).adata
        return representation


class StaffProfileSerializer(ProfileSerializerBase):
    class Meta:
        model = StaffProfile
        fields = "__all__"
        read_only_fields = ('date_birth', "user")

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
    degree_display = CharField(source='get_degree_display', read_only=True)

    class Meta:
        model = Education
        fields = "__all__"

    async def ato_representation(self, instance):
        representation = await super().ato_representation(instance)
        representation['university'] = await UniversitySerializer(instance.university).adata
        return representation


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
