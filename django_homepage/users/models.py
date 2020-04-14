import hashlib
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from phone_field import PhoneField

from djafforum.models import Topic, Timeline, Tags, ForumCategory

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


class Badge(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def get_users(self):
        user_profile = Profile.objects.filter(badges__in=[self])
        return user_profile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    file_prepend = "forum_user/profilepics/"
    used_votes = models.IntegerField(default='0')
    user_roles = models.CharField(choices=USER_ROLES, max_length=10, blank=True)
    badges = models.ManyToManyField(Badge)
    profile_pic = models.FileField(max_length=500, null=True, upload_to=img_url, blank=True)
    send_mailnotifications = models.BooleanField(default=False, blank=True)

    # need to add social details for a user if we implement socail login

    def get_no_of_up_votes(self):
        user_topics = UserTopics.objects.filter(user=self.user)
        votes = 0
        for topic in user_topics:
            votes += topic.no_of_votes
        return votes

    def get_no_of_down_votes(self):
        user_topics = UserTopics.objects.filter(user=self.user)
        votes = 0
        for topic in user_topics:
            votes += topic.no_of_down_votes
        return votes

    def get_topics(self):
        topics = Topic.objects.filter(created_by=self.user)
        return topics

    def get_followed_topics(self):
        topics = UserTopics.objects.filter(user=self.user, is_followed=True)
        topics = Topic.objects.filter(id__in=topics.values_list('topic', flat=True))
        return topics

    def get_liked_topics(self):
        topics = UserTopics.objects.filter(user=self.user, is_like=True)
        topics = Topic.objects.filter(id__in=topics.values_list('topic', flat=True))
        return topics

    def get_timeline(self):
        timeline = Timeline.objects.filter(user=self.user).order_by('-created_on')
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

    def get_absolute_url(self):
        return reverse("users:view_profile", kwargs={"user_id": self.user.id, "username": self.user.username})

    class Meta:
        db_table = 'profile'


class Contact(models.Model):
    business_name = models.OneToOneField(Profile, max_length=500, on_delete=models.CASCADE)
    github_profile_link = models.URLField(help_text="Your github profile link")
    mobile_number = PhoneField(blank=False, help_text='Contact phone number')
    email_address = models.EmailField()

    def __str__(self):
        return self.business_name


class Skill(models.Model):
    choices = (
        ('junior dev', '1-2years'),
        ('senior dev', '3-5years'),
        ('expert', '6years and above'),
    )
    skill = models.CharField(max_length=350)
    years_of_experience = models.CharField(choices=choices, max_length=350)

    def __str__(self):
        return self.skill

class Project(models.Model):
    github_project_link = models.URLField(help_text="Link to your project on Github")
    project_url = models.URLField(help_text="Project URL")
    thumbnail = models.ImageField()

    def __str__(self):
        return self.github_project_link

    # Auto-create Profile model on User model creation


@receiver(post_save, sender=get_user_model())
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class UserTopics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_user')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_topic')
    is_followed = models.BooleanField(default=False)
    followed_on = models.DateField(null=True, blank=True)
    no_of_votes = models.IntegerField(default='0')
    no_of_down_votes = models.IntegerField(default='0')
    is_like = models.BooleanField(default=False)
