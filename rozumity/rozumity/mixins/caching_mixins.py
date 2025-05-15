from hashlib import md5
from django.core.cache import cache
from asgiref.sync import sync_to_async
from rest_framework.response import Response


class CacheMixinBase:
    async def _generate_cache_key(self, request=None):
        cache_key = request.get_full_path() if request else self.__class__.__name__.lower()
        self.cache_key = md5(cache_key.encode()).hexdigest()
        return self.cache_key


class CacheListMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key_page = await self._generate_cache_key(request)
        cache_key = await self._generate_cache_key()

        if not await cache.ahas_key(cache_key_page):
            resp = await sync_to_async(self.list)(request, *args, **kwargs)
            data_ids, cached_data= [], {}
            id_name = self.serializer_class.custom_id if hasattr(self.serializer_class, "custom_id") else "id"
            for item in resp.data["results"]:
                try:
                    cache_key_id = f"{cache_key}:{item[id_name]}"
                except KeyError as e:
                    raise KeyError("Please specify the custom_id")
                if not await cache.ahas_key(cache_key_id):
                    cached_data[cache_key_id] = item
                data_ids.append(item[id_name])
            cached_data[cache_key_page] = data_ids
            await cache.aset_many(cached_data, 100, None)
            return resp

        cached_ids = await cache.aget(cache_key_page)
        data = await cache.aget_many((f"{cache_key}:{id}" for id in cached_ids))
        data = data.values()

        if self.pagination_class and "LimitOffset" in self.pagination_class.__name__: 
            pg = self.pagination_class()
            pg.request, pg.count, pg.offset, pg.limit = (
                request, len(data), pg.get_offset(request), pg.get_limit(request)
            )
            return pg.get_paginated_response(data)

        return Response(data)


class CacheCreateMixin(CacheMixinBase):
    async def post(self, request, *args, **kwargs):
        resp = await self.acreate(request, *args, **kwargs)
        id_name = self.serializer_class.custom_id if hasattr(self.serializer_class, "custom_id") else "id"
        try:
            cache_key = f"{await self._generate_cache_key()}:{resp.data[id_name]}"
        except KeyError as e:
            raise KeyError("Please specify the custom_id")
        await cache.aset(cache_key, resp.data)
        return resp


class CacheRetrieveMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        if await cache.ahas_key(cache_key):
            return Response(await cache.aget(cache_key))
        else:
            resp = await sync_to_async(self.retrieve)(request, *args, **kwargs)
            await cache.aset(cache_key, resp.data)
            return resp


class CacheUpdateMixin(CacheMixinBase):
    async def patch(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        resp = await sync_to_async(self.partial_update)(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp

    async def put(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        resp = await sync_to_async(self.update(request, *args, **kwargs))
        await cache.aset(cache_key, resp.data)
        return resp


class CacheDestroyMixin(CacheMixinBase):
    async def delete(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        resp = await sync_to_async(self.destroy(request, *args, **kwargs))
        if await cache.ahas_key(cache_key):
            await cache.adelete(cache_key, resp.data)
        return resp


class CacheLCMixin(CacheListMixin, CacheCreateMixin):
    pass


class CacheRUMixin(CacheRetrieveMixin, CacheUpdateMixin):
    pass


class CacheRDMixin(CacheRetrieveMixin, CacheDestroyMixin):
    pass


class CacheRUDMixin(CacheRetrieveMixin, CacheUpdateMixin, CacheDestroyMixin):
    pass
