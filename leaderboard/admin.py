from django.contrib import admin
from .models import Contact, Project, Skill

# Register your models here.
admin.site.register(Skill)
admin.site.register(Contact)
admin.site.register(Project)
