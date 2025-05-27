from uuid import uuid4
from django.test import TestCase
from rozumity.mixins.testing_mixins import ProfileCreationMixin
from rozumity.utils import rel
from screening.models import *
from screening.views import *


class ScreeningCreationTests(ProfileCreationMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.category = CategoryQuestionary.objects.create(
            title='category 1', description='description 1'
        )
        cls.questionary = Questionary.objects.create(
            title='questionary 1', description='description 1',
            category = cls.category
        )
        cls.question = QuestionaryQuestion.objects.create(
            title='question 1', text='text 1', weight=0.2,
            questionary=cls.questionary,
        )
        cls.dimension = QuestionaryDimension.objects.create(
            title='dimension 1', description='description 1'
        )
        cls.answer = QuestionaryAnswer.objects.create(
            question=cls.question, dimension=cls.dimension,
            title='answer 1', value=5
        )
        cls.score1 = QuestionaryScore.objects.create(
            dimension=cls.dimension, max_score=49
        )
        cls.score2 = QuestionaryScore.objects.create(
            dimension=cls.dimension, min_score=50
        )
        cls.result = QuestionaryResult.objects.create(
            title='result 1', description='description 1',
            questionary=cls.questionary
        )
        cls.result.scores.set([cls.score1, cls.score2])

    def setUp(self):
        super().setUp()
        self.response = QuestionaryResponse.objects.create(
            client=self.profile_client, result=self.result
        )
        self.response.answers.set([self.answer])

    async def test_create_questionary(self):
        self.assertEqual(self.questionary.category.title, self.category.title)
        question_test = await self.questionary.questions.aget()
        self.assertEqual(question_test.title, self.question.title)
        answer_test = await rel(self.dimension, 'answers')
        answer_test = await answer_test.aget()
        self.assertEqual(answer_test.title, answer_test.title)
        dimension_test = await rel(answer_test, 'dimension')
        self.assertEqual(dimension_test.title, self.dimension.title)
        result_test = await rel(self.response, 'result')
        self.assertEqual(result_test.title, self.result.title)
        score = await result_test.scores.aget(dimension=self.dimension, min_score=0)
        self.assertEqual(score.min_score, self.score1.min_score)
        self.assertEqual(score.max_score, self.score1.max_score)
        response_test = await result_test.responses.aget()
        self.assertIsInstance(response_test.id, type(uuid4()))
        self.assertEqual(score.max_score, self.score1.max_score)

    async def test_category_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/categories/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("category 1", response.text)

    async def test_questionary_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/questionaries/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

    async def test_questionary_detail(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/questionary/{self.questionary.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("questionary 1", response.text)

    async def test_dimension_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/dimensions/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dimension 1", response.text)

    async def test_dimension_detail(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/dimension/{self.dimension.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dimension 1", response.text)

    async def test_question_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/questions/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("question 1", response.text)

    async def test_question_detail(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/question/{self.question.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("question 1", response.text)

    async def test_answer_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/answers/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer 1", response.text)

    async def test_answer_detail(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/answer/{self.answer.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer 1", response.text)

    async def test_response_detail(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("result 1", response.text)

    async def test_response_detail_forbidden(self):
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                headers={"Authorization": f"Bearer {self.token_expert}"}
            )
        self.assertEqual(response.status_code, 403)
