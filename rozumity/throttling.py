from asgiref.sync import sync_to_async
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class ThrottleRateAnon(AnonRateThrottle):
    async def allow_request(self, request, view) -> bool:
        """
        Checks if the request is allowed for an anonymous user based on the rate limit.
        :return: bool
        """
        return await sync_to_async(super().allow_request)(request, view)


class ThrottleRateLogged(UserRateThrottle):
    async def allow_request(self, request, view) -> bool:
        """
        Checks if the request is allowed based on the rate limit.
        :return: bool
        """ 
        return await sync_to_async(super().allow_request)(request, view)
