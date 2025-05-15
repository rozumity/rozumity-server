from django.urls import path
from accounts.views import *


app_name = 'accounts'

urlpatterns = [
    path(
        "users/",
        UserListView.as_view(),
        name='users'
    ),
    path(
        "user/<uuid:pk>/",
        UserRetrieveView.as_view(),
        name='user'
    ),
    path(
        "education/educations/",
        EducationListCreateView.as_view(),
        name='educations'
    ),
    path(
        "education/education/<int:pk>/",
        EducationRetrieveUpdateDestroyView.as_view(),
        name='education'
    ),
    path(
        "education/universities/",
        UniversityListView.as_view(),
        name='universities'
    ),
    path(
        "education/university/<int:pk>/",
        UniversityRetrieveView.as_view(),
        name='university'
    ),
    path(
        "education/speciality/<int:pk>/",
        SpecialityRetrieveView.as_view(),
        name='speciality'
    ),
    path(
        "education/specialities/",
        SpecialityListView.as_view(),
        name='speciality'
    ),
    path(
        "profile/client/<str:pk>/",
        ClientProfileRetrieveUpdateView.as_view(),
        name='client-profile'
    ),
    path(
        "profile/expert/<str:pk>/",
        ExpertProfileRetrieveUpdateView.as_view(),
        name='expert-profile'
    ),
    path(
        "subscriptions/",
        SubscriptionPlanListView.as_view(),
        name='subscriptions'
    ),
    path(
        "subscription/<int:pk>/",
        SubscriptionPlanRetrieveView.as_view(),
        name='subscription'
    ),
    path(
        "contracts/",
        TherapyContractCreateListView.as_view(),
        name='contracts'
    ),
    path(
        "contract/<int:pk>/",
        TherapyContractRetrieveUpdateView.as_view(),
        name='contract'
    )
]
