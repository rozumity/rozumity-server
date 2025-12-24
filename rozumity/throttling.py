from asgiref.sync import sync_to_async
from rest_framework.throttling import (
    AnonRateThrottle, UserRateThrottle
)


class AnonRateAsyncThrottle(AnonRateThrottle):
    async def allow_request(self, request, view) -> bool:
        return await sync_to_async(super().allow_request)(request, view)


class UserRateAsyncThrottle(UserRateThrottle):
    async def allow_request(self, request, view) -> bool:
        return await sync_to_async(super().allow_request)(request, view)
