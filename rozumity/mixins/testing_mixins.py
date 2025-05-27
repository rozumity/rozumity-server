# python manage.py test
# python ../manage.py test accounts
from httpx import AsyncClient, ASGITransport
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from asgiref.sync import sync_to_async, async_to_sync
from rozumity.asgi import application
from accounts.models import ClientProfile, ExpertProfile
from educations.models import *


class ProfileCreationMixin:
    @staticmethod
    def get_emails():
        return {
            "client": "client@user.com",
            "expert": "expert@user.com",
            "staff": "staff@user.com"
        }
    
    @staticmethod
    def get_password():
        return "password123"

    @staticmethod
    async def get_user_model():
        return await sync_to_async(get_user_model)()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_model = get_user_model()
        emails, password = cls.get_emails(), cls.get_password()
        cls.user_client = user_model.objects.create_user(
            email=emails["client"],
            password=password,
            is_client=True
        )
        cls.user_expert = user_model.objects.create_user(
            email=emails["expert"], password=password,
            is_expert=True
        )
        cls.user_staff = user_model.objects.create_superuser(
            email=emails["staff"], password=password
        )

    def setUp(self):
        self.profile_client = ClientProfile.objects.get(
            user=self.user_client
        )
        self.profile_expert = ExpertProfile.objects.get(
            user=self.user_expert
        )
        self.api_client = AsyncClient(
            transport=ASGITransport(app=application), 
            base_url="http://testserver"
        )
        self.token_client = str(RefreshToken.for_user(
            self.user_client
        ).access_token)
        self.token_expert = str(RefreshToken.for_user(
            self.user_expert
        ).access_token)
