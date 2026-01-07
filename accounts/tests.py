from django.test import TestCase
from rozumity.utils import ProfileCreationMixin
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from accounts.models import (
    StaffProfile, TherapyContract, SubscriptionPlan,
    Speciality, University, Education
)

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
            univ = await University.objects.acreate(title="Super University", country="UA")

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


# class EducationTests(TestCase):
#     fixtures = ['specialities_ukraine.json', 'universities_ukraine.json', 'users.json', 'subscription_plans.json']

#     async def test_create_profiles(self):
#         speciality = await Speciality.objects.acreate(
#             code=222, title="Medicine", is_medical=True
#         )
#         university = await University.objects.acreate(title="title", country="UA")
#         education = await Education.objects.acreate(
#             university=university, degree=Education.DegreeChoices.DOC,
#             speciality=speciality, date_start="2024-05-19", date_end="2020-05-19"
#         )
#         university = await rel(education, "university")
#         self.assertEqual(university.title, "title")
#         self.assertEqual(university.country.code, "UA")

#     async def test_university_list(self):
#         response = await self.api_client.get(
#             reverse("educations:universities"), 
#             headers={"Authorization": f"Bearer {self.token_expert}"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("title", response.text)

#     async def test_university_detail(self):
#         response = await self.api_client.get(
#             reverse("educations:university", args=[1]),
#             headers={"Authorization": f"Bearer {self.token_expert}"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("title", response.text)

#     async def test_speciality_list(self):
#         response = await self.api_client.get(
#             reverse("educations:specialities"),
#             headers={"Authorization": f"Bearer {self.token_expert}"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("is_medical", response.text)

#     async def test_speciality_detail(self):
#         response = await self.api_client.get(
#             reverse("educations:speciality", args=[1]),
#             headers={"Authorization": f"Bearer {self.token_expert}"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("is_medical", response.text)

#     async def test_education(self):
#         data = {
#             "university": 1, "speciality": 1, "degree": 5,
#             "date_start": "2024-05-19",
#             "date_end": "2025-05-19"
#         }
        
#         response = await self.api("post", reverse("educations:educations"), data, self.token_expert)
#         self.assertIn(response.status_code, (200, 201))
#         self.assertIn('"degree":5,', response.text)
#         await self.profile_expert.education.aset([await Education.objects.aget(pk=response.json()["id"])])
        
#         response = await self.api_client.get(
#             reverse("educations:education", args=[response.json()["id"]]),
#             headers={"Authorization": f"Bearer {self.token_expert}"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('"degree":5,', response.text)
