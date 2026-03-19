from adrf.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ChoiceField, ReadOnlyField, EmailField, IntegerField, CharField
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
    id = ReadOnlyField(source='user.id')
    email = ReadOnlyField(source='user.email')
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
    # Read-only nested representation for responses
    university_detail = UniversitySerializer(source='university', read_only=True)
    speciality_detail = SpecialitySerializer(source='speciality', read_only=True)
    degree_display = ReadOnlyField(source='get_degree_display')

    class Meta:
        model = Education
        fields = (
            'id', 'expert', 'university', 'university_detail', 
            'speciality', 'speciality_detail', 'degree', 
            'degree_display', 'date_start', 'date_end'
        )
        extra_kwargs = {
            # university and speciality IDs are used for writing
            'university': {'write_only': True},
            'speciality': {'write_only': True},
            # expert is not required in the input payload
            'expert': {'read_only': True}
        }

    async def acreate(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['expert'] = await ExpertProfile.objects.aget(user=request.user)
        
        return await super().acreate(validated_data)

# --- Expert Profile ---

class ExpertProfileSerializer(ProfileSerializerBase):
    countries_allowed = CountryField(multiple=True)
    educations = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = ExpertProfile
        exclude = ('user',)

# --- Client Profile ---

class ClientProfileSerializer(ProfileSerializerBase):
    countries_allowed = CountryField(multiple=True)

    class Meta:
        model = ClientProfile
        exclude = ('user',)

# --- Subscription Plan ---

class SubscriptionPlanSerializer(ModelSerializer):
    price = MoneyField(max_digits=14, decimal_places=2)
    price_currency = ReadOnlyField(source='get_price_currency_display')
    duration_display = ReadOnlyField(source='get_duration_display')
    duration = IntegerField(write_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

# --- Subscription ---

class SubscriptionSerializer(ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)

    class Meta:
        model = SubscriptionPlan
        exclude = ('user', 'plan')

# --- Therapy Contract ---

class TherapyContractSerializer(ModelSerializer):
    invite_email = EmailField(write_only=True, required=False)
    client_details = ClientProfileSerializer(source='client', read_only=True)
    expert_details = ExpertProfileSerializer(source='expert', read_only=True)
    client = CharField(allow_null=True, default=None, write_only=True, required=False)
    expert = CharField(allow_null=True, default=None, write_only=True, required=False)

    class Meta:
        model = TherapyContract
        fields = "__all__"
        read_only_fields = ("contract_start_date",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        method = request.method if request else None
        if method in ['PATCH', 'PUT'] or self.instance:
            self.fields.pop('invite_email', None)
        elif method == 'POST' or not self.instance:
            self.fields.pop('is_deleted', None)
            self.fields.pop('is_active', None)
            self.fields.pop('client', None)
            self.fields.pop('expert', None)
            if request and hasattr(request.user, 'expert_profile'):
                if 'invite_email' in self.fields:
                    self.fields['invite_email'].required = True

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        if self.instance:
            attrs.pop('invite_email', None)
            for field in ['client', 'expert']:
                if field in attrs and attrs[field] is not None:
                    attrs.pop(field)
            return attrs

        invite_email = attrs.pop('invite_email', None)
        client_prof = getattr(user, 'client_profile', None)
        expert_prof = getattr(user, 'expert_profile', None)
        try:
            if client_prof:
                attrs['client'] = client_prof
                attrs['expert'] = None if not invite_email else ExpertProfile.objects.get(user__email=invite_email)
            elif expert_prof:
                attrs['expert'] = expert_prof
                attrs['client'] = ClientProfile.objects.get(user__email=invite_email)
            else:
                raise ValidationError("Profile not found.")
        except (ExpertProfile.DoesNotExist, ClientProfile.DoesNotExist):
            raise ValidationError({"invite_email": "Profile not found."})
        return attrs
