from django.urls import path
from accounts import views

app_name = 'accounts'

urlpatterns = [
    path("users/", views.UserReadOnlyViewSet.as_view({"get": "alist"}), name="users"),
    path("user/<uuid:pk>/", views.UserReadOnlyViewSet.as_view({"get": "aretrieve"}), name="user"),
    path("profile/client/<uuid:pk>/", views.ClientProfileViewSet.as_view({"get": "aretrieve", "put": "aupdate", "patch": "partial_aupdate"}), name="client-profile"),
    path("profile/expert/<uuid:pk>/", views.ExpertProfileViewSet.as_view({"get": "aretrieve", "put": "aupdate", "patch": "partial_aupdate"}), name="expert-profile"),
    path("subscriptions/", views.SubscriptionPlanReadOnlyViewSet.as_view({"get": "alist"}), name="subscriptions"),
    path("subscription/<int:pk>/", views.SubscriptionPlanReadOnlyViewSet.as_view({"get": "aretrieve"}), name="subscription"),
    path("contracts/", views.TherapyContractViewSet.as_view({"post": "acreate"}), name="contracts"),
    path("contract/<int:pk>/", views.TherapyContractViewSet.as_view({"get": "aretrieve", "put": "aupdate", "patch": "partial_aupdate"}), name="contract")
]
