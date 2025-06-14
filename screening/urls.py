from django.urls import path
from screening.views import *
from screening import views

app_name = 'screening'

urlpatterns = [
    path("questionaries/categories/", views.QuestionaryCategoryListView.as_view(), name="questionaries-categories"),
    path("questionaries/category/<int:pk>/", views.QuestionaryCategoryRetrieveView.as_view(), name="questionaries-category"),
    path("questionaries/questionaries/", views.QuestionaryListView.as_view(), name="questionaries-questionaries"),
    path("questionaries/questionary/<int:pk>/", views.QuestionaryRetrieveView.as_view(), name="questionaries-questionary"),
    path("questionaries/answers/", views.QuestionaryAnswerListView.as_view(), name="questionaries-answers"), 
    path("questionaries/responses/", views.QuestionaryResponseListCreateView.as_view(), name="questionaries-responses"),
    path("questionaries/response/<uuid:pk>/", views.QuestionaryResponseRetrieveUpdateView.as_view(), name="questionaries-response"),

    path("surveys/", views.SurveyListView.as_view(), name="surveys-list"),
    path("survey/<int:pk>/", views.SurveyRetrieveView.as_view(), name="survey-detail"),
    path("surveythemes/", views.SurveyThemeListCreateView.as_view(), name="surveythemes-list"),
    path("surveytheme/<int:pk>/", views.SurveyThemeRetrieveUpdateDestroyView.as_view(), name="surveytheme-detail"),
    path("surveyresults/", views.SurveyResultCreateView.as_view(), name="surveyresults-create"),
    path("surveyresult/<int:pk>/", views.SurveyResultRetrieveUpdateView.as_view(), name="surveyresult-detail"),
    path("surveyentries/", views.SurveyEntryCreateView.as_view(), name="surveyentries-create"),
    path("surveyentry/<int:pk>/", views.SurveyEntryRetrieveUpdateDestroyView.as_view(), name="surveyentry-detail"),
    path("tags/", views.TagScreeningListView.as_view(), name="tags-list"),
    path("tag/<int:pk>/", views.TagScreeningRetrieveView.as_view(), name="tag-detail"),
]
