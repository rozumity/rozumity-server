from asgiref.sync import sync_to_async
from factory.django import DjangoModelFactory


class Factory(DjangoModelFactory):
    @classmethod
    async def acreate(cls, **kwargs):
        return await sync_to_async(cls.create)(**kwargs)

    @classmethod
    async def acreate_batch(cls, *args, **kwargs):
        return await sync_to_async(cls.create_batch)(*args, **kwargs)
