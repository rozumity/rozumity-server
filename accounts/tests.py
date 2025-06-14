from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from rozumity.mixins.testing_mixins import ProfileCreationMixin
from rozumity.utils import rel
from accounts.models import (
    ClientProfile, ExpertProfile, StaffProfile,
    TherapyContract, SubscriptionPlan
)
from educations.models import *


class AuthenticationTests(ProfileCreationMixin, TestCase):
    async def test_create_users(self):
        emails = self.get_emails()
        self.assertTrue(self.user_client.is_client)
        self.assertTrue(self.user_expert.is_expert)
        self.assertEqual(self.user_client.email, emails["client"])
        self.assertEqual(self.user_expert.email, emails["expert"])
        for user in (self.user_client, self.user_expert):
            self.assertTrue(user.is_active)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    async def test_create_superuser_profile(self):
        User = await sync_to_async(get_user_model)()
        admin_user = await sync_to_async(User.objects.create_superuser)(
            email="super@user.com", password="foo"
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertFalse(hasattr(admin_user, "username"))
        profile = await StaffProfile.objects.aget(user=admin_user)
        self.assertIsNotNone(profile)
        self.assertFalse(await profile.is_filled)
        self.assertTrue(await profile.is_empty)
        await profile.adelete()
        with self.assertRaises(ObjectDoesNotExist):
            await StaffProfile.objects.aget(user=profile.user)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(id=profile.user.id)

    async def test_create_profiles(self):
        User = await self.get_user_model()
        self.assertEqual(self.profile_client.id, self.user_client.id)
        self.assertEqual(self.profile_expert.id, self.user_expert.id)
        speciality = await Speciality.objects.acreate(
            code=222, title="Medicine", is_medical=True
        )
        university = await University.objects.acreate(title="title", country="UA")
        education = await Education.objects.acreate(
            university=university, degree=Education.DegreeChoices.DOC,
            speciality=speciality, date_start="2024-05-19", date_end="2020-05-19"
        )
        await self.profile_expert.education.aadd(education)
        profile_education = await self.profile_expert.education.aget(id=education.id)
        self.assertIsNotNone(await rel(profile_education, "university"))
        self.assertIsNotNone(await rel(profile_education, "speciality"))
        for profile in (self.profile_client, self.profile_expert):
            self.assertIsNotNone(profile)
            self.assertFalse(await profile.is_filled)
            self.assertTrue(await profile.is_empty)
            await profile.adelete()
        with self.assertRaises(ObjectDoesNotExist):
            await ExpertProfile.objects.aget(user=self.profile_expert.user)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(id=self.profile_expert.user.id)
        with self.assertRaises(ObjectDoesNotExist):
            await ClientProfile.objects.aget(user=self.profile_client.user)
        with self.assertRaises(ObjectDoesNotExist):
            await User.objects.aget(id=self.profile_client.user.id)


class ContractTests(ProfileCreationMixin, TestCase):
    fixtures = ["subscription_plans"]

    async def test_contract_create(self):
        subscription_client = await SubscriptionPlan.objects.aget(id=1)
        subscription_expert = await SubscriptionPlan.objects.aget(id=2)
        contract = await TherapyContract.objects.acreate(
            client=self.profile_client,
            expert=self.profile_expert,
            client_plan=subscription_client,
            expert_plan=subscription_expert,
            client_plan_days=0,
            expert_plan_days=14
        )
        self.assertIsNotNone(contract)
        self.assertEqual(await rel(contract, 'client_id'), self.profile_client.pk)
        self.assertEqual(await rel(contract, 'expert_id'), self.profile_expert.pk)
        self.assertEqual(await rel(contract, 'expert_plan_id'), subscription_expert.pk)
        self.assertEqual(await rel(contract, 'client_plan_id'), subscription_client.pk)
