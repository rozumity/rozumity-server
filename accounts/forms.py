from django import forms
from django.contrib.auth import get_user_model


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(label='E-Mail')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    is_client = forms.BooleanField(label='Is Client', required=False)
    is_staff = forms.BooleanField(label='Is Staff', required=False)
    is_expert = forms.BooleanField(label='Is Expert', required=False)
    is_superuser = forms.BooleanField(label='Is Superuser', required=False)
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'is_client', 'is_expert', 'is_superuser')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
           user.save()

        return user
