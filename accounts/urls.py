from django.urls import path, include
from rest_framework import routers
from accounts import views


app_name = 'accounts'

router = routers.DefaultRouter()
router.register(r'users', views.UserListView, basename='users-list')
router.register(r'user', views.UserRetrieveView, basename='user-detail')
router.register(r'profile/client', views.ClientProfileRetrieveUpdateView, basename='client-profile')
router.register(r'profile/experts', views.ExpertProfileRetrieveUpdateView, basename='expert-profile')
router.register(r'subscriptions', views.SubscriptionPlanListView, basename='subscriptions')
router.register(r'subscription', views.SubscriptionPlanRetrieveView, basename='subscription')
router.register(r'contracts', views.TherapyContractCreateView, basename='contracts')
router.register(r'contract', views.TherapyContractRetrieveUpdateView, basename='contract')

urlpatterns = [
    path("", include(router.urls)),
]
