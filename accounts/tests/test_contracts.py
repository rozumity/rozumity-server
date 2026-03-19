import pytest
from datetime import timedelta, date
from django.utils import timezone
from asgiref.sync import sync_to_async

from accounts.models import TherapyContract
from rozumity.factories.accounts import (
    TherapyContractFactory, SubscriptionPlanFactory, 
    ClientProfileFactory
)

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestTherapyContractFull:
    
    @pytest.fixture
    async def free_plan(self):
        return await SubscriptionPlanFactory.acreate(has_diary=False, has_ai=False)

    @pytest.fixture
    async def pro_plan(self):
        return await SubscriptionPlanFactory.acreate(
            has_diary=True, has_ai=True, has_screening=True, has_dyagnosis=True
        )

    # --- Section 1: Payment & Activity Logic ---

    @pytest.mark.parametrize("c_days, e_days, expected_paid, expected_full", [
        (TherapyContract.DurationDays.FREE, TherapyContract.DurationDays.FREE, False, False),
        (TherapyContract.DurationDays.WEEK, TherapyContract.DurationDays.FREE, True, False),
        (TherapyContract.DurationDays.WEEK, TherapyContract.DurationDays.MONTH, True, True),
    ])
    async def test_payment_logic_states(self, c_days, e_days, expected_paid, expected_full):
        """
        Ensure that payment flags (is_paid, is_paid_full) correctly reflect 
        the combination of client and expert subscription durations.
        """
        contract = await TherapyContractFactory.acreate(
            client_plan_days=c_days, 
            expert_plan_days=e_days
        )
        assert await contract.is_paid is expected_paid
        assert await contract.is_paid_full is expected_full

    async def test_activity_at_expiration_edge_case(self):
        """
        Verify that a contract is marked as inactive exactly when the 
        current time reaches the calculated expiration date.
        """
        now = timezone.now()
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.DAY,
            client_plan_prolong_date=now - timedelta(days=1)
        )
        assert await contract.is_active_client is False

    # --- Section 2: Date Calculations ---

    async def test_date_calculations(self):
        """
        Confirm that expiration dates for both participants are calculated 
        correctly relative to their respective prolongation dates and durations.
        """
        now = timezone.now()
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.WEEK,   # 7
            expert_plan_days=TherapyContract.DurationDays.MONTH, # 30
            client_plan_prolong_date=now,
            expert_plan_prolong_date=now
        )
        
        c_end = await contract.date_end_client
        e_end = await contract.date_end_expert
        
        assert c_end.date() == (now + timedelta(days=7)).date()
        assert e_end.date() == (now + timedelta(days=30)).date()
        assert (await contract.date_end) == e_end

    # --- Section 3: Feature Inheritance ---

    async def test_feature_flags_merging(self, pro_plan, free_plan):
        """
        Verify that the contract correctly merges feature availability (OR logic) 
        from both the client's and the expert's active subscription plans.
        """
        # Hybrid scenario: Client (Pro), Expert (Free)
        contract = await TherapyContractFactory.acreate(
            client_plan=pro_plan, 
            expert_plan=free_plan
        )
        
        assert await contract.has_diary is True
        assert await contract.has_ai is True
        
        # Expert specific
        contract.expert_plan = pro_plan
        assert await contract.has_dyagnosis is True

    # --- Section 4: Profiles & Integrity ---

    async def test_profile_integration(self):
        """
        Test the integration between the contract and profile models, 
        ensuring calculated properties like age and adult status are accurate.
        """
        age_20 = date.today() - timedelta(days=20*365.25)
        client = await ClientProfileFactory.acreate(
            first_name="Ivan", last_name="Ivanov", date_birth=age_20
        )
        contract = await TherapyContractFactory.acreate(client=client)
        
        assert await client.is_adult is True
        assert int(await client.age) == 20
        assert await client.name == "Ivan Ivanov"

    async def test_null_relations_safety(self):
        """Ensure __str__ and properties handle None gracefully."""
        contract = await TherapyContractFactory.acreate(client=None, expert=None)
        
        assert "Contract | Client: None" in str(contract)
        assert await contract.has_both is False
        assert await contract.has_client_only is False

    async def test_db_constraints_forever(self):
        """Validate 999 days doesn't break validators."""
        contract = await TherapyContractFactory.acreate(
            client_plan_days=TherapyContract.DurationDays.FOREVER
        )
        # Sync_to_async is needed for full_clean as it's a sync Django method
        await sync_to_async(contract.full_clean)()
        assert contract.client_plan_days == 999
