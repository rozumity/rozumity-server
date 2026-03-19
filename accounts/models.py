import uuid
from datetime import date, timedelta, timezone

from django.db import models
from django.utils import timezone
from django.core.exceptions import SynchronousOnlyOperation
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField

from rozumity.utils import rel

from accounts.managers import EmailUserManager
import asyncio
from django.db import transaction
from asgiref.sync import async_to_sync

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    email = models.EmailField(_("email address"), unique=True, max_length=64)
    is_client = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
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
    
    def _create_profile_sync(self):
        from accounts.models import ClientProfile, ExpertProfile, StaffProfile
        if self.is_expert:
            model = ExpertProfile
        elif self.is_staff:
            model = StaffProfile
        else:
            model = ClientProfile

        model.objects.get_or_create(user=self)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(self._create_profile_sync)

    async def asave(self, *args, **kwargs):
        is_new = self._state.adding
        await super().asave(*args, **kwargs)
        if is_new:
            transaction.on_commit(self._create_profile_sync)
            
    async def anonymize(self):
        self.email = f"deleted_{uuid.uuid4().hex[:10]}@rozumity.ua"
        self.is_active = False
        self.is_deleted = True
        self.set_unusable_password() 
        
        await self.asave(update_fields=['email', 'is_active', 'is_deleted', 'password'])
        
        profile = await self.get_profile()
        if profile:
            profile.first_name = "Deleted"
            profile.last_name = "User"
            profile.country = ""
            await profile.asave()


class AbstractProfile(models.Model):
    class GenderChoices(models.IntegerChoices):
        MALE = 0, _("Male")
        FEMALE = 1, _("Female")
        NONBINARY = 2, _("Non-binary")
        TRANSGENDER = 3, _("Transgender")
        INTERSEX = 4, _("Intersex")
        HIDE = 5, _("Prefer not to say")

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, editable=False
    )
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)
    gender = models.SmallIntegerField(choices=GenderChoices.choices, default=GenderChoices.HIDE)
    country = CountryField(blank=True, blank_label="(Select country)")
    date_birth = models.DateField(
        default=date.today()-timedelta(days=18*365), blank=True, null=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        try:
            return self.user.email
        except SynchronousOnlyOperation:
            return str(self.pk)

    @property
    def id(self):
        return self.pk

    @property
    async def user_email(self):
        return getattr(await rel(self, 'user'), 'email')
    
    @property
    async def name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    async def name_reversed(self):
        return f'{self.last_name} {self.first_name}'

    @property
    async def age(self):
        return (date.today() - self.date_birth).days / 365

    @property
    async def is_adult(self):
        return True if await self.age > 18 else False

    @property
    async def gender_verbose(self):
        return self.get_gender_display()

    @property
    async def is_filled(self):
        return bool(await self.name) and bool(self.country)

    @property
    async def is_empty(self):
        return not await self.is_filled


class ClientProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Profile Client")
        verbose_name_plural = _("Profiles Client")
        default_related_name = "clientprofile"
    
    @property
    async def experts(self):
        contracts = await rel(self, "contracts")
        return [await rel(c, 'expert') async for c in contracts.all()]


class ExpertProfile(AbstractProfile):
    countries_allowed = CountryField(
        multiple=True, blank=True, 
        blank_label=_("Select countries")
    )
    education_extra = models.TextField(max_length=500, default="", blank=True)

    class Meta:
        verbose_name = _("Profile Expert")
        verbose_name_plural = _("Profiles Expert")
        default_related_name = "expertprofile"
    
    @property
    async def education_list(self):
        """Повертає всі записи про освіту для цього експерта"""
        return [e async for e in self.educations.all()]

    @property
    async def clients(self):
        contracts = await rel(self, "contracts")
        return [await rel(c, 'client') async for c in contracts.all()]


class StaffProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Profile Staff")
        verbose_name_plural = _("Profiles Staff")


class Speciality(models.Model):
    code = models.CharField(
        default="053", max_length=3,
        validators=[MinLengthValidator(3)]
    )
    title = models.CharField(
        max_length=128, default="Psychology"
    )
    code_world = models.CharField(
        default="0313", max_length=4,
        validators=[MinLengthValidator(4)]
    )
    title_world = models.CharField(
        max_length=128, default="Psychology"
    )
    is_medical = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Speciality')
        verbose_name_plural = _('Specialities')

    def __str__(self):
        return f'{self.code} {self.title}'


class University(models.Model):
    title = models.CharField(max_length=128, default="")
    title_world = models.CharField(max_length=128, default="")
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

    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.CASCADE, related_name="educations", blank=True, null=True
    )
    university = models.ForeignKey(University, on_delete=models.PROTECT)
    degree = models.SmallIntegerField(choices=DegreeChoices.choices, default=DegreeChoices.COURSE)
    speciality = models.ForeignKey('Speciality', on_delete=models.PROTECT, null=True)
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return f'{self.get_degree_display()}, {self.speciality}, {self.university}'

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    @property
    async def education_duration(self):
        delta = self.date_end - self.date_start
        return round(delta.days / 365.25)


class SubscriptionPlan(models.Model):
    class DurationDays(models.IntegerChoices):
        FREE = 0, _("Free")
        WEEK2 = 14, _("Two weeks")
        MONTH = 30, _("Month")
        MONTH3 = 90, _("Three months")
        MONTH6 = 180, _("Half a year")
        YEAR = 360, _("Year")
        FOREVER = 999, _("Forever")

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    duration = models.SmallIntegerField(choices=DurationDays.choices, default=DurationDays.FREE)
    is_client = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    has_diary = models.BooleanField(default=False)
    has_ai = models.BooleanField(default=False)
    has_screening = models.BooleanField(default=False)
    has_dyagnosis = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")

    def __str__(self):
        return f"{self.title} - {self.price} ({self.get_owner_type_display()})"


class Subscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def calculate_end_date(self):
        start = self.start_date or timezone.now()
        days = self.plan.duration
        if days == SubscriptionPlan.DurationDays.FOREVER:
            return start + timedelta(days=365*100)
        return start + timedelta(days=days)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.calculate_end_date()
        super().save(*args, **kwargs)

    
class TherapyContract(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    client = models.ForeignKey(
        ClientProfile, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contracts"
    )
    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contracts"
    )
    contract_start_date = models.DateTimeField(default=timezone.now, editable=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Therapy Contract")
        verbose_name_plural = _("Therapy Contracts")

    def __str__(self):
        return f'Contract | Client: {self.client}, Expert: {self.expert}'
