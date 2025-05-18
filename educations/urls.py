from django.urls import path
from educations.views import *

app_name = 'educations'

urlpatterns = [
    path(
        "educations/",
        EducationCreateView.as_view(),
        name='educations'
    ),
    path(
        "education/<int:pk>/",
        EducationRetrieveUpdateView.as_view(),
        name='education'
    ),
    path(
        "universities/",
        UniversityListView.as_view(),
        name='universities'
    ),
    path(
        "university/<int:pk>/",
        UniversityRetrieveView.as_view(),
        name='university'
    ),
    path(
        "speciality/<int:pk>/",
        SpecialityRetrieveView.as_view(),
        name='speciality'
    ),
    path(
        "specialities/",
        SpecialityListView.as_view(),
        name='speciality'
    ),
]
