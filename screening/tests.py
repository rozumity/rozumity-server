from django.urls import reverse
from django.test import TestCase
from django.core.cache import cache
from rozumity.mixins.testing_mixins import APIClientTestMixin
from screening.models import *
from screening.views import *


class ScreeningClientTests(APIClientTestMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = CategoryScreening.objects.create(
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
        cls.question2 = QuestionaryQuestion.objects.create(
            title='question 2', text='text 2', weight=1,
            questionary=cls.questionary,
        )
        cls.answer = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 1'
        )
        cls.answer2 = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 2'
        )
        cls.answer3 = QuestionaryAnswer.objects.create(
            question=cls.question2, title='answer 3'
        )
        cls.answer4 = QuestionaryAnswer.objects.create(
            question=cls.question2, title='answer 4'
        )
        cls.dimension = QuestionaryDimension.objects.create(
            title='dimension 1', description='description 1'
        )
        cls.dimension2 = QuestionaryDimension.objects.create(
            title='dimension 2', description='description 2'
        )
        QuestionaryDimensionValue.objects.bulk_create([
            QuestionaryDimensionValue(answer=cls.answer, dimension=cls.dimension, value=5),
            QuestionaryDimensionValue(answer=cls.answer, dimension=cls.dimension2, value=25),
            QuestionaryDimensionValue(answer=cls.answer2, dimension=cls.dimension, value=4),
            QuestionaryDimensionValue(answer=cls.answer3, dimension=cls.dimension2, value=6),
            QuestionaryDimensionValue(answer=cls.answer4, dimension=cls.dimension2, value=10),
        ])
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
        cls.score_extra.scores.set([cls.score1])

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

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

    async def test_response(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-responses"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"questionary":1', response.text)
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"questionary":1', response.text)
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        response = await self.api(
            "get", reverse("screening:questionaries-response", args=[self.response.pk]),
            {}, self.token_expert
        )
        self.assertEqual(response.status_code, 403)

    async def test_get_questionary(self):
        response = await self.api(
            "get", reverse("screening:questionaries-questionaries"), {}, self.token_client
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

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
        ),"json")()['results'][0]
        self.assertIn({
            'id': 1, 'title': 'category 1',
            'description': 'description 1', 'is_active': True
        }, response["categories"])
        self.assertIn({
            'id': 1, 'title': 'tag 1', 'description': 'description 1',
            'color': '#FFFFFF', 'is_active': True
        }, response["tags"])

        answers = [question["answers"][0]["id"] for question in response["questions"]]
        response = getattr(await self.api(
            "post", reverse("screening:questionaries-responses"), {
                "client": str(self.profile_client.id),
                "questionary": response["id"]
            }, self.token_client
        ), "json")()
        self.assertTrue(await getattr(await QuestionaryResponse.objects.aget(id=response["id"]), 'ais_empty'))

        response = getattr(await self.api(
            "patch", reverse(
                "screening:questionaries-response", 
                args=[response["id"]]
            ), {"answers": answers[0:1]}, self.token_client
        ), "json")()
        self.assertFalse(await getattr(await QuestionaryResponse.objects.aget(id=response["id"]), 'ais_empty'))
        self.assertFalse(response["is_filled"])
        self.assertEqual(len(response["answers"]), 1)

        response = getattr(await self.api(
            "patch", reverse(
                "screening:questionaries-response", 
                args=[response["id"]]
            ), {"answers": answers}, self.token_client
        ), "json")()
        self.assertTrue(response["is_filled"])
        self.assertEqual(len(response["answers"]), 0)
        scores_map = getattr(await QuestionaryResponse.objects.aget(id=response["id"]), 'scores_map')
        scores_map_test = {
            str(self.dimension.id): 0, str(self.dimension2.id): 0
        }
        async for dim in self.answer.dimension_values.all():
            scores_map_test[str(dim.dimension_id)] += dim.value
        async for dim in self.answer3.dimension_values.all():
            scores_map_test[str(dim.dimension_id)] += dim.value
        self.assertListEqual(list(scores_map.keys()), list(scores_map_test.keys()))
        self.assertListEqual(list(scores_map.values()), list(scores_map_test.values()))

        response = getattr(await self.api(
            "get", reverse(
                "screening:questionaries-response", 
                args=[response['id']]
            ), token=self.token_client
        ), "json")()
        self.assertEqual(response['scores'][0]['id'], self.score1.id)
        self.assertEqual(response['scores_extra'][0]['id'], self.score_extra.id)
