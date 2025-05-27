from django.urls import path
from screening.views import *
from django.urls import path
from screening.views import *

app_name = 'screening'

urlpatterns = [
    path(
        "questionaries/categories/",
        CategoryQuestionaryListView.as_view(),
        name="questionaries-categories"
    ),
    path(
        "questionaries/category/<int:pk>/",
        CategoryQuestionaryRetrieveView.as_view(),
        name="questionaries-category"),
    path(
        "questionaries/questionaries/",
        QuestionaryListView.as_view(),
        name="questionaries-questionaries"),
    path(
        "questionaries/questionary/<int:pk>/",
        QuestionaryRetrieveView.as_view(),
        name="questionaries-questionary"),
    path(
        "questionaries/dimensions/",
        QuestionaryDimensionListView.as_view(),
        name="questionaries-dimensions"),
    path(
        "questionaries/dimension/<int:pk>/",
        QuestionaryDimensionRetrieveView.as_view(),
        name="questionaries-dimension"),
    path(
        "questionaries/questions/",
        QuestionaryQuestionListCreateView.as_view(),
        name="questionaries-questions"
    ),
    path(
        "questionaries/question/<int:pk>/",
        QuestionaryQuestionRetrieveView.as_view(),
        name="questionaries-question"
    ),
    path(
        "questionaries/answers/",
        QuestionaryAnswerListCreateView.as_view(), 
        name="questionaries-answers"
    ),
    path(
        "questionaries/answer/<int:pk>/",
        QuestionaryAnswerRetrieveView.as_view(),
        name="questionaries-answer"
    ),
    path(
        "questionaries/responses/",
        QuestionaryResponseCreateView.as_view(),
        name="questionaries-responses"
    ),
    path(
        "questionaries/response/<uuid:pk>/",
        QuestionaryResponseRetrieveUpdateView.as_view(),
        name="questionaries-response"
    ),
]