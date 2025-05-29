from django.urls import path
from screening.views import *
from screening import views

app_name = 'screening'

urlpatterns = [
    path("questionaries/categories/", views.CategoryQuestionaryListView.as_view(), name="questionaries-categories"),
    path("questionaries/category/<int:pk>/", views.CategoryQuestionaryRetrieveView.as_view(), name="questionaries-category"),
    path("questionaries/questionaries/", views.QuestionaryListView.as_view(), name="questionaries-questionaries"),
    path("questionaries/questionary/<int:pk>/", views.QuestionaryRetrieveView.as_view(), name="questionaries-questionary"),
    path("questionaries/dimensions/", views.QuestionaryDimensionListView.as_view(), name="questionaries-dimensions"),
    path("questionaries/dimension/<int:pk>/", views.QuestionaryDimensionRetrieveView.as_view(), name="questionaries-dimension"),
    path("questionaries/questions/", views.QuestionaryQuestionListView.as_view(), name="questionaries-questions"),
    path("questionaries/question/<int:pk>/", views.QuestionaryQuestionRetrieveView.as_view(), name="questionaries-question"),
    path("questionaries/answers/", views.QuestionaryAnswerListCreateView.as_view(), name="questionaries-answers"),
    path("questionaries/answer/<int:pk>/", views.QuestionaryAnswerRetrieveView.as_view(), name="questionaries-answer"),
    path("questionaries/responses/", views.QuestionaryResponseListCreateView.as_view(), name="questionaries-responses"),
    path("questionaries/response/<uuid:pk>/", views.QuestionaryResponseRetrieveUpdateView.as_view(), name="questionaries-response"),
]
