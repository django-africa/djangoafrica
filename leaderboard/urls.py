from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path("", views.index, name='index'),
    path("contact/", views.contact, name="contact"),
    path("projects/", views.projects, name="project"),
    path("skills/", views.skills, name="skill"),
]
