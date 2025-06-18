from hashlib import md5
from asgiref.sync import sync_to_async
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.response import Response

from rozumity.mixins.filtering_mixins import OwnedList


class CacheMixinBase:
    async def _generate_cache_key(self):
        return md5(self.__class__.__name__.lower().encode()).hexdigest()

    async def _generate_request_cache_key(self, request):
        cache_key = md5(request.get_full_path().encode()).hexdigest()
        if isinstance(self, OwnedList):
            cache_key = f'{cache_key}:{md5(str(request.user.id).encode()).hexdigest()}'
        return cache_key


class ListMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key_page = await self._generate_request_cache_key(request)
        cache_key = await self._generate_cache_key()
        paginator_cls = getattr(self, "pagination_class", None)
        if paginator_cls:
            paginator = paginator_cls()
            paginator.request = request
            if "LimitOffset" in paginator_cls.__name__:
                paginator.offset = paginator.get_offset(request)
                paginator.limit = paginator.get_limit(request)

        if not await cache.ahas_key(cache_key_page):
            queryset = self.filter_queryset(self.get_queryset())
            data = await sync_to_async(getattr)(self.get_serializer(
                queryset if not paginator else await paginator.paginate_queryset(
                    queryset, request, view=self
                ), many=True
            ), 'data')
            id_name = getattr(self.serializer_class, "custom_id", "id")
            items = data.get("results", data) if isinstance(data, dict) else data
            data_ids, cached_data = [], {}
            for item in items:
                cache_key_id = f"{cache_key}:{item[id_name]}"
                if not await cache.ahas_key(cache_key_id):
                    cached_data[cache_key_id] = item
                data_ids.append(item[id_name])
            cached_data[cache_key_page] = data_ids
            await cache.aset_many(cached_data, 100, None)
            return await sync_to_async(paginator.get_paginated_response)(data)

        cached_ids = await cache.aget(cache_key_page)
        data = await cache.aget_many((f"{cache_key}:{id}" for id in cached_ids))
        data = tuple(data.values())
        if paginator_cls:
            if "LimitOffset" in paginator_cls.__name__:
                paginator.count = await self.get_queryset().acount()
            else:
                paginator.page = data
            return await sync_to_async(paginator.get_paginated_response)(data)
        return Response(data)


class CreateMixin(CacheMixinBase):
    async def post(self, request, *args, **kwargs):
        resp = await self.acreate(request, *args, **kwargs)
        id_name = getattr(self.serializer_class, "custom_id", "id")
        try:
            cache_key = f"{await self._generate_cache_key()}:{resp.data[id_name]}"
        except KeyError:
            raise KeyError("Please specify the custom_id")
        await cache.aset(cache_key, resp.data)
        return resp


class RetrieveMixin(CacheMixinBase):
    async def get(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        if await cache.ahas_key(cache_key):
            return Response(await cache.aget(cache_key))
        else:
            serializer = self.get_serializer()
            response = Response(await sync_to_async(
                serializer.to_representation
            )(await self.aget_object()))
            await cache.aset(cache_key, response.data)
            return response


class UpdateMixin(CacheMixinBase):
    async def aupdate(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = await self.aget_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        await serializer.asave()
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return Response(
            await sync_to_async(getattr)(serializer, 'data'),
            status=status.HTTP_200_OK
        )

    async def patch(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        kwargs["partial"] = True
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp

    async def put(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        resp = await self.aupdate(request, *args, **kwargs)
        await cache.aset(cache_key, resp.data)
        return resp


class DestroyMixin(CacheMixinBase):
    async def delete(self, request, *args, **kwargs):
        cache_key = f"{await self._generate_cache_key()}:{self.kwargs['pk']}"
        instance = await self.aget_object()
        await instance.adelete()
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        if await cache.ahas_key(cache_key):
            await cache.adelete(cache_key)
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


class CacheViewSetMixin(CacheMixinBase, viewsets.GenericViewSet):
    async def list(self, request, *args, **kwargs):
        mixin = ListMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.get(request, *args, **kwargs)

    async def create(self, request, *args, **kwargs):
        mixin = CreateMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.post(request, *args, **kwargs)

    async def retrieve(self, request, *args, **kwargs):
        mixin = RetrieveMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.get(request, *args, **kwargs)

    async def update(self, request, *args, **kwargs):
        mixin = UpdateMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.put(request, *args, **kwargs)

    async def partial_update(self, request, *args, **kwargs):
        mixin = UpdateMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.patch(request, *args, **kwargs)

    async def destroy(self, request, *args, **kwargs):
        mixin = DestroyMixin()
        mixin.__dict__.update(self.__dict__)
        return await mixin.delete(request, *args, **kwargs)
