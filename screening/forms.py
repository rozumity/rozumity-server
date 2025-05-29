from django.forms import ModelForm
from django.forms.widgets import TextInput
from screening.models import TagScreening


class TagScreeningAdminForm(ModelForm):
    class Meta:
        model = TagScreening
        fields = "__all__"
        widgets = {
            "color": TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super(TagScreeningAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["color"].widget = TextInput(
                attrs={"type": "color", "title": self.instance.color}
            )
