import pytest_asyncio
from adrf.test import AsyncAPIClient

@pytest_asyncio.fixture
async def adrf_client():
    """
    Fixture for the asynchronous DRF APIClient from 'adrf' package.
    """
    return AsyncAPIClient()
