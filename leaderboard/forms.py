from django.forms import ModelForm
from .models import Project, Contact, Skill


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['business_name', 'github_profile_link', 'mobile_number', 'email_address']


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['business_name',"github_project_link", "project_url", "thumbnail"]


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ["skill", "years_of_experience"]
