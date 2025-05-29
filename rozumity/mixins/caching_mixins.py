from hashlib import md5
from django.core.cache import cache
from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.response import Response


class CacheMixinBase:
    async def _generate_cache_key(self):
        self.cache_key = md5(self.__class__.__name__.lower().encode()).hexdigest()
        return self.cache_key

    async def _generate_request_cache_key(self, request):
        self.cache_key = md5(self.__class__.__name__.lower().encode()).hexdigest()
        return self.cache_key


class ListMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key_page = await self._generate_request_cache_key(request)
        cache_key = await self._generate_cache_key()
        if not await cache.ahas_key(cache_key_page):
            queryset = self.filter_queryset(self.get_queryset())
            page = await self.apaginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = await sync_to_async(getattr)(serializer, 'data')
                resp = await self.get_apaginated_response(data)
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = await sync_to_async(getattr)(serializer, 'data')
                resp = Response(data, status=status.HTTP_200_OK)
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


class CreateMixin(CacheMixinBase):
    async def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await serializer.asave()
        data = await sync_to_async(getattr)(serializer, 'data')
        headers = await sync_to_async(self.get_success_headers)(data)
        resp = Response(data, status=status.HTTP_201_CREATED, headers=headers)
        id_name = self.serializer_class.custom_id if hasattr(self.serializer_class, "custom_id") else "id"
        try:
            cache_key = f"{await self._generate_cache_key()}:{resp.data[id_name]}"
        except KeyError as e:
            raise KeyError("Please specify the custom_id")
        await cache.aset(cache_key, resp.data)
        return resp


class RetrieveMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        if await cache.ahas_key(cache_key):
            return Response(await cache.aget(cache_key))
        else:
            resp = Response(await sync_to_async(getattr)(
                self.get_serializer(await self.aget_object(), many=False), 
                'data'
            ), status=status.HTTP_200_OK)
            await cache.aset(cache_key, resp.data)
            return resp


class UpdateMixin(CacheMixinBase):
    async def aupdate(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = await self.aget_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await serializer.asave()
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        data = await sync_to_async(getattr)(serializer, 'data')
        return Response(data, status=status.HTTP_200_OK)

    async def patch(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        kwargs["partial"] = True
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp

    async def put(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp


class DestroyMixin(CacheMixinBase):
    async def delete(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs["pk"]}"
        instance = await self.aget_object()
        await instance.adelete()
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        if await cache.ahas_key(cache_key):
            await cache.adelete(cache_key, resp.data)
        return resp


class ListCreateMixin(ListMixin, CreateMixin):
    pass


class ReadUpdateMixin(RetrieveMixin, UpdateMixin):
    pass


class RetrieveDestroyMixin(RetrieveMixin, DestroyMixin):
    pass


class RetrieveUpdateDestroyMixin(RetrieveMixin, UpdateMixin, DestroyMixin):
    pass


class CacheMixin(
    ListMixin, CreateMixin, RetrieveMixin, UpdateMixin, DestroyMixin
):
    pass
