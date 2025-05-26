# python manage.py test
# python ../manage.py test accounts
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async, async_to_sync
from accounts.models import ClientProfile, ExpertProfile
from educations.models import *


class ProfileCreationMixin:
    @staticmethod
    def get_emails():
        return {
            "client": "client@user.com",
            "expert": "expert@user.com",
        }
    
    @staticmethod
    def get_password():
        return "password123"

    @staticmethod
    async def get_user_model():
        return await sync_to_async(get_user_model)()

    @classmethod
    async def create_test_user_client(cls):
        User = await cls.get_user_model()
        return await sync_to_async(User.objects.create_user)(
            email=cls.get_emails()["client"],
            password=cls.get_password(),
            is_client=True
        )

    @classmethod
    async def create_test_user_expert(cls):
        User = await cls.get_user_model()
        return await sync_to_async(User.objects.create_user)(
            email=cls.get_emails()["expert"],
            password=cls.get_password(),
            is_expert=True
        )

    @classmethod
    async def create_test_users(cls):
        return await cls.create_test_user_client(), await cls.create_test_user_expert()

    @classmethod
    async def create_test_client(cls):
        user = await cls.create_test_user_client()
        return await ClientProfile.objects.aget(user=user)

    @classmethod
    async def create_test_expert(cls):
        user = await cls.create_test_user_expert()
        return await ExpertProfile.objects.aget(user=user)

    @classmethod
    async def create_test_profiles(cls):
        user_client, user_expert = await cls.create_test_users()
        client = await ClientProfile.objects.aget(user=user_client)
        expert = await ExpertProfile.objects.aget(user=user_expert)
        return client, expert

    @classmethod
    def create_test_user_client_sync(cls):
        return async_to_sync(cls.create_test_user_client)()

    @classmethod
    def create_test_user_expert_sync(cls):
        return async_to_sync(cls.create_test_user_expert)()

    @classmethod
    def create_test_profile_client_sync(cls):
        return async_to_sync(cls.create_test_client)()
