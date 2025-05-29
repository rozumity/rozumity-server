from django.urls import path
from educations import views

app_name = 'educations'

urlpatterns = [
    path("educations/", views.EducationListCreateView.as_view(), name="educations-list-create"),
    path("education/<int:pk>/", views.EducationRetrieveUpdateView.as_view(), name="education-detail"),
    path("universities/", views.UniversityListView.as_view(), name="universities-list"),
    path("university/<int:pk>/", views.UniversityRetrieveView.as_view(), name="university-detail"),
    path("specialities/", views.SpecialityListView.as_view(), name="specialities-list"),
    path("speciality/<int:pk>/", views.SpecialityRetrieveView.as_view(), name="speciality-detail"),
]
