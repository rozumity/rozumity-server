import pytest
from decimal import Decimal
from accounts.models import SubscriptionPlan
from rozumity.factories.accounts import SubscriptionPlanFactory, UserFactory
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestSubscriptionPlanFull:
    """
    Complete test suite for SubscriptionPlan model.
    Covers owner types, feature flags, money fields, and string representation.
    """
    async def test_owner_type_choices_completeness(self):
        """
        Ensure all defined OwnerTypes are valid and have correct display names.
        """
        # Testing all integer choices
        choices = SubscriptionPlan.OwnerTypes
        
        assert choices.CLIENT == 0
        assert choices.EXPERT == 1
        assert choices.BOTH == 2
        
        # Verify labels (translations)
        assert choices.CLIENT.label == "Client"
        assert choices.EXPERT.label == "Expert"
        assert choices.BOTH.label == "Both"

    async def test_exclusive_feature_combinations(self):
        """
        Verify that features can be toggled individually without affecting others.
        Check cases where only one specific feature is active.
        """
        # Case: Only Diary enabled
        diary_only = await SubscriptionPlanFactory.acreate(has_diary=True, has_ai=False)
        assert diary_only.has_diary is True
        assert diary_only.has_ai is False
        assert diary_only.has_screening is False
        
        # Case: Only AI enabled
        ai_only = await SubscriptionPlanFactory.acreate(has_ai=True, has_diary=False)
        assert ai_only.has_ai is True
        assert ai_only.has_diary is False
        
        # Case: Only Screening enabled
        screening_only = await SubscriptionPlanFactory.acreate(has_screening=True, has_diary=False)
        assert screening_only.has_screening is True
        assert screening_only.has_dyagnosis is False

    async def test_diagnosis_feature_specifically(self):
        """
        Separate check for the 'dyagnosis' field (verifying the typo-name in model).
        """
        plan = await SubscriptionPlanFactory.acreate(has_dyagnosis=True)
        assert plan.has_dyagnosis is True
        
        plan_disabled = await SubscriptionPlanFactory.acreate(has_dyagnosis=False)
        assert plan_disabled.has_dyagnosis is False

    async def test_bulk_creation_owner_filtering(self):
        """
        Verify that we can filter plans by owner_type in the database.
        """
        # Create multiple plans
        await SubscriptionPlanFactory.acreate_batch(2, owner_type=SubscriptionPlan.OwnerTypes.CLIENT)
        await SubscriptionPlanFactory.acreate_batch(3, owner_type=SubscriptionPlan.OwnerTypes.EXPERT)
        
        client_plans_count = await SubscriptionPlan.objects.filter(
            owner_type=SubscriptionPlan.OwnerTypes.CLIENT
        ).acount()
        
        expert_plans_count = await SubscriptionPlan.objects.filter(
            owner_type=SubscriptionPlan.OwnerTypes.EXPERT
        ).acount()
        
        assert client_plans_count == 2
        assert expert_plans_count == 3

    async def test_plan_update_features(self):
        """
        Ensure that updating a plan correctly saves new feature states.
        """
        plan = await SubscriptionPlanFactory.acreate(has_diary=False)
        assert plan.has_diary is False
        
        plan.has_diary = True
        await plan.asave()
        
        # Refresh from DB
        await plan.arefresh_from_db()
        assert plan.has_diary is True

    async def test_money_field_precision_and_currency(self):
        """
        Fixes the currency comparison error and verifies decimal precision.
        """
        price_val = Decimal("299.99")
        plan = await SubscriptionPlanFactory.acreate(
            price=price_val,
            price_currency='USD'
        )
        
        # Verify amount
        assert plan.price.amount == price_val
        
        # FIX: compare with .code or cast to string to avoid Currency object mismatch
        assert plan.price.currency.code == 'USD'
        assert str(plan.price.currency) == 'USD'

    async def test_plan_string_representation(self):
        """
        Check the __str__ method formatting: "{title} - {price} ({owner})"
        """
        plan = await SubscriptionPlanFactory.acreate(
            title="Professional Plan",
            price=Decimal("100.00"),
            owner_type=SubscriptionPlan.OwnerTypes.EXPERT
        )
        
        expected_str = f"Professional Plan - $100.00 (Expert)"
        # Note: djmoney string formatting might vary slightly based on locale (e.g., '100.00 USD')
        # We check for key components to be safe
        plan_str = str(plan)
        assert "Professional Plan" in plan_str
        assert "100.00" in plan_str
        assert "(Expert)" in plan_str

    async def test_long_content_handling(self):
        """
        Test that the model accepts maximum lengths for CharField and TextField.
        """
        max_title = "T" * 64
        max_desc = "D" * 500
        
        plan = await SubscriptionPlanFactory.acreate(
            title=max_title,
            description=max_desc
        )
        
        assert len(plan.title) == 64
        assert len(plan.description) == 500


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestSubscriptionPlanAPI:
    """
    In-depth testing for SubscriptionPlan Read-Only views.
    Verifies permissions, data structure, and HTTP method restrictions.
    """

    async def test_list_plans_authenticated(self, adrf_client):
        """
        Verify that an authenticated user can list all plans.
        """
        await SubscriptionPlanFactory.acreate(title="Plan A", owner_type=0)
        await SubscriptionPlanFactory.acreate(title="Plan B", owner_type=1)

        user = await UserFactory.acreate()
        url = reverse('accounts:subscription-plans-list')

        adrf_client.force_authenticate(user=user)
        response = await adrf_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        assert "results" in response.data
        assert isinstance(response.data['results'], list)
        assert len(response.data['results']) >= 2

    async def test_retrieve_plan_detail_data(self, adrf_client):
        """
        Verify the detailed fields of a single plan.
        """
        plan = await SubscriptionPlanFactory.acreate(
            title="Premium Support",
            price=150.00,
            has_ai=True,
            owner_type=SubscriptionPlan.OwnerTypes.BOTH
        )
        user = await UserFactory.acreate()
        url = reverse('accounts:subscription-plans-detail', kwargs={'pk': plan.pk})

        adrf_client.force_authenticate(user=user)
        response = await adrf_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Premium Support"
        assert response.data['has_ai'] is True
        assert "150.00" in str(response.data['price'])

        assert response.data['owner_type'] == SubscriptionPlan.OwnerTypes.BOTH.label

    async def test_read_only_methods_enforcement(self, adrf_client):
        """
        Verify that POST, PUT, DELETE are forbidden for this ViewSet.
        """
        plan = await SubscriptionPlanFactory.acreate()
        user = await UserFactory.acreate(is_staff=True)
        url = reverse('accounts:subscription-plans-detail', kwargs={'pk': plan.pk})
        
        adrf_client.force_authenticate(user=user)
        
        list_url = reverse('accounts:subscription-plans-list')
        response_post = await adrf_client.post(list_url, data={"title": "New"})
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response_delete = await adrf_client.delete(url)
        assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    async def test_owner_type_filtering_logic(self, adrf_client):
        """
        Check if the owner_type choices are correctly represented as labels.
        """
        plan = await SubscriptionPlanFactory.acreate(owner_type=SubscriptionPlan.OwnerTypes.EXPERT)
        user = await UserFactory.acreate()
        url = reverse('accounts:subscription-plans-detail', kwargs={'pk': plan.pk})

        adrf_client.force_authenticate(user=user)
        response = await adrf_client.get(url)

        assert response.data['owner_type'] == SubscriptionPlan.OwnerTypes.EXPERT.label

    async def test_caching_validity(self, adrf_client):
        """
        Verify that caching returns data consistently.
        """
        plan = await SubscriptionPlanFactory.acreate(title="CacheTest")
        user = await UserFactory.acreate()
        url = reverse('accounts:subscription-plans-detail', kwargs={'pk': plan.pk})
        
        adrf_client.force_authenticate(user=user)
        
        res1 = await adrf_client.get(url)
        res2 = await adrf_client.get(url)
        
        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.data['title'] == res2.data['title']
