import uuid
from datetime import date, timedelta, timezone

from django.db import models
from django.utils import timezone
from django.core.exceptions import SynchronousOnlyOperation
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField

from rozumity.utils import rel

from accounts.managers import EmailUserManager


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


class AbstractProfile(models.Model):
    class GenderChoices(models.IntegerChoices):
        MALE = 0, _("Male")
        FEMALE = 1, _("Female")
        NONBINARY = 2, _("Non-binary")
        TRANSGENDER = 3, _("Transgender")
        INTERSEX = 4, _("Intersex")
        HIDE = 5, _("Prefer not to say")

    user = models.OneToOneField(
        User, on_delete=models.RESTRICT, primary_key=True, editable=False
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
    education = models.ManyToManyField('educations.Education', blank=True)
    education_extra = models.TextField(max_length=500, default="")
    countries_allowed = CountryField(
        multiple=True, blank=True, 
        blank_label=_("Select countries")
    )

    class Meta:
        verbose_name = _("Profile Expert")
        verbose_name_plural = _("Profiles Expert")
        default_related_name = "expertprofile"
    
    @property
    async def clients(self):
        contracts = await rel(self, "contracts")
        return [await rel(c, 'client') async for c in contracts.all()]


class StaffProfile(AbstractProfile):
    class Meta:
        verbose_name = _("Profile Staff")
        verbose_name_plural = _("Profiles Staff")


class SubscriptionPlan(models.Model):
    class OwnerTypes(models.IntegerChoices):
        CLIENT = 0, _("Client")
        EXPERT = 1, _("Expert")
        BOTH = 2, _("Both")

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
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
    class DurationDays(models.IntegerChoices):
        FREE = 0, _("Free")
        DAY = 1, _("Day")
        WEEK = 7, _("Week")
        WEEK2 = 14, _("Two weeks")
        MONTH = 30, _("Month")
        MONTH3 = 90, _("Three months")
        MONTH6 = 180, _("Half a year")
        YEAR = 360, _("Year")
        FOREVER = 999, _("Forever")

    client = models.ForeignKey(
        ClientProfile, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contracts"
    )
    expert = models.ForeignKey(
        ExpertProfile, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contracts"
    )
    client_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contract_client"
    )
    expert_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.PROTECT,
        null=True, blank=True, related_name="contract_expert"
    )
    client_plan_days = models.SmallIntegerField(
        choices=DurationDays.choices, default=DurationDays.FREE
    )
    expert_plan_days = models.SmallIntegerField(
        choices=DurationDays.choices, default=DurationDays.FREE
    )
    contract_start_date = models.DateTimeField(default=timezone.now, editable=False)
    client_plan_prolong_date = models.DateTimeField(default=timezone.now)
    expert_plan_prolong_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Therapy Contract")
        verbose_name_plural = _("Therapy Contracts")

    def __str__(self):
        return f'Contract | Client: {self.client}, Expert: {self.expert}'

    @property
    async def date_end_client(self):
        if self.client_plan_duration:
            return self.client_plan_prolong_date + timedelta(
                days=self.client_plan_days
            )

    @property
    async def date_end_expert(self):
        if self.expert_plan:
            return self.expert_plan_prolong_date + timedelta(
                days=self.expert_plan_days
            )

    @property
    async def date_end(self):
        return max(await self.date_end_client, await self.date_end_expert)

    @property
    async def is_paid(self):
        return any((
            self.client_plan_days != self.DurationDays.FREE,
            self.expert_plan_days != self.DurationDays.FREE
        ))

    @property
    async def is_paid_full(self):
        return all((
            self.client_plan_days != self.DurationDays.FREE,
            self.expert_plan_days != self.DurationDays.FREE
        ))

    @property
    async def is_paid_client(self):
        return self.client_plan_days != self.DurationDays.FREE

    @property
    async def is_paid_expert(self):
        return self.expert_plan_days != self.DurationDays.FREE

    @property
    async def is_active_client(self):
        if await self.is_paid_client:
            return await self.date_end_client > timezone.now()
        return False

    @property
    async def is_active_expert(self):
        if await self.is_paid_expert:
            return await self.date_end_expert > timezone.now()
        return False

    @property
    async def is_active(self):
        if await self.is_paid:
            return any((
                await self.is_active_client,
                await self.is_active_expert
            ))
        return False

    @property
    async def is_active_full(self):
        if await self.is_paid_full:
            return await self.date_end > timezone.now()
        return False

    @property
    async def has_client_only(self):
        return all((await rel(self, "client"), not await rel(self, "expert")))

    @property
    async def has_expert_only(self):
        return all((await rel(self, "expert"), not await rel(self, "client")))

    @property
    async def has_both(self):
        return all((await rel(self, "expert"), await rel(self, "client")))

    @property
    async def has_diary(self):
        client_plan = await rel(self, "client_plan")
        expert_plan = await rel(self, "expert_plan")
        return any((client_plan.has_diary, expert_plan.has_diary))

    @property
    async def has_ai(self):
        client_plan = await rel(self, "client_plan")
        expert_plan = await rel(self, "expert_plan")
        return any((client_plan.has_ai, expert_plan.has_ai))

    @property
    async def has_screening(self):
        client_plan = await rel(self, "client_plan")
        expert_plan = await rel(self, "expert_plan")
        return any((client_plan.has_screening, expert_plan.has_screening))

    @property
    async def has_dyagnosis(self):
        expert_plan = await rel(self, "expert_plan")
        return expert_plan.has_dyagnosis
