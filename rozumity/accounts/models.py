from datetime import date, timedelta, timezone

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
#from django.contrib.postgres.fields import ArrayField

from .managers import EmailUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, max_length=64)
    is_staff = models.BooleanField(default=False)
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


class Speciality(models.Model):
    code = models.SmallIntegerField()
    title = models.CharField(max_length=128)

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
    DEGREE_CHOICES = (
        (0, _('course')), (1, _('undergraduate')), (2, _('specialist')), (3, _('master')), 
        (4, _('postgraduate')), (5, _('doctor'))
    )
    university = models.ForeignKey(University, on_delete=models.PROTECT)
    degree = models.SmallIntegerField(choices=DEGREE_CHOICES, default=0)
    speciality = models.ForeignKey('Speciality', on_delete=models.PROTECT, null=True)
    date_start = models.DateField()
    date_end = models.DateField()

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    @property
    def education_duration(self):
        delta = self.date_start - self.date_end
        return round(delta.days / 365)


class AbstractProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text=_('User (Required).'), primary_key=True)
    GENDER_CHOICES = (
        (0, _('male')), (1, _('female')), (2, _('non-binary')), (3, _('transgender')), 
        (4, _('intersex')), (5, _('prefer not to say'))
    )

    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    # PostgreSQL specific django_postgres_extensions
    # Allows to select multiple genders at once, for example, intersex female
    #gender = ArrayField(models.SmallIntegerField(choices=GENDER_CHOICES, default=5), default=(5,), max_length=2, size=2)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=5)
    country = CountryField(blank=True, blank_label="(Select country)")
    date_birth = models.DateField(default=date.today()-timedelta(days=18*365), blank=True, null=True)

    class Meta:
        abstract=True

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def name_reversed(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def age(self):
        return (date.today() - self.date_birth).days / 365

    @property
    def is_adult(self):
        return True if self.age > 18 else False

    @property
    def gender_verbose(self):
        genders = dict(self.GENDER_CHOICES)
        return ', '.join([genders[gender] for gender in self.gender])

    @property
    def gender_default(self):
        return (5, _('prefer not to say'))


class ClientProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Client's Profile")
        verbose_name_plural = _("Clients' Profiles")

    def __str__(self):
        return str(self.user.email)


class ExpertProfile(AbstractProfile):
    education = models.ManyToManyField(Education, blank=True)
    education_extra = models.TextField(max_length=500, blank=True)
    countries_allowed = CountryField(multiple=True, blank=True, blank_label="(Select countries)")

    class Meta:
        verbose_name = _("Expert's Profile")
        verbose_name_plural = _("Experts' Profiles")

    def __str__(self):
        return str(self.user.email)


class StaffProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Staff member's Profile")
        verbose_name_plural = _("Staff members' Profiles")

    def __str__(self):
        return str(self.user.email)


class SubscriptionPlan(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    duration = models.DurationField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    owner_type = models.SmallIntegerField(choices=((0, _('client')), (1, _('expert'))), default=0)
    has_diary = models.BooleanField(default=False)
    has_ai = models.BooleanField(default=False)
    has_screening = models.BooleanField(default=False)
    has_dyagnosis = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")

    def __str__(self):
        return f"{self.title} - {self.price} ({self.owner_type})"


class TherapyContract(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE)
    subscriptionClient = models.ForeignKey('SubscriptionPlan', on_delete=models.PROTECT, related_name="contractClientPlan")
    subscriptionExpert = models.ForeignKey('SubscriptionPlan', on_delete=models.PROTECT, related_name="contractExpertPlan")
    date_start = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Therapy Contract")
        verbose_name_plural = _("Therapy Contracts")

    def __str__(self):
        return f'{self.client} - {self.expert}'

    @property
    def is_paid(self):
        return True if self.subscriptionClient or self.subscriptionExpert else False

    @property
    def is_paid_full(self):
        return True if self.subscriptionClient and self.subscriptionExpert else False

    @property
    def is_paid_client(self):
        return True if self.subscriptionClient else False

    @property
    def is_paid_expert(self):
        return True if self.subscriptionExpert else False

    @property
    def date_end_client(self):
        if self.subscriptionClient:
            return self.date_start + timedelta(days=self.subscriptionClient.duration)

    @property
    def date_end_expert(self):
        if self.subscriptionExpert:
            return self.date_start + timedelta(days=self.subscriptionExpert.duration)

    @property
    def date_end(self):
        date_end_client = self.date_end_client
        date_end_expert = self.date_end_expert
        if date_end_client or date_end_expert:
            return date_end_client if date_end_client > date_end_expert else date_end_expert

    @property
    def is_active_client(self):
        return self.date_end_client < timezone.now()

    @property
    def is_active_expert(self):
        return self.date_end_expert < timezone.now()

    @property
    def is_active(self):
        return self.date_end < timezone.now()

    @property
    def has_diary(self):
        return self.subscriptionClient.has_diary or self.subscriptionExpert.has_diary

    @property
    def has_ai(self):
        return self.subscriptionClient.has_ai or self.subscriptionExpert.has_ai

    @property
    def has_screening(self):
        return self.subscriptionClient.has_screening or self.subscriptionExpert.has_screening

    @property
    def has_dyagnosis(self):
        return self.subscriptionExpert.has_dyagnosis


class Diary(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    theme = models.SmallIntegerField(choices=((0, _('light')), (1, _('dark'))), default=0)
    has_health_attention = models.BooleanField(default=False)
    date_start = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = _("Diary")
        verbose_name_plural = _("Diaries")
    
    def __str__(self):
        return f'{self.client} - {self.expert}'
