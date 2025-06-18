from django.urls import reverse
from django.test import TestCase
from rozumity.mixins.testing_mixins import APIClientTestMixin
from screening.models import *
from screening.views import *


class ScreeningClientTests(APIClientTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = QuestionaryCategory.objects.create(
            title='category 1', description='description 1'
        )
        cls.tag = TagScreening.objects.create(
            title='tag 1', description='description 1', color='#FFFFFF'
        )
        cls.questionary = Questionary.objects.create(
            title='questionary 1', description='description 1'
        )
        cls.questionary.categories.set([cls.category])
        cls.questionary.tags.set([cls.tag])
        cls.question = QuestionaryQuestion.objects.create(
            title='question 1', text='text 1', weight=1,
            questionary=cls.questionary,
        )
        cls.dimension = QuestionaryDimension.objects.create(
            title='dimension 1', description='description 1'
        )
        cls.dimension2 = QuestionaryDimension.objects.create(
            title='dimension 2', description='description 2'
        )
        cls.score1 = QuestionaryScore.objects.create(
            title='score1', description='desc', questionary=cls.questionary,
            dimension=cls.dimension, min_score=2, max_score=77
        )
        cls.score2 = QuestionaryScore.objects.create(
            title='score2', description='desc', questionary=cls.questionary,
            dimension=cls.dimension2, min_score=0, max_score=100
        )
        cls.score_extra = QuestionaryScoreExtra.objects.create(
            title='extra desc',
            description='Multidimensional score desc',
            questionary=cls.questionary
        )
        cls.score_extra.scores.set([cls.score1, cls.score2])
        cls.value = QuestionaryDimensionValue.objects.create(
            dimension=cls.dimension, value=5
        )
        cls.value2 = QuestionaryDimensionValue.objects.create(
            dimension=cls.dimension2, value=25
        )
        cls.answer = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 1'
        )
        cls.answer2 = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 2'
        )
        cls.answer.values.set([cls.value, cls.value2])

    async def test_category_tag(self):
        response = await self.api(
            "get", reverse("screening:questionaries-tags"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("tag 1", response.text)
        response = await self.api(
            "get", reverse("screening:questionaries-categories"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("category 1", response.text)

    async def test_questionary(self):
        response = await self.api(
            "get", reverse("screening:questionaries-questionaries"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)
        response = await self.api(
            "get", reverse("screening:questionaries-questionary", args=[self.questionary.pk]),
            {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

    async def test_answer(self):
        response = await self.api(
            "get", reverse("screening:questionaries-answers"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer 1", response.text)

    async def test_response(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-responses"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.text)
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"questionary":{"id":', response.text)
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_expert
        )
        self.assertEqual(response.status_code, 404)

    async def test_get_questionary_by_pk(self):
        response = getattr(await self.api(
            "get", "/api/screening/questionaries/questionary/999999/", token=self.token_client
        ), "json")()
        self.assertDictEqual({'detail': 'No Questionary matches the given query.'}, response)
        response = getattr(await self.api(
            "get", reverse("screening:questionaries-questionary", args=[self.questionary.id]), 
            token=self.token_client
        ), "json")()
        self.assertIn({
            'id': 1, 'title': 'category 1', 
            'description': 'description 1', 'is_active': True
        }, response["categories"])
        self.assertIn({
            'id': 1, 'title': 'tag 1', 'description': 'description 1', 
            'color': '#FFFFFF', 'is_active': True
        }, response["tags"])

    async def test_user_questionary_response_flow(self):
        response = await self.api(
            "get", reverse("screening:questionaries-questionaries"),
            {"categories": [99999], "tags":[99999]}, self.token_client
        )
        self.assertEqual(response.json()['results'], [])
        response = getattr(await self.api(
            "get", reverse("screening:questionaries-questionaries"), 
            {"categories": [self.category.id], "tags":[self.tag.id]}, self.token_client
        ), "json")()['results'][0]
        self.assertIn({
            'id': 1, 'title': 'category 1',
            'description': 'description 1', 'is_active': True
        }, response["categories"])
        self.assertIn({
            'id': 1, 'title': 'tag 1', 'description': 'description 1',
            'color': '#FFFFFF', 'is_active': True
        }, response["tags"])

        answers = [question["answers"][0] for question in response["questions"]]

        response = getattr(await self.api("post", reverse("screening:questionaries-responses"), {
            "client": str(self.profile_client.id),
            "questionary": response["id"],
            "answers": [answer["id"] for answer in answers]
        }, self.token_client), "json")()
        #raise ValueError(response)
