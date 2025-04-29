from django.core.cache import cache
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class AsyncCacheMixinBase:
    async def _generate_cache_key(self, request=None):
        #cache_key = 'async-cache:' + hashlib.md5(key_prefix.encode()).hexdigest()
        if request:
            return 'list-cache:' + request.get_full_path()
        return self.cache_key if hasattr(self, "cache_key") else self.__class__.__name__.lower()


class AsyncCacheListMixin(AsyncCacheMixinBase):
    class LimitOffsetPaginationCache(LimitOffsetPagination):
        async def aget_paginated_response(self, data):
            self.offset = self.get_offset(self.request)
            self.limit = self.get_limit(self.request)
            self.count = len(data)
            return Response({
                'count': len(data),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            })
        
    async def get(self, request, *args, **kwargs):
        pagination = None
        cache_key_page = await self._generate_cache_key(request)
        cache_key = await self._generate_cache_key()
        if self.pagination_class and "LimitOffset" in self.pagination_class.__name__:
            pagination = AsyncCacheListMixin.LimitOffsetPaginationCache()
            pagination.request = request
        if await cache.ahas_key(cache_key_page):
            cached_ids = await cache.aget(cache_key_page)
            data = await cache.aget_many((f"{cache_key}:{id}" for id in cached_ids))
            data = [v for (_, v) in data.items()]
            return await pagination.aget_paginated_response(data) if pagination else Response(data)
        else:
            resp = await self.alist(request, *args, **kwargs)
            data_ids, cached_data = [], {}
            for o in resp.data["results"]:
                cache_key_id = f"{cache_key}:{o['id']}"
                if not await cache.ahas_key(cache_key_id):
                    cached_data[cache_key_id] = o
                data_ids.append(o['id'])
            cached_data[cache_key_page] = data_ids
            await cache.aset_many(cached_data, 100, None)
            return resp


class AsyncCacheCreateMixin(AsyncCacheMixinBase):
    async def post(self, request, *args, **kwargs):
        resp = await self.acreate(request, *args, **kwargs)
        cache_key = f"{await self._generate_cache_key()}:{resp.data['id']}"
        await cache.aset(cache_key, resp.data)
        return resp


class AsyncCacheRetrieveMixin(AsyncCacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        if await cache.ahas_key(cache_key):
            return Response(await cache.aget(cache_key))
        else:
            resp = await self.aretrieve(request, *args, **kwargs)
            await cache.aset(cache_key, resp.data)
            return resp


class AsyncCacheUpdateMixin(AsyncCacheMixinBase):
    async def patch(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        resp = await sync_to_async(self.partial_update)(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp

    async def put(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp


class AsyncCacheDestroyMixin(AsyncCacheMixinBase):
    async def delete(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
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
