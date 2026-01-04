from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path("users/", views.UserViewSet.as_view({'get': 'alist'}), name="user-list"),
    path("users/<uuid:pk>/", views.UserViewSet.as_view({'get': 'aretrieve'}), name="user-detail"),

    path("subscription-plans/", views.SubscriptionPlanViewSet.as_view({'get': 'list'}), name="subscription-plan-list"),
    path("subscription-plans/<uuid:pk>/", views.SubscriptionPlanViewSet.as_view({'get': 'retrieve'}), name="subscription-plan-detail"),

    path("client-profiles/<uuid:pk>/", views.RetrieveUpdateClientProfileView.as_view(), name="client-profile-detail"),
    path("expert-profiles/<uuid:pk>/", views.RetrieveUpdateExpertProfileView.as_view(), name="expert-profile-detail"),

    path("therapy-contracts/", views.CreateTherapyContractView.as_view(), name="therapy-contract-create"),
    path("therapy-contracts/<uuid:pk>/", views.RetrieveUpdateTherapyContractView.as_view(), name="therapy-contract-detail"),
]