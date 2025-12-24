from asgiref.sync import sync_to_async

async def get_profile(request):
    for ptype in ("client", "expert", "staff"):
        profile = await sync_to_async(getattr)(request.user, f'{ptype}profile', None)
        if profile:
            return profile
    raise KeyError("The object has not any profile attributes.")
