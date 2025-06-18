# python manage.py test
import asyncio
from httpx import AsyncClient, ASGITransport
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from asgiref.sync import sync_to_async
from rozumity.asgi import application
from accounts.models import ClientProfile, ExpertProfile
from educations.models import *


class APIClientTestMixin:
    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_model = get_user_model()
        cls.user_client = user_model.objects.filter(is_client=True).first()
        cls.user_expert = user_model.objects.filter(is_expert=True).first()
        cls.profile_client = ClientProfile.objects.filter(pk=cls.user_client.id).first()
        cls.profile_expert = ExpertProfile.objects.filter(pk=cls.user_expert.id).first()
        cls.api_client = AsyncClient(
            transport=ASGITransport(app=application), 
            base_url="http://testserver"
        )
        cls.token_client = str(RefreshToken.for_user(
            cls.user_client
        ).access_token)
        cls.token_expert = str(RefreshToken.for_user(
            cls.user_expert
        ).access_token)
        cls.method_client_map = {
            "get": cls.api_client.get,
            "post": cls.api_client.post,
            "put": cls.api_client.put,                
            "patch": cls.api_client.patch,
            "delete": cls.api_client.delete
        }

    @classmethod
    def tearDownClass(cls):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(cls.api_client.aclose())
        else:
            loop.run_until_complete(cls.api_client.aclose())

    @staticmethod
    async def get_user_model():
        return await sync_to_async(get_user_model)()

    async def api(self, method:str="get", url="/", data={}, token=None):
        req = self.method_client_map[method]
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if method == 'get':
            return await req(url, headers=headers, params=data)
        return await req(url, headers=headers, json=data)


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
        cls.profile_client = ClientProfile.objects.get(
            user=cls.user_client
        )
        cls.profile_expert = ExpertProfile.objects.get(
            user=cls.user_expert
        )
