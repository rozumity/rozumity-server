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
        cls.value = QuestionaryAnswerValue.objects.create(
            dimension=cls.dimension, value=5
        )
        cls.value2 = QuestionaryAnswerValue.objects.create(
            dimension=cls.dimension2, value=25
        )
        cls.answer = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 1'
        )
        cls.answer2 = QuestionaryAnswer.objects.create(
            question=cls.question, title='answer 2'
        )
        cls.answer.values.set([cls.value, cls.value2])
        cls.score1 = QuestionaryScore.objects.create(
            dimension=cls.dimension, min_score=2, max_score=77
        )
        cls.score2 = QuestionaryScore.objects.create(
            dimension=cls.dimension2, min_score=0, max_score=100
        )
        cls.result = QuestionaryResult.objects.create(
            title='result 1', description='description 1',
            questionary=cls.questionary
        )
        cls.result.scores.set([cls.score1, cls.score2])

    async def test_create_questionary(self):
        question_test = await self.questionary.questions.aget()
        self.assertEqual(question_test.title, self.question.title)
        dimension_test = await rel(self.value, 'dimension')
        self.assertEqual(dimension_test.title, self.dimension.title)
        score = await self.result.scores.aget(dimension=self.dimension)
        self.assertEqual(score.min_score, self.score1.min_score)
        self.assertEqual(score.max_score, self.score1.max_score)

    # Category
    async def test_category_list(self):
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/categories/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("category 1", response.text)

    # Questionary
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

    # Dimension
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

    # Question
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

    # Answer
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

    # Response
    async def test_response_list(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        async with self.api_client as ac:
            response = await ac.get(
                "/api/screening/questionaries/responses/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.text)

    async def test_response_detail(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn('"client":"client@user.com",', response.text)

    async def test_response_detail_forbidden(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        async with self.api_client as ac:
            response = await ac.get(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                headers={"Authorization": f"Bearer {self.token_expert}"}
            )
        self.assertEqual(response.status_code, 403)

    async def test_response_update_put(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        new_result = await QuestionaryResult.objects.acreate(
            title='result 2', description='desc 2',
            questionary=self.questionary
        )
        async with self.api_client as ac:
            response = await ac.put(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                json={"result": new_result.pk, "client": self.profile_client.pk},
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        self.assertEqual(response.status_code, 400)

    async def test_response_update_answers_patch(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        new_answer = await QuestionaryAnswer.objects.acreate(
            question=self.question, title='answer 1'
        )
        new_value = await QuestionaryAnswerValue.objects.acreate(
            dimension=self.dimension2, value=100
        )
        await new_answer.values.aset([self.value, new_value])
        await self.response.answers.aset([new_answer])
        
        self.assertIsNone(await rel(self.response, 'result'))
        async with self.api_client as ac:
            response = await ac.patch(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                json={"answers": [self.answer.pk]},
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        updated_response = await QuestionaryResponse.objects.aget(pk=self.response.pk)
        self.assertIsNone(await rel(updated_response, 'result'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("created_at", response.text)

    async def test_response_update_answers_result_patch(self):
        self.response = await QuestionaryResponse.objects.acreate(
            client=self.profile_client, questionary=self.questionary
        )
        new_result = await QuestionaryResult.objects.acreate(
            title='result 2', description='description 2',
            questionary=self.questionary
        )
        new_score = await QuestionaryScore.objects.acreate(
            dimension=self.dimension2, min_score=1, max_score=2
        )
        await new_result.scores.aset([self.score1, new_score])
        self.assertIsNone(await rel(self.response, 'result'))
        async with self.api_client as ac:
            response = await ac.patch(
                f"/api/screening/questionaries/response/{self.response.pk}/",
                json={"answers": [self.answer.pk]},
                headers={"Authorization": f"Bearer {self.token_client}"}
            )
        updated_response = await QuestionaryResponse.objects.aget(pk=self.response.pk)
        self.assertEqual(getattr(await rel(updated_response, 'result'), 'pk'), self.result.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn("created_at", response.text)
