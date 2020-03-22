# from django.contrib.auth import get_user_model
import hashlib
from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
User = get_user_model()

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


class Vote(models.Model):
    TYPES = (
        ("U", "Up"),
        ("D", "Down"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_user')
    type = models.CharField(choices=TYPES, max_length=1)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user


class ForumCategory(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_by')
    title = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=False)
    color = models.CharField(max_length=20, default="#999999")
    is_votable = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=1000)
    description = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)

    def get_topics(self):
        topics = Topic.objects.filter(category=self, status='Published')
        return topics

    def __str__(self):
        return self.title


# tags created for topic
class Tags(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=50, unique=True)

    def get_topics(self):
        topics = Topic.objects.filter(tags__in=[self], status='Published')
        return topics


# Badges created for topic
class Badge(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def get_users(self):
        user_profile = User.objects.filter(badges__in=[self])
        return user_profile


class Topic(models.Model):
    title = models.CharField(max_length=2000)
    description = RichTextUploadingField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, max_length=10)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    no_of_views = models.IntegerField(default='0')
    slug = models.SlugField(max_length=1000)
    tags = models.ManyToManyField(Tags)
    no_of_likes = models.IntegerField(default='0')
    votes = models.ManyToManyField(Vote)

    def get_comments(self):
        comments = Comment.objects.filter(topic=self, parent=None)
        return comments

    def get_all_comments(self):
        comments = Comment.objects.filter(topic=self)
        return comments

    def get_last_comment(self):
        comments = Comment.objects.filter(topic=self).order_by('-updated_on').first()
        return comments

    def get_total_of_votes(self):
        no_of_votes = self.up_votes_count() + self.down_votes_count()
        return no_of_votes

    def up_votes_count(self):
        return self.votes.filter(type="U").count()

    def down_votes_count(self):
        return self.votes.filter(type="D").count()

    def __str__(self):
        return str(self.title) if self.title else ''

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super(Topic, self).save(*args, **kwargs)


class Comment(models.Model):
    comment = models.TextField(null=True, blank=True)
    commented_by = models.ForeignKey(User, related_name="commented_by", on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, related_name="topic_comments", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", blank=True, null=True, related_name="comment_parent", on_delete=models.CASCADE)
    mentioned = models.ManyToManyField(User, related_name="mentioned_users")
    votes = models.ManyToManyField(Vote)

    def get_comments(self):
        comments = self.comment_parent.all()
        return comments

    def up_votes_count(self):
        return self.votes.filter(type="U").count()

    def down_votes_count(self):
        return self.votes.filter(type="D").count()


# user followed topics
class UserTopics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_followed = models.BooleanField(default=False)
    followed_on = models.DateField(null=True, blank=True)
    no_of_votes = models.IntegerField(default='0')
    no_of_down_votes = models.IntegerField(default='0')
    is_like = models.BooleanField(default=False)


# user activity
class Timeline(models.Model):
    content_type = models.ForeignKey(ContentType, related_name="content_type_timelines", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    namespace = models.CharField(max_length=250, default="default", db_index=True)
    event_type = models.CharField(max_length=250, db_index=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        index_together = [("content_type", "object_id", "namespace"), ]
        ordering = ['-created_on']


class Attachment(models.Model):
    file_prepend = "forum_topic/attachments/"
    uploaded_by = models.ForeignKey(User, related_name='attachments_user', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    attached_file = models.FileField(
        max_length=500, null=True, blank=True, upload_to=img_url)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
