from asgiref.sync import sync_to_async

async def getrel(obj, field:str):
    return await sync_to_async(getattr)(obj, field)
