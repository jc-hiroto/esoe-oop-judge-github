from .models import Profile

from django.forms import ModelForm


class ProfileUpdateGithubForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['github_account', 'github_repository']
