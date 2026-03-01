from django.urls import path, include
from accounts import views
from adrf import routers


app_name = 'accounts'

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet, basename="users")
router.register(r"universities", views.UniversityReadOnlyViewSet, basename="universities")
router.register(r"subscription-plans", views.SubscriptionPlanViewSet, basename="subscription-plans")
router.register(r"specialities", views.SpecialityReadOnlyViewSet, basename="specialities")

urlpatterns = [
    path("", include(router.urls)),

    path("client-profiles/<uuid:pk>/", views.RetrieveUpdateClientProfileView.as_view(), name="client-profile-detail"),
    path("expert-profiles/<uuid:pk>/", views.RetrieveUpdateExpertProfileView.as_view(), name="expert-profile-detail"),
    path("therapy-contracts/", views.ListCreateTherapyContractView.as_view(), name="therapy-contract-create"),
    path("therapy-contracts/<uuid:pk>/", views.RetrieveUpdateTherapyContractView.as_view(), name="therapy-contract-detail"),
    path("educations/<int:pk>/", views.EducationRetrieveUpdateDestroyView.as_view(), name="education-detail"),
]