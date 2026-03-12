from asgiref.sync import sync_to_async
from factory.django import DjangoModelFactory


class Factory(DjangoModelFactory):
    @classmethod
    async def acreate(cls, **kwargs):
        select_related = kwargs.pop('select_related', [])
        instance = await sync_to_async(cls.create)(**kwargs)
        if select_related:
            return await cls._meta.model.objects.select_related(*select_related).aget(pk=instance.pk)
        return instance

    @classmethod
    async def acreate_batch(cls, *args, **kwargs):
        return await sync_to_async(cls.create_batch)(*args, **kwargs)
