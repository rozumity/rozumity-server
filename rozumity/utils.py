from asgiref.sync import sync_to_async

async def rel(obj, field:str):
    return await sync_to_async(getattr)(obj, field)
