from django.urls import path
from accounts.views import *


app_name = 'accounts'

urlpatterns = [
    path(
        "user/<int:pk>",
        UserRetrieveUpdateView.as_view(),
        name='user'
    ),
    path(
        "users/",
        UserListView.as_view(),
        name='users'
    ),
    path(
        "education/<int:pk>",
        EducationRetrieveUpdateDestroyView.as_view(),
        name='education'
    ),
    path(
        "educations/",
        EducationListCreateView.as_view(),
        name='educations'
    ),
    path(
        "education/university/<int:pk>",
        UniversityRetrieveUpdateDestroyView.as_view(),
        name='university'
    ),
    path(
        "education/universities/",
        UniversityListCreateView.as_view(),
        name='universities'
    ),
    path(
        "education/speciality/<int:pk>",
        SpecialityRetrieveUpdateDestroyView.as_view(),
        name='speciality'
    ),
    path(
        "education/specialities/",
        SpecialityListCreateView.as_view(),
        name='speciality'
    ),
    path(
        "profile/client/<int:pk>",
        ClientProfileRetrieveUpdateView.as_view(),
        name='client-profile'
    ),
    path(
        "profile/clients",
        ClientProfileListView.as_view(),
        name='client-profiles'
    ),
    path(
        "profile/expert/<int:pk>",
        ExpertProfileRetrieveUpdateView.as_view(),
        name='expert-profile'
    ),
    path(
        "profile/experts",
        ExpertProfileListView.as_view(),
        name='expert-profiles'
    ),
    path(
        "subscription/<int:pk>",
        SubscriptionPlanRetrieveUpdateDestroyView.as_view(),
        name='subscription'
    ),
    path(
        "subscriptions",
        SubscriptionPlanListCreateView.as_view(),
        name='subscriptions'
    ),
#    path(
#        "diary/<int:pk>",
#        DiaryRetrieveUpdateDestroyView.as_view(),
#        name='diary'),
#    path(
#        "diaries",
#        DiaryListCreateView.as_view(),
#        name='diaries'
#    )
]
