from django.urls import path, include
from accounts import views
from adrf import routers


app_name = 'accounts'

router = routers.DefaultRouter()
router.register(r"universities", views.UniversityReadOnlyViewSet, basename="universities")
router.register(r"subscription-plans", views.SubscriptionPlanViewSet, basename="subscription-plans")
router.register(r"specialities", views.SpecialityReadOnlyViewSet, basename="specialities")
router.register(r"therapy-contracts", views.TherapyContractViewSet, basename="contracts")
router.register(r"educations", views.EducationViewSet, basename="educations")

urlpatterns = [
    path("", include(router.urls)),
    path("client-profiles/<uuid:pk>/", views.RetrieveUpdateClientProfileView.as_view(), name="client-profile-detail"),
    path("expert-profiles/<uuid:pk>/", views.RetrieveUpdateExpertProfileView.as_view(), name="expert-profile-detail"),
]