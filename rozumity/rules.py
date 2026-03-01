import rules


@rules.predicate
def is_profile_owner(user, profile):
    return user and profile and profile.user_id == user.id


@rules.predicate
def is_client(user):
    return user and getattr(user, 'is_client', False)


@rules.predicate
def is_expert(user):
    return user and getattr(user, 'is_expert', False)


@rules.predicate
def is_owner(user, obj):
    if not user or not obj:
        return False
    return (
        getattr(obj, 'client_id', None) == user.id
    ) or (
        getattr(obj, 'expert_id', None) == user.id
    )


rules.add_perm('is_profile_owner', rules.is_staff | is_profile_owner)
rules.add_perm('is_expert', rules.is_staff | is_expert)
rules.add_perm('is_client', rules.is_staff | is_client)
rules.add_perm('is_owner', rules.is_staff | is_owner)
