from django.urls import path,include
from screening.views import *
from screening import views
from rest_framework import routers

app_name = 'screening'

router = routers.DefaultRouter()
router.register(r"categories", views.CategoryQuestionaryListView, basename="questionaries-categories")
router.register(r"category", views.CategoryQuestionaryRetrieveView, basename="questionaries-category")
router.register(r"questionaries", views.QuestionaryListView, basename="questionaries-questionaries")
router.register(r"questionary", views.QuestionaryRetrieveView, basename="questionaries-questionary")
router.register(r"dimensions", views.QuestionaryDimensionListView, basename="questionaries-dimensions")
router.register(r"dimension", views.QuestionaryDimensionRetrieveView, basename="questionaries-dimension")
router.register(r"questions", views.QuestionaryQuestionListCreateView, basename="questionaries-questions")
router.register(r"question", views.QuestionaryQuestionRetrieveView, basename="questionaries-question")
router.register(r"answers", views.QuestionaryAnswerListCreateView, basename="questionaries-answers")
router.register(r"answer", views.QuestionaryAnswerRetrieveView, basename="questionaries-answer")
router.register(r"responses", views.QuestionaryResponseCreateView, basename="questionaries-responses")
router.register(r"response", views.QuestionaryResponseRetrieveUpdateView, basename="questionaries-response")

urlpatterns = [
    path("questionaries/", include(router.urls)),
]
