from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, RedirectView, UpdateView, View
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import *
from django.http import JsonResponse


User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['user_profile'] = self.get_object()
        user_topics = UserTopics.objects.filter(user=self.get_object())
        context['user_topics'] = user_topics
        context['user_liked_topics'] = user_topics.filter(is_like=True)
        context['user_followed_topics'] = user_topics.filter(is_followed=True)
        context['user_created_topics'] = Topic.objects.filter(
            created_by=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if not user_profile.send_mailnotifications:
            user_profile.send_mailnotifications = True
        else:
            user_profile.send_mailnotifications = False
        user_profile.save()
        return JsonResponse({'error': False, 'response': 'You have successfully uploaded the settings',
                             "send_mailnotifications": user_profile.send_mailnotifications})




user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']
            user_profile.save()
            return JsonResponse({'error': False, 'response': 'Successfully uploaded'})
        else:
            return JsonResponse({'error': True, 'response': 'Please Upload Your Profile pic'})


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("myforum:topic_list")


user_redirect_view = UserRedirectView.as_view()


class UserSettingsView(LoginRequiredMixin, View):
    model = User

    def get_object(self):
        return get_object_or_404(User)

    def get_success_url(self):
        return redirect(reverse("users:detail", kwargs={"username": self.username}))

    def post(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if not user_profile.send_mailnotifications:
            user_profile.send_mailnotifications = True
        else:
            user_profile.send_mailnotifications = False
        user_profile.save()
        return JsonResponse({'error': False, 'response': 'You have successfully updated the settings',
                             "send_mailnotifications": user_profile.send_mailnotifications})

class UserProfilePicView(LoginRequiredMixin, View):
    model = User

    def get_object(self):
        return get_object_or_404(UserProfile)

    def get_success_url(self):
        return redirect(reverse("users:detail", kwargs={"username": self.username}))


user_profilepic_view = UserProfilePicView.as_view()
