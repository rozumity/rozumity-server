# python manage.py test
# python ../manage.py test accounts
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from accounts.models import (
    ClientProfile, ExpertProfile, StaffProfile,
    TherapyContract, SubscriptionPlan
)
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
        return await ClientProfile.objects.aget(email=user.email)

    async def create_test_expert(self):
        user = await self.create_test_user_expert()
        return await ExpertProfile.objects.aget(email=user.email)

    async def create_test_profiles(self):
        user_client, user_expert = await self.create_test_users()
        client = await ClientProfile.objects.aget(email=user_client.email)
        expert = await ExpertProfile.objects.aget(email=user_expert.email)
        return client, expert


class AuthenticationTests(ProfileCreationMixin, TestCase):
    async def test_create_users(self):
        user_client, user_expert = await self.create_test_users()
        self.assertTrue(user_client.is_client)
        self.assertTrue(user_expert.is_expert)
        self.assertEqual(user_client.email, self.emails["client"])
        self.assertEqual(user_expert.email, self.emails["expert"])
        for user in (user_client, user_expert):
            self.assertTrue(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    async def test_create_superuser_profile(self):
        User = await sync_to_async(get_user_model)()
        admin_user =  await sync_to_async(User.objects.create_superuser)(
            email="super@user.com", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertFalse(hasattr(admin_user, "username"))
        profile = await StaffProfile.objects.aget(email=admin_user.email)
        self.assertIsNotNone(profile)
        self.assertFalse(await profile.is_filled)
        self.assertTrue(await profile.is_empty)
        await profile.adelete()
        with self.assertRaises(ObjectDoesNotExist):
            await ClientProfile.objects.aget(email=await profile.user_email)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(email=await profile.user_email)

    async def test_create_profiles(self):
        User = await self.get_user_model()
        profile_client, profile_expert = await self.create_test_profiles()
        self.assertEqual(await profile_client.user_email, self.emails["client"])
        self.assertEqual(await profile_expert.user_email, self.emails["expert"])
        speciality = await Speciality.objects.acreate(
            code=222, title="Medicine", is_medical=True
        )
        university = await University.objects.acreate(title="title", country="UA")
        education = await Education.objects.acreate(
            university=university, degree=Education.DegreeChoices.DOC,
            speciality=speciality, date_start="2024-05-19", date_end="2020-05-19"
        )
        await profile_expert.education.aadd(education)
        profile_education = await profile_expert.education.aget(id=education.id)
        self.assertIsNotNone(await profile_education.rel("university"))
        self.assertIsNotNone(await profile_education.rel("speciality"))
        for profile in (profile_client, profile_expert):
            self.assertIsNotNone(profile)
            self.assertFalse(await profile.is_filled)
            self.assertTrue(await profile.is_empty)
            await profile.adelete()
        with self.assertRaises(ObjectDoesNotExist):
            await ExpertProfile.objects.aget(email=profile_expert.email)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(email=profile_expert.email)
        with self.assertRaises(ObjectDoesNotExist):
            await ClientProfile.objects.aget(email=profile_client.email)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(email=profile_client.email)


# TODO: test async model props
class ContractTests(ProfileCreationMixin, TestCase):
    fixtures = ["subscription_plans"]
    async def test_contract_create(self):
        profile_client, profile_expert = await self.create_test_profiles()
        subscription_client = await SubscriptionPlan.objects.aget(id=1)
        subscription_expert = await SubscriptionPlan.objects.aget(id=2)
        contract = await TherapyContract.objects.acreate(
            client=profile_client,
            expert=profile_expert,
            client_plan=subscription_client,
            expert_plan=subscription_expert,
            client_plan_days=0,
            expert_plan_days=14
        )
        self.assertIsNotNone(contract)
        rel = await contract.rel("client")
        self.assertEqual(await rel.user_email, await profile_client.user_email)
        rel = await contract.rel("expert")
        self.assertEqual(await rel.user_email, await profile_expert.user_email)
        rel = await contract.rel("client_plan")
        self.assertEqual(await contract.rel("expert_plan"), subscription_expert)
        self.assertEqual(rel, subscription_client)
