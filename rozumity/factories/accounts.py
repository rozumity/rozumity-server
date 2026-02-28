import factory
from datetime import date
from accounts.models import *

from .base import Factory


class UserFactory(Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user_{n}@rozumity.com")
    is_client = False
    is_expert = False
    is_staff = False
    is_active = True


class SubscriptionPlanFactory(Factory):
    class Meta:
        model = SubscriptionPlan

    title = factory.Sequence(lambda n: f"Plan {n}")
    description = factory.Faker("sentence", nb_words=10)
    price = 50.00
    owner_type = SubscriptionPlan.OwnerTypes.BOTH
    has_diary = False
    has_ai = False


class ClientProfileFactory(Factory):
    class Meta:
        model = ClientProfile
        django_get_or_create = ('user',)
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory, is_client=True)
    first_name = factory.Faker("first_name", locale="en_US")
    last_name = factory.Faker("last_name", locale="en_US")
    country = "UA"
    date_birth = date(1990, 1, 1)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.pop('user')
        instance, _ = model_class.objects.update_or_create(
            user=user, defaults=kwargs
        )
        return instance


class ExpertProfileFactory(Factory):
    class Meta:
        model = ExpertProfile
        django_get_or_create = ('user',)
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory, is_expert=True)
    first_name = factory.Faker("first_name", locale="en_US")
    last_name = factory.Faker("last_name", locale="en_US")
    country = "US"
    education_extra = "Some extra courses"
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.pop('user')
        instance, _ = model_class.objects.update_or_create(
            user=user, defaults=kwargs
        )
        return instance

    @factory.post_generation
    def education(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for edu in extracted:
                self.education.add(edu)

class TherapyContractFactory(Factory):
    class Meta:
        model = TherapyContract

    client = factory.SubFactory(ClientProfileFactory)
    expert = factory.SubFactory(ExpertProfileFactory)
    client_plan = factory.SubFactory(SubscriptionPlanFactory)
    expert_plan = factory.SubFactory(SubscriptionPlanFactory)
    
    client_plan_days = TherapyContract.DurationDays.MONTH
    expert_plan_days = TherapyContract.DurationDays.MONTH
    
    client_plan_prolong_date = factory.LazyFunction(timezone.now)
    expert_plan_prolong_date = factory.LazyFunction(timezone.now)
