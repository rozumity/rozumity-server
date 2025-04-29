from django.core.cache import cache
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

class AsyncCacheListMixin:
    class LimitOffsetPaginationCache(LimitOffsetPagination):
        async def aget_paginated_response(self, data):
            self.count = len(data)
            return Response({
                'count': len(data),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            })

        async def aget_cached_key(self, key):
            self.offset = self.get_offset(self.request)
            self.limit = self.get_limit(self.request)
            return f"{key}_ids_{self.offset}_{self.limit}"
        
    async def get(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.lower().split("list")[0]
            print(cache_key)
        else:
            cache_key = self.cache_key
        if self.pagination_class and "LimitOffset" in self.pagination_class.__name__:
            pagination = AsyncCacheListMixin.LimitOffsetPaginationCache()
            pagination.request = request
            cache_key_page = await pagination.aget_cached_key(cache_key)
        else:
            pagination = None
            cache_key_page = f"{cache_key}_list"
        if await cache.ahas_key(cache_key_page):
            cached_ids = await cache.aget(cache_key_page)
            data = await cache.aget_many((f"{cache_key}_{id}" for id in cached_ids))
            data = [v for (_, v) in data.items()]
            return await pagination.aget_paginated_response(data) if pagination else Response(data)
        else:
            resp = await self.alist(request, *args, **kwargs)
            data_ids, cached_data = [], {}
            for o in resp.data["results"]:
                print(o)
                cache_key_id = f"{cache_key}_{o['id']}"
                if not await cache.ahas_key(cache_key_id):
                    cached_data[cache_key_id] = o
                data_ids.append(o['id'])
            cached_data[cache_key_page] = data_ids
            await cache.aset_many(cached_data, 100, None)
            return resp


class AsyncCacheCreateMixin:
    async def post(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.replace("List", "").lower().split("create")[0]
            print(cache_key)
        else:
            cache_key = self.cache_key
        resp = await self.acreate(request, *args, **kwargs)
        cache_key = f"{cache_key}_{resp.data['id']}"
        await cache.aset(cache_key, resp.data)
        return resp


class AsyncCacheRetrieveMixin:
    async def get(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.lower().split("retrieve")[0]
            print(cache_key)
        else:
            cache_key = self.cache_key
        cache_key = f"{cache_key}_{self.kwargs['pk']}"
        if await cache.ahas_key(cache_key):
            return Response(await cache.aget(cache_key))
        else:
            resp = await self.aretrieve(request, *args, **kwargs)
            await cache.aset(cache_key, resp.data)
            return resp


class AsyncCacheUpdateMixin:
    async def patch(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.replace("Retrieve", "").replace("Destroy", "").lower().split("update")[0]
            print(cache_key)
        else:
            cache_key = self.cache_key
        cache_key = f"{cache_key}_{self.kwargs['pk']}"
        resp = await sync_to_async(self.partial_update)(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp

    async def put(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.replace("Retrieve", "").replace("Destroy", "").lower().split("update")[0]
            print(cache_key)
        else:
            cache_key = self.cache_key
        cache_key = f"{cache_key}_{self.kwargs['pk']}"
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp


class AsyncCacheDestroyMixin:
    async def delete(self, request, *args, **kwargs):
        if not hasattr(self, "cache_key"):
            cache_key = self.__class__.__name__.replace("Retrieve", "").replace("Update", "").lower().split("destroy")[0]
            print(cache_key)
        cache_key = f"{cache_key}_{self.kwargs['pk']}"
        resp = await self.adestroy(request, *args, **kwargs)
        if await cache.ahas_key(cache_key):
            await cache.adelete(cache_key, resp.data)
        return resp


class AsyncCacheListCreateMixin(AsyncCacheListMixin, AsyncCacheCreateMixin):
    pass


class AsyncCacheRetrieveUpdateMixin(AsyncCacheRetrieveMixin, AsyncCacheUpdateMixin):
    pass


class AsyncCacheRetrieveDestroyMixin(AsyncCacheRetrieveMixin, AsyncCacheDestroyMixin):
    pass


class AsyncCacheRetrieveUpdateDestroyMixin(AsyncCacheRetrieveMixin, AsyncCacheUpdateMixin, AsyncCacheDestroyMixin):
    pass
