from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from djafforum.models import Topic, Comment, Badge, Timeline, Tags, ForumCategory
import hashlib
from datetime import datetime

STATUS = (
    ('Draft', 'Draft'),
    ('Published', 'Published'),
    ('Disabled', 'Disabled'),
)

USER_ROLES = (
    ('Admin', 'Admin'),
    ('Publisher', 'Publisher'),
)

def img_url(self, filename):
    hash_ = hashlib.md5()
    hash_.update(
        str(filename).encode('utf-8') + str(datetime.now()).encode('utf-8'))
    file_hash = hash_.hexdigest()
    return "%s%s/%s" % (self.file_prepend, file_hash, filename)

class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    file_prepend = "forum_user/profilepics/"
    used_votes = models.IntegerField(default='0')
    user_roles = models.CharField(choices=USER_ROLES, max_length=10, blank=True)
    # badges = models.ManyToManyField(Badge)
    profile_pic = models.FileField(
        max_length=500, null=True, upload_to=img_url, blank=True)
    send_mailnotifications = models.BooleanField(default=False, blank=True)

    # need to add social details for a user if we implement socail login

    def get_no_of_up_votes(self):
        user_topics = UserTopics.objects.filter(user=self.id)
        votes = 0
        for topic in user_topics:
            votes += topic.no_of_votes
        return votes

    def get_no_of_down_votes(self):
        user_topics = UserTopics.objects.filter(user=self.id)
        votes = 0
        for topic in user_topics:
            votes += topic.no_of_down_votes
        return votes

    def get_topics(self):
        topics = Topic.objects.filter(created_by=self.id)
        return topics

    def get_followed_topics(self):
        topics = UserTopics.objects.filter(user=self.id, is_followed=True)
        topics = Topic.objects.filter(id__in=topics.values_list('topic', flat=True))
        return topics

    def get_liked_topics(self):
        topics = UserTopics.objects.filter(user=self.id, is_like=True)
        topics = Topic.objects.filter(id__in=topics.values_list('topic', flat=True))
        return topics

    def get_timeline(self):
        timeline = Timeline.objects.filter(user=self.id).order_by('-created_on')
        return timeline

    def get_user_topic_tags(self):
        tags = Tags.objects.filter(id__in=self.get_topics().values_list('tags', flat=True))
        return tags

    def get_user_topic_categories(self):
        categories = ForumCategory.objects.filter(id__in=self.get_topics().values_list('category', flat=True))
        return categories
        # return []

    def get_user_suggested_topics(self):
        categories = ForumCategory.objects.filter(id__in=self.get_topics().values_list('category', flat=True))
        topics = Topic.objects.filter(category__id__in=categories.values_list('id', flat=True))
        return topics
        # return []

    # def get_topic_users(self):
    #     comment_user_ids = Comment.objects.filter(commented_by=True).values_list('commented_by', flat=True)
    #     liked_users_ids = UserTopics.objects.filter(is_like=True).values_list('user', flat=True)
    #     followed_users = UserTopics.objects.filter(is_followed=True).values_list('user', flat=True)
    #     all_users = (list(comment_user_ids) + list(liked_users_ids) + list(followed_users) + [self.id])
    #     users = User.objects.filter(id__in=set(all_users))
    #     return users

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

class UserTopics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_topic')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_topic')
    is_followed = models.BooleanField(default=False)
    followed_on = models.DateField(null=True, blank=True)
    no_of_votes = models.IntegerField(default='0')
    no_of_down_votes = models.IntegerField(default='0')
    is_like = models.BooleanField(default=False)
