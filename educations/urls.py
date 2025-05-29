from django.urls import path, include
from rest_framework import routers
from educations import views

app_name = 'educations'

router = routers.DefaultRouter()
router.register(r'educations', views.EducationListCreateView, basename='educations')
router.register(r'education', views.EducationRetrieveUpdateView, basename='education')
router.register(r'universities', views.UniversityListView, basename='universities')
router.register(r'university', views.UniversityRetrieveView, basename='university')
router.register(r'specialities', views.SpecialityListView, basename='specialities')
router.register(r'speciality', views.SpecialityRetrieveView, basename='speciality')

urlpatterns = [
    path("", include(router.urls)),
]
