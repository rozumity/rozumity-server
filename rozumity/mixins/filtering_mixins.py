class Owned:
    def get_queryset(self):
        if self.request.user.is_authenticated:
            model = self.serializer_class.Meta.model
            if hasattr(model, 'client'):
                return model.objects.filter(client__user=self.request.user)
            elif hasattr(model, 'expert'):
                return model.objects.filter(expert__user=self.request.user)
            return model.objects.all()
        return None
    
    async def aget_object(self):
        obj = await super().aget_object()
        for permission in self.get_permissions():
            if hasattr(permission, "has_object_permission"):
                if not permission.has_object_permission(self.request, self, obj):
                    self.permission_denied(self.request)
        return obj
