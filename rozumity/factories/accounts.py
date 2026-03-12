import factory
import uuid
from datetime import date, timedelta
from django.utils import timezone
from accounts.models import (
    User, SubscriptionPlan, ClientProfile, ExpertProfile, 
    TherapyContract, Speciality, University, Education
)
from rozumity.factories.base import Factory

# --- USER FACTORY ---

class UserFactory(Factory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user_{n}@rozumity.com")
    is_client = False
    is_expert = False
    is_staff = False  # Set to False by default to avoid creating StaffProfile unnecessarily
    is_active = True
    date_joined = factory.LazyFunction(timezone.now)

# --- PROFILES ---

class ClientProfileFactory(Factory):
    class Meta:
        model = ClientProfile
        django_get_or_create = ('user',)

    # When creating a profile, User will receive is_client=True
    user = factory.SubFactory(UserFactory, is_client=True, is_staff=False)
    first_name = factory.Faker("first_name", locale="en_US")
    last_name = factory.Faker("last_name", locale="en_US")
    country = "UA"
    date_birth = date(1990, 1, 1)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.pop('user')
        instance, _ = model_class.objects.update_or_create(
            user=user, 
            defaults=kwargs
        )
        return instance


class ExpertProfileFactory(Factory):
    class Meta:
        model = ExpertProfile
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory, is_expert=True, is_staff=False)
    first_name = factory.Faker("first_name", locale="en_US")
    last_name = factory.Faker("last_name", locale="en_US")
    country = "US"
    education_extra = "Some extra courses"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Synchronize defaults with data coming from the factory to handle 
        cases where the profile was already auto-created by the User model.
        """
        user = kwargs.pop('user')
        instance, _ = model_class.objects.update_or_create(user=user, defaults=kwargs)
        return instance

    @factory.post_generation
    def education(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for edu in extracted:
                self.education.add(edu)

# --- INFRASTRUCTURE ---

class SubscriptionPlanFactory(Factory):
    class Meta:
        model = SubscriptionPlan

    title = factory.Sequence(lambda n: f"Plan {n}")
    description = factory.Faker("sentence", nb_words=10)
    price = 50.00
    owner_type = SubscriptionPlan.OwnerTypes.BOTH
    has_diary = False
    has_ai = False


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

# --- EDUCATIONS ---

class SpecialityFactory(Factory):
    class Meta:
        model = Speciality

    code = factory.Iterator(["053", "035", "225"])
    title = factory.Iterator(["Psychology", "Philology", "Medical Psychology"])
    code_world = "0313"
    title_world = "Psychology"
    is_medical = False


class UniversityFactory(Factory):
    class Meta:
        model = University

    title = factory.Sequence(lambda n: f"University №{n}")
    title_world = factory.Sequence(lambda n: f"University №{n}")
    country = "US"


class EducationFactory(Factory):
    class Meta:
        model = Education

    university = factory.SubFactory(UniversityFactory)
    degree = Education.DegreeChoices.MASTER
    speciality = factory.SubFactory(SpecialityFactory)
    expert = factory.SubFactory(ExpertProfileFactory) # Mandatory relationship
    date_start = factory.LazyFunction(lambda: date.today() - timedelta(days=5*365))
    date_end = factory.LazyFunction(lambda: date.today() - timedelta(days=1*365))
