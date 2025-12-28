from django.test import TestCase
from rozumity.mixins.testing_mixins import ProfileCreationMixin
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import (
    StaffProfile, TherapyContract, SubscriptionPlan
)
from educations.models import Speciality, University, Education

User = get_user_model()


class AuthenticationTests(ProfileCreationMixin, TestCase):
    
    async def test_create_users(self):
        self.assertTrue(self.u_client.is_client)
        self.assertTrue(self.u_expert.is_expert)
        self.assertEqual(self.u_client.email, "client@user.com")
    
        self.assertTrue(self.u_client.is_active)
        self.assertFalse(self.u_client.is_staff)

    async def test_create_superuser_profile(self):
        admin_user = await sync_to_async(User.objects.create_superuser)(
            email="super@user.com", password="foo"
        )
        
        self.assertTrue(admin_user.is_superuser)

        profile = await StaffProfile.objects.aget(user=admin_user)
        self.assertIsNotNone(profile)

        self.assertTrue(await profile.is_empty)
        
        await profile.adelete()
        with self.assertRaises(ObjectDoesNotExist):
            await StaffProfile.objects.aget(user=admin_user)

    async def test_create_profiles(self):
            spec = await Speciality.objects.acreate(code=222, title="Medicine", is_medical=True)
            univ = await University.objects.acreate(title="title", country="UA")

            edu = await Education.objects.acreate(
                university=univ, 
                degree=Education.DegreeChoices.DOC,
                speciality=spec, 
                date_start="2024-05-19", 
                date_end="2020-05-19"
            )

            await self.p_expert.education.aadd(edu)

            exists = await self.p_expert.education.filter(id=edu.id).aexists()
            self.assertTrue(exists)

            user_id = self.u_expert.id

            await self.p_expert.adelete()

            with self.assertRaises(ObjectDoesNotExist):
                await User.objects.aget(id=user_id)

class ContractTests(ProfileCreationMixin, TestCase):
    fixtures = ["subscription_plans.json"]

    async def test_contract_create(self):
        sub_client = await SubscriptionPlan.objects.aget(id=1)
        sub_expert = await SubscriptionPlan.objects.aget(id=2)
        
        contract = await TherapyContract.objects.acreate(
            client=self.p_client,
            expert=self.p_expert,
            client_plan=sub_client,
            expert_plan=sub_expert,
            client_plan_days=0,
            expert_plan_days=14
        )
        
        self.assertIsNotNone(contract.id)
        self.assertEqual(contract.client_id, self.p_client.pk)
        self.assertEqual(contract.expert_id, self.p_expert.pk)
