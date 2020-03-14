from django.urls import path
from . import views

app_name = "myforum"
urlpatterns = [
    path('', views.TopicList.as_view(), name="topic_list"),
    path('topic/add/', views.TopicAdd.as_view(), name="new_topic"),
    path('topic/<slug:slug>/update/', views.TopicUpdateView.as_view(), name="topic_update"),
    path('topic/view/<slug:slug>/', views.TopicView.as_view(), name="view_topic"),
    path('topic/like/<slug:slug>/', views.TopicLike.as_view(), name="like_topic"),
    path('topic/follow/<slug:slug>/', views.TopicFollow.as_view(), name="follow_topic"),
    path('topic/votes/<slug:slug>/up/', views.TopicVoteUpView.as_view(), name="topic_vote_up"),
    path('topic/votes/<slug:slug>/down/', views.TopicVoteDownView.as_view(), name="topic_vote_down"),

    path('mentioned-users/<int:topic_id>/', views.get_mentioned_user, name="get_mentioned_user"),

    path('comment/delete/<int:comment_id>/',
        views.CommentDelete.as_view(), name="comment_delete"),
    path('comment/edit/<int:comment_id>/', views.CommentEdit.as_view(), name="comment_edit"),

    path('categories/', views.ForumCategoryList.as_view(), name="forum_categories"),
    path('tags/', views.ForumTagsList.as_view(), name="forum_tags"),
    path('badges/', views.ForumBadgeList.as_view(), name="forum_badges"),

    path('category/<slug:slug>/', views.ForumCategoryView.as_view(), name="forum_category_detail"),
    path('tags/<slug:slug>/', views.ForumTagsView.as_view(), name="forum_tags_detail"),

    path('comment/add/', views.CommentAdd.as_view(), name="new_comment"),
    path('comment/votes/<int:pk>/up/', views.CommentVoteUpView.as_view(), name="comment_vote_up"),
    path('comment/votes/<int:pk>/down/', views.CommentVoteDownView.as_view(), name="comment_vote_down"),

    path('dashboard/category/add/', views.CategoryAdd.as_view(), name="add_category"),
    path('dashboard/topics/delete/<slug:slug>/', views.TopicDeleteView.as_view(), name="delete_topic"),

    path('dashboard/', views.LoginView.as_view(), name="dashboard"),
    path('dashboard/login', views.DashboardView.as_view(), name="dashboard_login"),
    path('logout/', views.getout, name='out'),

    path('dashboard/category/list/', views.CategoryList.as_view(), name="categories"),
    path('dashboard/category/delete/<slug:slug>',
        views.CategoryDelete.as_view(), name="delete_category"),
    path('dashboard/category/edit/<slug:slug>',
        views.CategoryEdit.as_view(), name="edit_category"),
    path('dashboard/category/view/<slug:slug>',
        views.CategoryDetailView.as_view(), name="view_category"),

    path('dashboard/badge/list/', views.BadgeList.as_view(), name="badges"),
    path('dashboard/badge/add/', views.BadgeAdd.as_view(), name="add_badge"),
    path('dashboard/badge/delete/<slug:slug>', views.BadgeDelete.as_view(), name="delete_badge"),
    path('dashboard/badge/edit/<slug:slug>', views.BadgeEdit.as_view(), name="edit_badge"),
    path('dashboard/badge/view/<slug:slug>/', views.BadgeDetailView.as_view(), name="view_badge"),

        path('dashboard/users/list/', views.UserList.as_view(), name="users"),
    path('dashboard/users/delete/<int:user_id>/',
        views.DashboardUserDelete.as_view(), name="delete_user"),
    path('dashboard/users/status/<int:user_id>/',
        views.UserStatus.as_view(), name="user_status"),
    path('dashboard/users/view/<int:user_id>/',
        views.UserDetail.as_view(), name="user_detail"),
    path('dashboard/users/edit/<int:user_id>/',
        views.DashboardUserEdit.as_view(), name="edit_user"),
    path('dashboard/topics/list/', views.DashboardTopicList.as_view(), name="topics"),
    path('dashboard/topics/delete/<slug:slug>/', views.TopicDeleteView.as_view(), name="delete_topic"),
    path('dashboard/topic/view/<slug:slug>/', views.TopicDetail.as_view(), name="topic_detail"),
    path('dashboard/topic/status/<slug:slug>/', views.TopicStatus.as_view(), name="topic_status"),

    path('dashboard/change-password/', views.ChangePassword.as_view(), name="change_password"),

]
