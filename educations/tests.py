from django.test import TestCase
from django.urls import reverse
from rozumity.utils import rel
from rozumity.mixins.testing_mixins import ProfileCreationMixin
from educations.models import *


class EducationTests(ProfileCreationMixin, TestCase):
    fixtures = ['specialities_ukraine.json', 'universities_ukraine.json']
    async def test_create_profiles(self):
        speciality = await Speciality.objects.acreate(
            code=222, title="Medicine", is_medical=True
        )
        university = await University.objects.acreate(title="title", country="UA")
        education = await Education.objects.acreate(
            university=university, degree=Education.DegreeChoices.DOC,
            speciality=speciality, date_start="2024-05-19", date_end="2020-05-19"
        )
        university = await rel(education, "university")
        self.assertEqual(university.title, "title")
        self.assertEqual(university.country.code, "UA")

    async def test_university_list(self):
        response = await self.api_client.get(
            reverse("educations:universities-list"), 
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.text)

    async def test_university_detail(self):
        response = await self.api_client.get(
            reverse("educations:university-detail", args=[1]),
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.text)

    async def test_speciality_list(self):
        response = await self.api_client.get(
            reverse("educations:specialities-list"),
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("is_medical", response.text)

    async def test_speciality_detail(self):
        response = await self.api_client.get(
            reverse("educations:speciality-detail", args=[1]),
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("is_medical", response.text)

    async def test_education(self):
        data = {
            "client": self.profile_client.user_id,
            "university": 1, "speciality": 1,
            "degree": 5,
            "date_start": "2024-05-19",
            "date_end": "2025-05-19"
        }
        
        response = await self.api_client.post(
            reverse("educations:educations-list-create"), json=data,
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertIn(response.status_code, (200, 201))
        self.assertIn('"degree":5,', response.text)
        await self.profile_expert.education.aset([await Education.objects.aget(pk=response.json()["id"])])
        
        response = await self.api_client.get(
            reverse("educations:education-detail", args=[response.json()["id"]]),
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"degree":5,', response.text)

        response = await self.api_client.get(
            reverse("educations:educations-list-create"),
            headers={"Authorization": f"Bearer {self.token_expert}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"degree":5,', response.text)
