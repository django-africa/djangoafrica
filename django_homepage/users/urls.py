from django.urls import path

from django_homepage.users.views import (
    user_redirect_view,
    user_update_view,
    user_detail_view,
    user_profilepic_view,
    user_profile_view,
    update_contact,
    skill_update,
    project_update
)

app_name = "users"
urlpatterns = [
    path('update_contact/', view=update_contact, name="update_contact"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),

    path('update_contact/', view=update_contact, name="update_contact"),
    # path('user/<slug:user_name>[a-zA-Z0-9_-]+.*?)/$', views.UserDetailView.as_view(), name="user_details"),
    path('profile/<int:user_id>/<str:username>', view=user_profile_view, name="view_profile"),
    # path('profile/$', views.UserProfileView.as_view(), name="user_profile"),
    
    path('update_project/', view=project_update, name="project_update"),
    path('update_skill/', view=skill_update, name="skill_update"),
    path('upload/profile-pic/', view=user_profilepic_view, name="user_profile_pic"),
    # path('send-mail/settings/$', views.UserSettingsView.as_view(), name="user_settings"),
]
