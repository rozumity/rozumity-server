from django.urls import path
from educations import views

app_name = 'educations'

urlpatterns = [
    path("educations/", views.EducationViewSet.as_view({'get': 'alist', 'post': 'acreate'}), name="educations"),
    path("education/<int:pk>/", views.EducationViewSet.as_view({'get': 'aretrieve','put': 'aupdate','patch': 'partial_aupdate'}), name="education"),
    path("universities/", views.UniversityReadOnlyViewSet.as_view({'get': 'alist'}), name="universities"),
    path("university/<int:pk>/", views.UniversityReadOnlyViewSet.as_view({'get': 'aretrieve'}), name="university"),
    path("specialities/", views.SpecialityReadOnlyViewSet.as_view({'get': 'alist'}), name="specialities"),
    path("speciality/<int:pk>/", views.SpecialityReadOnlyViewSet.as_view({'get': 'aretrieve'}), name="speciality"),
]
