from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import DetailView, RedirectView, UpdateView, View
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from .models import *
from .models import Project, Contact, Skill
# from leaderboard.models import Project, Skill, Contact
from django.http import JsonResponse




class UserDetailView(LoginRequiredMixin, DetailView):

    model = Profile
    slug_field = "username"
    slug_url_kwarg = "username"
    template = 'users/profile_detail.html'

    def get_object(self):
        return get_object_or_404(Profile, username=self.kwargs['user.username', 'user.id'])

    def get_success_url(self):
        return redirect(reverse("users:view_profile", kwargs={"user_id": "self.user.id", "username": 'self.user.username'}))

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context

    # def post(self, request, *args, **kwargs):
    #     pass



user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = Profile
    fields = ["user"]

    def get_success_url(self):
        return redirect(reverse("users:view_profile", kwargs={"user_id": "self.user__id", "username": 'self.user_username'}))

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

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
    model = Profile

    def get_object(self):
        return get_object_or_404(Profile)

    def get_success_url(self):
        return redirect(reverse("users:view_profile", kwargs={'user_id': 'self.user.id', "username": 'self.user.username'}))

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
    model = Profile

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        return HttpResponse("myforum:topic_list")

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
            JsonResponse({'error': False, 'response': 'Successfully uploaded'})
            return self.get_success_url()
        else:
            return JsonResponse({'error': True, 'response': 'Please Upload Your Profile pic'})



user_profilepic_view = UserProfilePicView.as_view()

class ProfileDetailView(LoginRequiredMixin, DetailView):

    model = Profile
    slug_fields = "user_id, username"
    slug_url_kwarg = "user_id, username"

    def get_object(self):
        return get_object_or_404(Profile, user_id=self.kwargs['user_id'])

    def get_success_url(self):
        return reverse("myforum:topic_list")

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        user_profile = self.get_object()
        context['user_profile'] = user_profile
        user_topics = UserTopics.objects.filter(user=user_profile.user)
        context['user_topics'] = user_topics
        context['user_liked_topics'] = user_topics.filter(is_like=True)
        context['user_followed_topics'] = user_topics.filter(is_followed=True)
        context['user_created_topics'] = Topic.objects.filter(
            created_by=user_profile.user)
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




user_profile_view = ProfileDetailView.as_view()

class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    model = Profile
    fields = ["user"]

    def get_success_url(self):
        return reverse("users:view_profile", kwargs={"username": 'self.request.username', 'user_id': 'self.request.user.id'})

    def get_object(self):
        return Profile.objects.get(user=self.request.user)



user_update_view = UserUpdateView.as_view()


class UserContactUpdate(View):
    
    model = Contact
    fields = ["github_profile_link", "phone_number", "email_address"]
    git = "https://www.github.com/"
    
    def get_object(self):
        return get_object_or_404(Contact)

    def get_success_url(self):
        return reverse("users:view_profile")

    # def post(self, request, *args, **kwargs):
    #     contact = self.get_object()
    #     contact.github_profile_link = self.git + request.POST['github_username']
    #     contact.mobile_number = request.POST['mobile_number']
    #     contact.email_address = request.POST['email']
    #     contact.save()
    #     print ("contact link is" + contact.github_profile_link,
    #             "mobile number is" + contact.mobile_number,
    #             "email adress is " + contact.email_address)
    #     return HttpResponse("contact saved")
        
update_contact = UserContactUpdate.as_view()       

# def update_contact(request):
#     git = "https://www.github.com/"
#     if request.method=='POST':
#         contact = Contact.objects.get()
#         contact.github_profile_link = git + request.POST['github_username']
#         contact.mobile_number = request.POST['mobile_number']
#         contact.email_address = request.POST['email']
#         contact.save()
#         message = "Contact updated"
#         return HttpResponse(message)

class UserProjectUpdate(View):
    model = Project

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Project)
    
    def post(self, request):
        project = self.get_object()
        project.github_project_link = request.POST['github_project_link']
        project.project_url = request.POST['project_url']
        project.save()
        message = "Project updated"
        return HttpResponse(message)

project_update = UserProjectUpdate.as_view()

# def project_update(request):
#     if request.method=='POST':
#         project = get_object_or_404(Project,)
#         project.github_project_link = request.POST['github_project_link']
#         project.project_url = request.POST['project_url']
#         project.save()
#         message = "Project updated"
#         return HttpResponse(message)
    
           
# class UserSkillUpdate(View):
#     model : Skill

#     def get_object(self, *args, **kwargs):
#         return get_object_or_404(Skill)
    
#     def post(self, request):
#         skill = self.get_object()
#         skill.skill= request.POST['skill']
#         skill.years_of_experience = request.POST['duration']
#         skill.save()
#         message = "Contact updated"
#         return HttpResponse(message)

# skill_update = UserSkillUpdate.as_view()

def skill_update(request):
    print("Hey hello")
    if request.method=='POST':
        skill = Skill.objects.get()
        skill.skill= request.POST['skill']
        skill.years_of_experience = request.POST['duration']
        skill.save()
        message = "Contact updated"
        return HttpResponse(message)
