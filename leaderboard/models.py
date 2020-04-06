from django.db import models
from phone_field import PhoneField
# Create your models here.


class Contact(models.Model):
    business_name = models.CharField(max_length=500)
    github_profile_link = models.URLField(help_text="Your github profile link")
    mobile_number = PhoneField(blank=False, help_text='Contact phone number')
    email_address = models.EmailField()

    def __str__(self):
        return self.business_name


class Project(models.Model):
    business_name = models.ForeignKey(Contact, on_delete=models.CASCADE)
    github_project_link = models.URLField(help_text="Link to your project on Github")
    project_url = models.URLField(help_text="Project URL")
    thumbnail = models.ImageField()

    def __str__(self):
        return self.github_project_link


class Skill(models.Model):
    business_name = models.ForeignKey(Contact, on_delete=models.CASCADE)
    skill = models.CharField(max_length=500)
    years_of_experience = models.IntegerField(default=0)

    def __str__(self):
        return self.skill
