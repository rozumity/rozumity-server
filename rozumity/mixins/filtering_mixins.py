class OwnedList:
    def get_queryset(self):
        if self.request.user.is_authenticated:
            model = self.get_serializer_class().Meta.model
            if hasattr(model, 'client'):
                return model.objects.filter(client__user=self.request.user)
            elif hasattr(model, 'expert'):
                return model.objects.filter(expert__user=self.request.user)
            return model.objects.all()
        return None
