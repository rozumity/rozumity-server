from adrf.serializers import ModelSerializer
from rest_framework.serializers import (
    ChoiceField, ReadOnlyField
)
from djmoney.contrib.django_rest_framework import MoneyField
from django_countries.serializer_fields import CountryField
from rozumity.utils import CountryFieldMixin
from accounts.models import *

# --- Profile ---

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "is_staff", "is_client", "is_expert", "is_active", "date_joined"]
        read_only_fields = fields


class ProfileSerializerBase(CountryFieldMixin, ModelSerializer):
    user_email = ReadOnlyField(source='user.email')
    country = CountryField()
    gender_display = ReadOnlyField(source='get_gender_display')

    class Meta:
        abstract = True

# --- Education ---

class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = Speciality
        fields = '__all__'

class UniversitySerializer(CountryFieldMixin, ModelSerializer):
    class Meta:
        model = University
        fields = '__all__'

class EducationSerializer(ModelSerializer):
    university_info = UniversitySerializer(source='university', read_only=True)
    speciality_info = SpecialitySerializer(source='speciality', read_only=True)
    degree_display = ReadOnlyField(source='get_degree_display')

    class Meta:
        model = Education
        fields = "__all__"
        extra_kwargs = {
            'university': {'write_only': True},
            'speciality': {'write_only': True},
            'expert': {'read_only': True}
        }

# --- Expert Profile (сложный случай) ---

class ExpertProfileSerializer(ProfileSerializerBase):
    countries_allowed = CountryField(multiple=True)
    educations = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = ExpertProfile
        fields = "__all__"
        read_only_fields = ('user',)

# --- Client Profile ---
class ClientProfileSerializer(ProfileSerializerBase):
    countries_allowed = CountryField(multiple=True)

    class Meta:
        model = ClientProfile
        fields = "__all__"
        read_only_fields = ('user',)

# --- Therapy Contract ---

class TherapyContractSerializer(ModelSerializer):
    status_display = ReadOnlyField(source='get_status_display')

    class Meta:
        model = TherapyContract
        fields = "__all__"
        read_only_fields = ("contract_start_date", "status") 

    def create(self, validated_data):
        return super().create(validated_data)


class SubscriptionPlanSerializer(ModelSerializer):
    owner_type = ChoiceField(
        choices=SubscriptionPlan.OwnerTypes.choices, 
        source='get_owner_type_display'
    )
    price = MoneyField(max_digits=14, decimal_places=2)
    price_currency = ReadOnlyField()

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id", "title", "description", "price", "price_currency",
            "owner_type", "has_diary", "has_ai", "has_screening", 
            "has_dyagnosis"
        ]
        read_only_fields = fields
