from django.test import TestCase

# Create your tests here.
# python manage.py test educations
from django.test import TestCase
from educations.models import *


class EducationTests(TestCase):
    async def test_create_profiles(self):
        speciality = await Speciality.objects.acreate(
            code=222, title="Medicine", is_medical=True
        )
        university = await University.objects.acreate(title="title", country="UA")
        education = await Education.objects.acreate(
            university=university, degree=Education.DegreeChoices.DOC,
            speciality=speciality, date_start="2024-05-19", date_end="2020-05-19"
        )
        university = await education.rel("university")
        self.assertEqual(university.title, "title")
        self.assertEqual(university.country.code, "UA")
