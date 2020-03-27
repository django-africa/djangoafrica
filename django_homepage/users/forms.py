from django.contrib.auth import get_user_model, forms as uforms
from django import forms
from django.template.defaultfilters import slugify
from django_homepage.users.models import Profile, Badge

User = get_user_model()


class UserChangeForm(uforms.UserChangeForm):
    class Meta(uforms.UserChangeForm.Meta):
        model = User

class PasswordChangeForm(uforms.PasswordChangeForm):
    class Meta:
        model = User

class AuthenticationForm(uforms.AuthenticationForm):
    class Meta:
        model = User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['badges']

class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        exclude = ('slug',)

    def clean_title(self):
        if Badge.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Badge with this Name already exists.')

        return self.cleaned_data['title']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BadgeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(BadgeForm, self).save(commit=False)
        instance.title = self.cleaned_data['title']
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])
        if commit:
            instance.save()
        return instance

