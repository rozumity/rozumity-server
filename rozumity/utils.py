from asgiref.sync import sync_to_async
from django_countries.serializers import CountryFieldMixin
from django.contrib.auth import get_user_model


async def rel(obj, field:str):
    return await sync_to_async(getattr)(obj, field)


class CountryFieldMixinAsync(CountryFieldMixin):
    async def build_standard_field(self, field_name, model_field):
        return sync_to_async(super().build_standard_field)(field_name, model_field)


class ProfileCreationMixin:
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for tests in classes that inherit from this mixin.
        
        Creates two users: a client and an expert, and their associated profiles.
        The users are created with the email addresses "client@user.com" and
        "expert@user.com", and the password "password123".
        """
        User = get_user_model()
        cls.u_client = User.objects.create_user(
            email="client@user.com", password="password123", is_client=True
        )
        cls.u_expert = User.objects.create_user(
            email="expert@user.com", password="password123", is_expert=True
        )
        cls.p_client = cls.u_client.clientprofile
        cls.p_expert = cls.u_expert.expertprofile
