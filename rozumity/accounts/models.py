import uuid
from datetime import date, timedelta, timezone

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
#from django.contrib.postgres.fields import ArrayField

from .managers import EmailUserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(_("email address"), unique=True, max_length=64)
    is_client = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = EmailUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return str(self.email)
    
    @property
    def is_staff(self):
        return self.is_superuser


class AbstractProfile(models.Model):
    class GenderChoices(models.IntegerChoices):
        MALE = 0, _("Male")
        FEMALE = 1, _("Female")
        NONBINARY = 2, _("Non-binary")
        TRANSGENDER = 3, _("Transgender")
        INTERSEX = 4, _("Intersex")
        HIDE = 5, _("Prefer not to say")

    id = models.OneToOneField(
        User, on_delete=models.CASCADE, help_text=_('User Email'), 
        primary_key=True, to_field='email', editable=False
    )

    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    # PostgreSQL specific django_postgres_extensions
    # Allows to select multiple genders at once, for example, intersex female
    #gender = ArrayField(models.SmallIntegerField(choices=GENDER_CHOICES, default=5), default=(5,), max_length=2, size=2)
    gender = models.SmallIntegerField(choices=GenderChoices.choices, default=GenderChoices.HIDE)
    country = CountryField(blank=True, blank_label="(Select country)")
    date_birth = models.DateField(
        default=date.today()-timedelta(days=18*365), blank=True, null=True
    )

    class Meta:
        abstract=True

    @property
    def email(self):
        return self.id_id

    @property
    async def email_async(self):
        return self.id_id

    def __str__(self):
        return str(self.email)
    
    @property
    async def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    async def name_reversed(self):
        return f'{self.last_name} {self.first_name}'

    @property
    async def age(self):
        return (date.today() - self.date_birth).days / 365

    @property
    async def is_adult(self):
        return True if self.age > 18 else False

    @property
    async def gender_verbose(self):
        return self.get_gender_display()


class ClientProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Client's Profile")
        verbose_name_plural = _("Clients' Profiles")
        default_related_name = 'clientprofile'


class ExpertProfile(AbstractProfile):
    education = models.ManyToManyField('Education', blank=True)
    education_extra = models.TextField(max_length=500, blank=True)
    countries_allowed = CountryField(multiple=True, blank=True, blank_label="(Select countries)")

    class Meta:
        verbose_name = _("Expert's Profile")
        verbose_name_plural = _("Experts' Profiles")
        default_related_name = 'expertprofile'


class StaffProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Staff member's Profile")
        verbose_name_plural = _("Staff members' Profiles")


class Speciality(models.Model):
    code = models.SmallIntegerField()
    title = models.CharField(max_length=128)
    is_medical = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Speciality')
        verbose_name_plural = _('Specialities')

    def __str__(self):
        return str(self.title)


class University(models.Model):
    title = models.CharField(max_length=128)
    country = CountryField(blank_label="(Select country)")

    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')

    def __str__(self):
        return str(self.title)


# TODO: possibility to upload or share a diploma or a certificate
class Education(models.Model):
    class DegreeChoices(models.IntegerChoices):
        COURSE = 0, _("Course")
        UNDER = 1, _("Undergraduate")
        SPEC = 2, _("Specialist")
        MASTER = 3, _("Master")
        POST = 4, _("Postgraduate")
        DOC = 5, _("Doctor")

    university = models.ForeignKey(University, on_delete=models.PROTECT)
    degree = models.SmallIntegerField(choices=DegreeChoices.choices, default=DegreeChoices.COURSE)
    speciality = models.ForeignKey('Speciality', on_delete=models.PROTECT, null=True)
    date_start = models.DateField()
    date_end = models.DateField()
    is_medical = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    @property
    async def education_duration(self):
        delta = self.date_start - self.date_end
        return round(delta.days / 365)


class SubscriptionPlan(models.Model):
    class OwnerTypes(models.IntegerChoices):
        CLIENT = 0, _("Client")
        EXPERT = 1, _("Expert")
        BOTH = 2, _("Both")

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    duration = models.DurationField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    owner_type = models.SmallIntegerField(
        choices=OwnerTypes.choices, default=OwnerTypes.BOTH
    )
    has_diary = models.BooleanField(default=False)
    has_ai = models.BooleanField(default=False)
    has_screening = models.BooleanField(default=False)
    has_dyagnosis = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")

    def __str__(self):
        return f"{self.title} - {self.price} ({self.get_owner_type_display()})"


class TherapyContract(models.Model):
    client_email = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, blank=True,
        related_name="contract"
    )
    expert_email = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, blank=True,
        related_name="contract"
    )
    client_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT, blank=True,
        related_name="client_contract"
    )
    expert_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT, blank=True,
        related_name="expert_contract"
    )
    date_start = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Therapy Contract")
        verbose_name_plural = _("Therapy Contracts")

    def __str__(self):
        return f'Contract | Client: {self.client_email}, Expert: {self.expert_email}'

    @property
    async def is_paid(self):
        return any(self.subscriptionClient, self.subscriptionExpert)

    @property
    async def is_paid_full(self):
        return all(self.subscriptionClient, self.subscriptionExpert)

    @property
    async def is_paid_client(self):
        return True if self.subscriptionClient else False

    @property
    async def is_paid_expert(self):
        return True if self.subscriptionExpert else False

    @property
    async def date_end_client(self):
        if self.subscriptionClient:
            return self.date_start + timedelta(days=self.subscriptionClient.duration)

    @property
    async def date_end_expert(self):
        if self.subscriptionExpert:
            return self.date_start + timedelta(days=self.subscriptionExpert.duration)

    @property
    async def date_end(self):
        date_end_client = self.date_end_client
        date_end_expert = self.date_end_expert
        if date_end_client or date_end_expert:
            return date_end_client if date_end_client > date_end_expert else date_end_expert

    @property
    async def is_active_client(self):
        return self.date_end_client < timezone.now()

    @property
    async def is_active_expert(self):
        return self.date_end_expert < timezone.now()

    @property
    async def is_active(self):
        return self.date_end < timezone.now()

    @property
    async def has_diary(self):
        return any(
            self.subscriptionClient.has_diary,
            self.subscriptionExpert.has_diary
        )

    @property
    async def has_ai(self):
        return any(
            self.subscriptionClient.has_ai,
            self.subscriptionExpert.has_ai
        )

    @property
    async def has_screening(self):
        return any(
            self.subscriptionClient.has_screening,
            self.subscriptionExpert.has_screening
        )

    @property
    async def has_dyagnosis(self):
        return self.subscriptionExpert.has_dyagnosis


class Diary(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, to_field="id")
    theme = models.SmallIntegerField(choices=((0, _('light')), (1, _('dark'))), default=0)
    has_health_attention = models.BooleanField(default=False)
    date_start = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = _("Diary")
        verbose_name_plural = _("Diaries")
    
    def __str__(self):
        return f'{self.client} - {self.expert}'
