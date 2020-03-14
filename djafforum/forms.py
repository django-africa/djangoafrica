from django.contrib.auth import get_user_model
from django import forms
from .models import ForumCategory, Badge, Topic, Comment
from django.template.defaultfilters import slugify


User = get_user_model()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = ForumCategory
        exclude = ('slug', 'created_by')

    def clean_title(self):
        if ForumCategory.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Category with this Name already exists.')

        return self.cleaned_data['title']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        instance.created_by = self.user
        instance.title = self.cleaned_data['title']
        if str(self.cleaned_data['is_votable']) == 'True':
            instance.is_votable = True
        else:
            instance.is_votable = False
        if str(self.cleaned_data['is_active']) == 'True':
            instance.is_active = True
        else:
            instance.is_active = False
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])

        if commit:
            instance.save()
        return instance


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


class TopicForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields["category"].widget.attrs = {"class": "form-control select2"}
        self.fields["title"].widget.attrs = {"class": "form-control"}
        self.fields["tags"].widget.attrs = {"class": "form-control tags"}

    tags = forms.CharField(required=False)

    class Meta:
        model = Topic
        fields = ("title", "category", "description", "tags")

    def clean_title(self):
        if Topic.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Topic with this Name already exists.')

        return self.cleaned_data['title']


    def save(self, commit=True):
        instance = super(TopicForm, self).save(commit=False)
        instance.title = self.cleaned_data['title']
        instance.description = self.cleaned_data['description']
        instance.category = self.cleaned_data['category']
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])
            instance.created_by = self.user
            instance.status = 'Published'
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment', 'topic')

    def clean_comment(self):
        if self.cleaned_data['comment']:
            return self.cleaned_data['comment']
        raise forms.ValidationError('This field is required')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.comment = self.cleaned_data['comment']
        instance.topic = self.cleaned_data['topic']
        if not self.instance.id:
            instance.commented_by = self.user
            if 'parent' in self.cleaned_data.keys() and self.cleaned_data['parent']:
                instance.parent = self.cleaned_data['parent']
        if commit:
            instance.save()
        return instance
