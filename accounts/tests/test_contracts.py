import pytest
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async

from rozumity.factories.accounts import *

from accounts.models import TherapyContract


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestTherapyContractFull:
    """
    Comprehensive test suite for TherapyContract model logic, 
    covering payments, dates, activity status, and plan features.
    """

    # --- Section 1: Payment Logic ---

    async def test_payment_flags_logic(self):
        """
        Verify all payment-related properties: is_paid, is_paid_full, 
        is_paid_client, and is_paid_expert.
        """
        # No one paid
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.FREE,
            expert_plan_days=TherapyContract.DurationDays.FREE
        )
        assert await contract.is_paid is False
        assert await contract.is_paid_full is False

        # Only client paid
        contract.client_plan_days = TherapyContract.DurationDays.WEEK
        assert await contract.is_paid is True
        assert await contract.is_paid_client is True
        assert await contract.is_paid_expert is False
        assert await contract.is_paid_full is False

        # Both paid
        contract.expert_plan_days = TherapyContract.DurationDays.MONTH
        assert await contract.is_paid_full is True
        assert await contract.is_paid_expert is True

    # --- Section 2: Date Calculations ---

    async def test_date_end_calculations(self):
        """
        Verify that date_end correctly identifies the furthest expiration date
        and handles various durations including FOREVER.
        """
        now = timezone.now()
        
        # Standard duration check
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.WEEK,   # 7 days
            client_plan_prolong_date=now,
            expert_plan_days=TherapyContract.DurationDays.MONTH, # 30 days
            expert_plan_prolong_date=now
        )
        
        expected_client_end = now + timedelta(days=7)
        expected_expert_end = now + timedelta(days=30)
        
        assert (await contract.date_end_client).date() == expected_client_end.date()
        assert (await contract.date_end_expert).date() == expected_expert_end.date()
        # date_end should be the max of both
        assert (await contract.date_end).date() == expected_expert_end.date()

    async def test_forever_duration_logic(self):
        """
        Ensure the FOREVER (999 days) constant is handled correctly for dates.
        """
        long_ago = timezone.now() - timedelta(days=500)
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.FOREVER,
            client_plan_prolong_date=long_ago
        )
        
        # Should still be active because 500 < 999
        assert await contract.is_active_client is True
        assert (await contract.date_end_client).date() == (long_ago + timedelta(days=999)).date()

    # --- Section 3: Activity Status ---

    async def test_activity_logic_combinations(self):
        """
        Test is_active and is_active_full under different expiration scenarios.
        """
        now = timezone.now()
        past = now - timedelta(days=60)
        
        # Case: Client active, Expert expired
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.MONTH,
            client_plan_prolong_date=now,
            expert_plan_days=TherapyContract.DurationDays.MONTH,
            expert_plan_prolong_date=past
        )
        
        assert await contract.is_active_client is True
        assert await contract.is_active_expert is False
        # is_active (any) should be True
        assert await contract.is_active is True
        # is_active_full (all/total_end) should be True because date_end is in the future
        assert await contract.is_active_full is True

    # --- Section 4: Plan Features (Inheritance) ---

    async def test_subscription_feature_flags(self):
        """
        Test that contract inherits features from both plans (OR logic),
        except for diagnosis which is expert-only.
        """
        # Client has diary, Expert has AI and Screening
        plan_c = await SubscriptionPlanFactory.acreate(has_diary=True, has_ai=False)
        plan_e = await SubscriptionPlanFactory.acreate(
            has_ai=True, has_screening=True, has_dyagnosis=True
        )
        
        contract = await TherapyContractFactory.acreate(
            client_plan=plan_c,
            expert_plan=plan_e
        )
        
        assert await contract.has_diary is True
        assert await contract.has_ai is True
        assert await contract.has_screening is True
        assert await contract.has_dyagnosis is True

        # If both empty
        empty_plan = await SubscriptionPlanFactory.acreate(has_diary=False, has_ai=False)
        contract.client_plan = empty_plan
        contract.expert_plan = empty_plan
        assert await contract.has_diary is False
        assert await contract.has_ai is False

    # --- Section 5: Relationships and Profiles ---

    async def test_relationship_helpers(self):
        """
        Verify has_both, has_client_only, and has_expert_only properties.
        """
        # Client only
        contract = await TherapyContractFactory.acreate(expert=None)
        assert await contract.has_client_only is True
        assert await contract.has_both is False
        
        # Expert only
        contract.expert = await ExpertProfileFactory.acreate()
        contract.client = None
        assert await contract.has_expert_only is True
        assert await contract.has_client_only is False
        
        # Both
        contract.client = await ClientProfileFactory.acreate()
        assert await contract.has_both is True

    async def test_profile_integration_via_contract(self):
        """
        Test properties of the profiles connected to the contract.
        """
        # Client aged 20
        birth_date = date.today() - timedelta(days=20*365.25)
        client = await ClientProfileFactory.acreate(
            first_name="Ivan", last_name="Ivanov", date_birth=birth_date
        )
        contract = await TherapyContractFactory.acreate(client=client)
        
        assert await client.is_adult is True
        assert int(await client.age) == 20
        assert await client.name == "Ivan Ivanov"

    # --- Section 6: Edge Cases & Safety ---

    async def test_null_plan_safety(self):
        """
        Ensure that properties don't crash if expert_plan or client_plan is None.
        """
        contract = await TherapyContractFactory.acreate(
            client_plan=None,
            expert_plan=None,
            client_plan_days=TherapyContract.DurationDays.FREE
        )
        
        # Testing features shouldn't raise AttributeError if rel() returns None
        # Note: This depends on how your rel() helper and model handles None.
        try:
            await contract.has_diary
            await contract.has_ai
        except AttributeError:
            pytest.fail("Contract features crashed when plans are None.")

    async def test_activity_at_exact_expiration_moment(self):
        """
        Test the exact moment of expiration.
        If date_end is exactly now, is_active should technically be False 
        (assuming > comparison).
        """
        now = timezone.now()
        # Set prolong date so that end date is exactly 'now'
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.DAY, # 1 day
            client_plan_prolong_date=now - timedelta(days=1)
        )
        
        # Depending on millisecond precision, it should be False or very close to it
        assert await contract.is_active_client is False

    async def test_empty_contract_relationships(self):
        """
        Test properties when both client and expert profiles are missing.
        """
        contract = await TherapyContractFactory.acreate(client=None, expert=None)
        
        assert await contract.has_client_only is False
        assert await contract.has_expert_only is False
        assert await contract.has_both is False

    async def test_complex_date_overlap(self):
        """
        Scenario: Client has a long-term plan from the past, 
        Expert has a short-term plan from today.
        """
        now = timezone.now()
        
        # Client: Year plan started 200 days ago (still ~160 days left)
        client_start = now - timedelta(days=200)
        # Expert: Day plan started today (1 day left)
        expert_start = now
        
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.YEAR, # 360 days
            client_plan_prolong_date=client_start,
            expert_plan_days=TherapyContract.DurationDays.DAY, # 1 day
            expert_plan_prolong_date=expert_start
        )
        
        client_end = await contract.date_end_client
        expert_end = await contract.date_end_expert
        
        assert client_end > expert_end
        assert await contract.date_end == client_end

    async def test_contract_string_representation_safe(self):
        """
        Ensure __str__ method works even if profiles are None.
        """
        contract = await TherapyContractFactory.acreate(client=None, expert=None)
        assert "Contract | Client: None" in str(contract)

    async def test_forever_constant_fits_db_constraints(self):
        """
        Ensure that the FOREVER value (999) does not violate 
        any MaxValueValidators or database IntegerField limits.
        """
        # Testing both client and expert duration fields
        try:
            contract = await TherapyContractFactory.acreate(
                client_plan_days=TherapyContract.DurationDays.FOREVER,
                expert_plan_days=TherapyContract.DurationDays.FOREVER
            )
            
            # Trigger full_clean to check for MaxValueValidator issues 
            # (acreate doesn't always call full_clean by default)
            await sync_to_async(contract.full_clean)()
            
            assert contract.client_plan_days == 999
            assert contract.expert_plan_days == 999
            
        except ValidationError as e:
            pytest.fail(f"FOREVER constant (999) caused a ValidationError: {e}")
        except Exception as e:
            pytest.fail(f"FOREVER constant (999) caused a database error: {e}")

    async def test_extreme_duration_values(self):
        """
        Check if the field can handle values even larger than FOREVER, 
        just in case of future expansion.
        """
        # Testing a 10-year equivalent in days
        ten_years_days = 3650 
        
        contract = await TherapyContractFactory.acreate(
            client_plan_days=ten_years_days
        )
        
        refreshed = await TherapyContract.objects.aget(pk=contract.pk)
        assert refreshed.client_plan_days == ten_years_days
