from uuid import uuid4
from django.test import TestCase
from rozumity.mixins.testing_mixins import ProfileCreationMixin
from rozumity.utils import rel
from screening.models import *


class ScreeningCreationTests(ProfileCreationMixin, TestCase):
    async def test_create_questionary(self):
        category = await CategoryQuestionary.objects.acreate(
            title='category 1', description='description 1'
        )
        questionary = await Questionary.objects.acreate(
            title='questionary 1', description='description 1',
            category = category
        )
        question = await QuestionaryQuestion.objects.acreate(
            title='question 1', text='text 1', weight=0.2,
            questionary=questionary,
        )
        dimension = await QuestionaryDimension.objects.acreate(
            title='dimension 1', description='description 1'
        )
        answer = await QuestionaryAnswer.objects.acreate(
            question=question, dimension=dimension,
            title='answer 1', value=5
        )
        score1 = await QuestionaryScore.objects.acreate(
            dimension=dimension, max_score=49
        )
        score2 = await QuestionaryScore.objects.acreate(
            dimension=dimension, min_score=50
        )
        result = await QuestionaryResult.objects.acreate(
            title='result 1', description='description 1',
            questionary=questionary
        )
        await result.scores.aset([score1, score2])
        response = await QuestionaryResponse.objects.acreate(
            client=await self.create_test_client(), result=result
        )
        await response.answers.aset([answer])

        category_test = questionary.category
        self.assertEqual(category_test.title, category.title)
        question_test = await questionary.questions.aget()
        self.assertEqual(question_test.title, question.title)
        answer_test = await rel(dimension, 'answers')
        answer_test = await answer_test.aget()
        self.assertEqual(answer_test.title, answer_test.title)
        dimension_test = await rel(answer_test, 'dimension')
        self.assertEqual(dimension_test.title, dimension.title)
        result_test = await rel(response, 'result')
        self.assertEqual(result_test.title, result.title)
        score = await result_test.scores.aget(dimension=dimension, min_score=0)
        self.assertEqual(score.min_score, score1.min_score)
        self.assertEqual(score.max_score, score1.max_score)
        response_test = await result_test.responses.aget()
        self.assertIsInstance(response_test.id, type(uuid4()))
        self.assertEqual(score.max_score, score1.max_score)
