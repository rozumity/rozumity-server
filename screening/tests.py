from django.urls import reverse
from django.test import TestCase
from rozumity.mixins.testing_mixins import APIClientTestMixin
from screening.models import *
from screening.views import *


async def get_data(serializer):
    """Use adata if the serializer supports it, data otherwise."""
    return await serializer.adata if hasattr(serializer, "adata") else serializer.data


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

    # Category
    async def test_category_list(self):
        response = await self.api(
            "get", reverse("screening:questionaries-categories"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("category 1", response.text)

    # Questionary
    async def test_questionary_list(self):
        response = await self.api(
            "get", reverse("screening:questionaries-questionaries"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

    async def test_questionary_detail(self):
        response = await self.api(
            "get", reverse("screening:questionaries-questionary", args=[self.questionary.pk]),
            {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

    # Answer
    async def test_answer_list(self):
        response = await self.api(
            "get", reverse("screening:questionaries-answers"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer 1", response.text)

    # Response
    async def test_response_list(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-responses"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.text)

    async def test_response_detail(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"questionary":{"id":', response.text)

    async def test_response_detail_forbidden(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_expert
        )
        self.assertEqual(response.status_code, 404)

    async def test_get_questionaries_by_category_tag(self):
        responses = [
            await self.api(
                "get", reverse("screening:questionaries-questionaries"), 
                {"categories": [self.category.id], "tags":[self.tag.id]},
                self.token_client
            ),
            await self.api(
                "get", reverse("screening:questionaries-questionaries"),
                {"categories": [99999], "tags":[99999]},
                self.token_client
            )
        ]
        response_ok = responses[0].json()['results'][0]
        response_empty = responses[1].json()['results']
        self.assertIn({
            'id': 1, 'title': 'category 1', 'description': 'description 1', 'is_active': True
        }, response_ok["categories"])
        self.assertIn({
            'id': 1, 'title': 'tag 1', 'description': 'description 1', 'color': '#FFFFFF', 'is_active': True
        }, response_ok["tags"])
        self.assertEqual(response_empty, [])


    async def test_get_questionary_by_id(self):
        responses = [
            await self.api(
                "get", reverse("screening:questionaries-questionary", args=[self.questionary.id]), token=self.token_client
            ),
            await self.api(
                "get", "/api/screening/questionaries/questionary/999999/", token=self.token_client
            ),
        ]
        response_ok = responses[0].json()
        response_fail = responses[1]
        self.assertIn({
            'id': 1, 'title': 'category 1', 'description': 'description 1', 'is_active': True
        }, response_ok["categories"])
        self.assertIn({
            'id': 1, 'title': 'tag 1', 'description': 'description 1', 'color': '#FFFFFF', 'is_active': True
        }, response_ok["tags"])
        self.assertDictEqual({'detail': 'No Questionary matches the given query.'}, response_fail.json())
