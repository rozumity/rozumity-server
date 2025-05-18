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
        TherapyContractCreateView.as_view(),
        name='contracts'
    ),
    path(
        "contract/<int:pk>/",
        TherapyContractRetrieveUpdateView.as_view(),
        name='contract'
    )
]
