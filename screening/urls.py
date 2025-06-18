from django.urls import path
from screening.views import *
from screening import views

app_name = 'screening'

urlpatterns = [
    path("questionaries/tags/", views.TagScreeningReadOnlyViewSet.as_view({'get': 'alist'}), name="questionaries-tags"),
    path("questionaries/tag/<int:pk>/", views.TagScreeningReadOnlyViewSet.as_view({'get': 'aretrieve'}), name="questionaries-tag"),
    path("questionaries/categories/", views.QuestionaryCategoryReadOnlyViewSet.as_view({'get': 'alist'}), name="questionaries-categories"),
    path("questionaries/category/<int:pk>/", views.QuestionaryCategoryReadOnlyViewSet.as_view({'get': 'aretrieve'}), name="questionaries-category"),
    path("questionaries/questionaries/", views.QuestionaryReadOnlyViewSet.as_view({'get': 'alist'}), name="questionaries-questionaries"),
    path("questionaries/questionary/<int:pk>/", views.QuestionaryReadOnlyViewSet.as_view({'get': 'aretrieve'}), name="questionaries-questionary"),
    path("questionaries/answers/", views.QuestionaryAnswerReadOnlyViewSet.as_view({'get': 'alist'}), name="questionaries-answers"),
    path("questionaries/responses/", views.QuestionaryResponseViewSet.as_view({'get': 'alist','post': 'acreate'}), name="questionaries-responses"),
    path("questionaries/response/<uuid:pk>/", views.QuestionaryResponseViewSet.as_view({'get': 'aretrieve','put': 'aupdate','patch': 'partial_aupdate'}), name="questionaries-response")
]
