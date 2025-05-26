# python manage.py test
# python ../manage.py test accounts
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async, async_to_sync
from accounts.models import ClientProfile, ExpertProfile
from educations.models import *


class ProfileCreationMixin:
    @classmethod
    def setUpTestData(cls):
        cls.emails = {
            "client": "client@user.com",
            "expert": "expert@user.com",
        }
        cls.password = "password123"

    @staticmethod
    async def get_user_model():
        return await sync_to_async(get_user_model)()

    async def create_test_user_client(self):
        User = await self.get_user_model()
        return await sync_to_async(User.objects.create_user)(
            email=self.emails["client"],
            password=self.password,
            is_client=True
        )

    async def create_test_user_expert(self):
        User = await self.get_user_model()
        return await sync_to_async(User.objects.create_user)(
            email=self.emails["expert"],
            password=self.password,
            is_expert=True
        )
    
    async def create_test_users(self):
        return await self.create_test_user_client(), await self.create_test_user_expert()

    async def create_test_client(self):
        user = await self.create_test_user_client()
        return await ClientProfile.objects.aget(user=user)

    async def create_test_expert(self):
        user = await self.create_test_user_expert()
        return await ExpertProfile.objects.aget(user=user)

    async def create_test_profiles(self):
        user_client, user_expert = await self.create_test_users()
        client = await ClientProfile.objects.aget(user=user_client)
        expert = await ExpertProfile.objects.aget(user=user_expert)
        return client, expert

    def create_test_user_client_sync(self):
        return async_to_sync(self.create_test_user_client)()

    def create_test_user_expert_sync(self):
        return async_to_sync(self.create_test_user_expert)()

    def create_test_profile_client_sync(self):
        return async_to_sync(self.create_test_client)()
