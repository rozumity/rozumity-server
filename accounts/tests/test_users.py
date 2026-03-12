import pytest
from django.utils import timezone
from rozumity.factories.accounts import *
from asgiref.sync import sync_to_async

import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
import pytest
import uuid
from accounts.models import User
from rozumity.factories.accounts import UserFactory


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestUserModelAdvanced:
    """
    Comprehensive tests for User model covering constraints, 
    manager logic, and edge cases.
    """

    async def test_email_uniqueness_enforced(self):
        email = "unique@rozumity.com"
        await UserFactory.acreate(email=email)
        
        from accounts.models import User
        from django.db import IntegrityError
        
        with pytest.raises(IntegrityError):
            await User.objects.acreate(email=email)

    async def test_email_normalization_by_manager(self):
        """
        Verify that EmailUserManager normalizes emails (lowercase domain).
        """
        email_raw = "TESTER@ROZUMITY.COM"
        email_expected = "TESTER@rozumity.com"
        
        # We use User.objects.acreate to hit the manager's create method
        user = await sync_to_async(User.objects.create_user)(email=email_raw, password="password123")
        assert user.email == email_expected

    async def test_uuid_primary_key_logic(self):
        """
        Ensure ID is a valid UUID and remains consistent.
        """
        user = await UserFactory.acreate()
        assert isinstance(user.id, uuid.UUID)
        
        # Verify it can be fetched by this UUID
        fetched_user = await User.objects.aget(id=user.id)
        assert fetched_user == user

    async def test_default_flags_from_model_definition(self):
        """
        Verify default values as defined in your models.py.
        Your model has is_staff=True by default.
        """
        # Create user without factory overrides to see model defaults
        user = await User.objects.acreate(email="default@test.com", password="pwd")
        
        assert user.is_staff is True  # Matches your models.py: is_staff = True
        assert user.is_active is True
        assert user.is_client is False
        assert user.is_expert is False

    async def test_email_max_length_constraint(self):
        """
        Test that email respects max_length=64.
        """
        long_email = "a" * 60 + "@test.com" # Exceeds 64 chars
        user = User(email=long_email)
        
        # full_clean() is where Django validates field lengths
        with pytest.raises(ValidationError):
            await sync_to_async(user.full_clean)()

    async def test_permissions_mixin_integration(self):
        """
        Verify that User correctly inherits from PermissionsMixin.
        """
        user = await UserFactory.acreate(is_superuser=True)
        assert user.is_superuser is True
        # Check basic permission methods (should not crash)
        assert user.has_perm("any_perm") is True 

    async def test_user_without_email_fails(self):
        """
        Verify that email is required (USERNAME_FIELD).
        """
        with pytest.raises(ValueError) as exc:
            # Most custom managers raise ValueError if email is missing
            await User.objects.create_user(email=None, password="password123")
        assert "email" in str(exc.value).lower()

    async def test_date_joined_auto_generation(self):
        """
        Ensure date_joined is set automatically on creation.
        """
        from datetime import datetime
        user = await UserFactory.acreate()
        assert isinstance(user.date_joined, datetime)
        # Should be very close to 'now'
        assert (timezone.now() - user.date_joined).seconds < 5
