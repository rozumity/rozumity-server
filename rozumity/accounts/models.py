from datetime import date, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    use_in_migrations = True
    
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, max_length=64)
    is_staff = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


# TODO: subscription plans
class AbstractProfile(models.Model):
    GENDER_CHOICES = (
        (0, _('male')), (1, _('female')), (2, _('non-binary')), (3, _('transgender')), 
        (4, _('intersex')), (5, _('prefer not to say'))
    )

    @staticmethod
    def get_default_gender():
        return (5,)

    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text=_('User (Required).'))
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    gender = ArrayField(models.SmallIntegerField(choices=GENDER_CHOICES, default=5), 
                        default=get_default_gender, max_length=2, size=2)
    country = CountryField(blank=True, null=True)
    date_birth = models.DateField(default=date.today()-timedelta(days=18*365), blank=True, null=True)
    
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
    country = CountryField()
    
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
    
    @property
    def education_duration(self):
        delta = self.date_start - self.date_end
        return round(delta.days / 365)


class ClientProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Client's Profile")
        verbose_name_plural = _("Clients' Profiles")
    
    def __str__(self):
        return str(self.user.email)


class ExpertProfile(AbstractProfile):
    education = models.ManyToManyField(Education, blank=True)
    education_extra = models.TextField(max_length=500, blank=True)
    countries_allowed = CountryField(many=True, blank=True, null=True)

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
