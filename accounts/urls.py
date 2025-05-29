from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path("users/", views.UserListView.as_view(), name="users-list"),
    path("user/<uuid:pk>/", views.UserRetrieveView.as_view(), name="user-detail"),
    path("profile/client/<uuid:pk>/", views.ClientProfileRetrieveUpdateView.as_view(), name="client-profile"),
    path("profile/expert/<uuid:pk>/", views.ExpertProfileRetrieveUpdateView.as_view(), name="expert-profile"),
    path("subscriptions/", views.SubscriptionPlanListView.as_view(), name="subscriptions"),
    path("subscription/<int:pk>/", views.SubscriptionPlanRetrieveView.as_view(), name="subscription"),
    path("contracts/", views.TherapyContractCreateView.as_view(), name="contracts"),
    path("contract/<int:pk>/", views.TherapyContractRetrieveUpdateView.as_view(), name="contract"),
]
