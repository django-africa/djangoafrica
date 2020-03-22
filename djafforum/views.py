from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm

from .models import *
from .forms import *
from .mixins import *
from users.forms import UserChangeForm
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

User = get_user_model()

def timeline_activity(user, content_object, namespace, event_type):
    Timeline.objects.create(
        user=user,
        content_object=content_object,
        namespace=namespace,
        event_type=event_type,
    )

def getout(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('myforum:topic_list'))
    else:
        logout(request)
        return HttpResponseRedirect(reverse('myforum:dashboard'))

class TopicUpdateView(CanUpdateTopicMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "forum/new_topic.html"

    def get_initial(self):
        initital = super(TopicUpdateView, self).get_initial();
        topic = self.get_object()
        tags = [tag.title for tag in topic.tags.all()]
        initital.update({
            "tags": ",".join(tags)
        })
        return initital

    def form_valid(self, form):
        topic = self.get_object()
        old_tags = [tag.title for tag in topic.tags.all()]
        topic = form.save()
        tags_text = form.cleaned_data['tags']
        if tags_text:
            new_tags = tags_text.split(',')
            remove_tags = set(new_tags) - set(old_tags)
            for tag in new_tags:
                tag_slug = slugify(tag)
                if not Tags.objects.filter(slug=tag_slug).exists():
                    tag = Tags.objects.create(slug=tag_slug, title=tag)
                    topic.tags.add(tag)
                else:
                    tag = Tags.objects.filter(slug=tag_slug).first()
                    if tag.title in remove_tags:
                        topic.remove(tag)
                    else:
                        topic.tags.add(tag)
        topic.save()
        return reverse_lazy('myforum:topic_list')

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'errors': form.errors})


class TopicList(ListView):
    template_name = 'forum/topic_list.html'
    context_object_name = "topic_list"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            query = Q(status='Published')|Q(created_by=self.request.user)
        else:
            query = Q(status='Published')
        queryset = Topic.objects.filter(query).order_by('-created_on')
        return queryset

class TopicAdd(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = "forum/new_topic.html"

    def get_form_kwargs(self):
        kwargs = super(TopicAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        topic = form.save()
        if self.request.POST['sub_category']:
            topic.category_id = self.request.POST['sub_category']
        topic.save()
        if 'tags' in form.cleaned_data.keys() and form.cleaned_data['tags']:
            for tag in form.cleaned_data['tags'].split(','):
                if not Tags.objects.filter(slug=slugify(tag)):
                    each = Tags.objects.create(slug=slugify(tag), title=tag)
                    topic.tags.add(each)
                else:
                    each = Tags.objects.filter(slug=slugify(tag)).first()
                    topic.tags.add(each)

        timeline_activity(user=self.request.user, content_object=self.request.user,
                          namespace='created topic on', event_type="topic-create")

        return redirect(reverse("myforum:topic_list"))

    def get_context_data(self, **kwargs):
        context = super(TopicAdd, self).get_context_data(**kwargs)
        form = TopicForm(self.request.GET)
        context['form'] = form
        context['status'] = STATUS
        context['categories'] = ForumCategory.objects.filter(
            is_active=True, is_votable=True, parent=None)
        context['sub_categories'] = ForumCategory.objects.filter(
            is_active=True, is_votable=True).exclude(parent=None)
        return context

class TopicView(TemplateView):
    template_name = 'forum/view_topic.html'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['topic'] = self.get_object()
        user_profile = get_object_or_404(User, username=self.request.user.username)
        context['user_profile'] = user_profile
        suggested_topics = Topic.objects.filter(
            category=self.get_object().category).exclude(id=self.get_object().id)
        job_url = 'http://' + self.request.META['HTTP_HOST'] + reverse(
            'myforum:view_topic', kwargs={'slug': self.get_object().slug})
        try:
            minified_url = google_mini(job_url, settings.MINIFIED_URL)
        except:
            minified_url = job_url

        context['minified_url'] = minified_url
        context['suggested_topics'] = suggested_topics
        return context


class TopicDeleteView(CanUpdateTopicMixin, DeleteView):
    model = Topic
    template_name = "forum/topic_delete.html"
    success_url = reverse_lazy("myforum:topic_list")

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = super(TopicDeleteView, self).get_object()
        return self.object

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({"error": False, "message": "deleted"})
        else:
            return super(TopicDeleteView, self).delete(request, *args, **kwargs)


class ForumCategoryList(ListView):
    queryset = ForumCategory.objects.filter(
        is_active=True, is_votable=True).order_by('-created_on')
    template_name = 'forum/categories.html'
    context_object_name = "categories"
    paginate_by = '10'

class ForumCategoryView(ListView):
    template_name = 'forum/topic_list.html'

    def get_queryset(self, queryset=None):
        if self.request.user.is_authenticated:
            query = Q(status="Published")|Q(created_by=self.request.user)
        else:
            query = Q(status="Published")
        category = get_object_or_404(ForumCategory, slug=self.kwargs.get("slug"))
        topics = category.topic_set.filter(query)
        return topics


class CategoryList(AdminMixin, ListView):
    model = ForumCategory
    template_name = 'dashboard/categories.html'
    context_object_name = 'categories_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        categories_list = ForumCategory.objects.filter(parent=None)
        context['categories_list'] = categories_list
        return context

    def post(self, request, *args, **kwargs):
        categories_list = self.model.objects.all()

        if request.POST.get('is_active') == 'True':
            categories_list = categories_list.filter(is_active=True)
        if request.POST.get('search_text', ''):
            categories_list = categories_list.filter(
                title__icontains=request.POST.get('search_text')
            )
        return render(request, self.template_name, {'categories_list': categories_list})

class CategoryDetailView(AdminMixin, DetailView):
    model = ForumCategory
    template_name = 'dashboard/view_category.html'
    slug_field = "slug"
    context_object_name = 'category'

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])

class CategoryAdd(AdminMixin, CreateView):
    model = ForumCategory
    form_class = CategoryForm
    template_name = "dashboard/category_add.html"
    success_url = reverse_lazy('myforum:dashboard')

    def get_form_kwargs(self):
        kwargs = super(CategoryAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        menu = form.save()
        if self.request.POST.get('parent'):
            menu.parent_id = self.request.POST.get('parent')
            menu.save()
        return reverse_lazy('myforum:topic_list')

    def get_success_url(self):
        return redirect(reverse('myforum:categories'))

    def get_context_data(self, **kwargs):
        context = super(CategoryAdd, self).get_context_data(**kwargs)
        form = CategoryForm(self.request.GET)
        menus = ForumCategory.objects.filter(parent=None)
        context['form'] = form
        context['menus'] = menus
        return context


class CategoryDelete(AdminMixin, DeleteView):
    model = ForumCategory
    slug_field = 'slug'
    template_name = "dashboard/categories.html"
    success_url = reverse_lazy('myforum:dashboard')

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('myforum:categories'))

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return reverse_lazy('myforum:categories')


class CategoryEdit(AdminMixin, UpdateView):
    model = ForumCategory
    form_class = CategoryForm
    template_name = "dashboard/category_add.html"
    context_object_name = 'category'

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super(CategoryEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        menu = form.save()
        if self.request.POST.get('parent'):
            menu.parent_id = self.request.POST.get('parent')
            menu.save()
        return reverse_lazy('myforum:categories')

    def get_success_url(self):
        return redirect(reverse('myforum:categories'))

    def get_context_data(self, **kwargs):
        context = super(CategoryEdit, self).get_context_data(**kwargs)
        form = CategoryForm(self.request.GET)
        menus = ForumCategory.objects.filter(parent=None)
        context['form'] = form
        context['menus'] = menus
        return context

class DashboardTopicList(AdminMixin, ListView):
    template_name = 'dashboard/topics.html'
    context_object_name = "topic_list"

    def get_queryset(self):
        queryset = Topic.objects.all()
        search_text = self.request.POST.get('search_text')
        if search_text:
            queryset = queryset.filter(
                Q(title__icontains=search_text) | Q(created_by__username__icontains=search_text)
            )
        return queryset


class BadgeDetailView(AdminMixin, DetailView):
    model = Badge
    template_name = 'dashboard/view_badge.html'
    slug_field = "slug"
    context_object_name = 'badge'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])


class BadgeAdd(AdminMixin, CreateView):
    model = Badge
    form_class = BadgeForm
    template_name = "dashboard/badge_add.html"

    def get_form_kwargs(self):
        kwargs = super(BadgeAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        data = {'error': False, 'response': 'Successfully Created Badge'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('myforum:badges'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(BadgeAdd, self).get_context_data(**kwargs)
        form = BadgeForm(self.request.GET)
        context['form'] = form
        return context


class BadgeDelete(AdminMixin, DeleteView):
    model = Badge
    slug_field = 'slug'
    template_name = "dashboard/badges.html"
    success_url = '/forum/dashboard/badges/'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('myforum:badges'))

    def post(self, request, *args, **kwargs):
        badge = self.get_object()
        badge.delete()
        return JsonResponse({'error': False, 'response': 'Successfully Deleted Badge'})


class BadgeEdit(AdminMixin, UpdateView):
    model = Badge
    template_name = "dashboard/badge_add.html"
    form_class = BadgeForm
    context_object_name = 'badge'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super(BadgeEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        data = {'error': False, 'response': 'Successfully Edited Badge'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('myforum:badges'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(BadgeEdit, self).get_context_data(**kwargs)
        form = BadgeForm(self.request.GET)
        context['form'] = form
        return context

class BadgeList(AdminMixin, ListView):
    model = Badge
    template_name = 'dashboard/badges.html'
    context_object_name = 'badges_list'

    def get_context_data(self, **kwargs):
        context = super(BadgeList, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        badges_list = self.model.objects.all()
        if request.POST.get('search_text', ''):
            badges_list = badges_list.filter(
                Q(title__icontains=request.POST.get('search_text')))
        per_page = request.POST.get("filter_per_page") if request.POST.get(
            "filter_per_page") else 10
        return render(request, self.template_name, {'badges_list': badges_list,
                                                    "per_page": per_page})

class UserList(AdminMixin, ListView):
    model = User
    template_name = 'dashboard/users.html'
    context_object_name = 'users_list'
    queryset = User.objects.filter()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        users_list = self.model.objects.all()
        if request.POST.get('search_text', ''):
            users_list = list(set(users_list.filter(
                user__email__icontains=request.POST.get('search_text')
            ) | users_list.filter(
                user__username__icontains=request.POST.get('search_text')
            )))
        per_page = request.POST.get("filter_per_page") if request.POST.get(
            "filter_per_page") else 10
        return render(request, self.template_name, {'users_list': users_list,
                                                    "per_page": per_page})


class CommentVoteUpView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        vote = comment.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="U")
            comment.votes.add(vote)
            comment.save()
            status = "up"
        elif vote and vote.type == "D":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})


class CommentVoteDownView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        vote = comment.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="D")
            comment.votes.add(vote)
            comment.save()
            status = "down"
        elif vote and vote.type == "U":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})



class CommentAdd(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = CommentForm
    template_name = 'forum/view_topic.html'

    def get_form_kwargs(self):
        kwargs = super(CommentAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        comment = form.save()
        if self.request.POST['parent']:
            comment.parent_id = self.request.POST['parent']
            comment.save()
        if self.request.POST.get('mentioned_user', False):
            data = self.request.POST.get('mentioned_user')
            comment.mentioned = comment_mentioned_users_list(data)
            comment.save()

        # for user in comment.topic.get_topic_users():
        #     mto = [user.user.email]
        #     c = {'comment': comment, "user": user.user,
        #          'topic_url': settings.HOST_URL+reverse('myforum:view_topic', kwargs={'slug': comment.topic.slug}),
        #          "HOST_URL": settings.HOST_URL}
        #     t = loader.get_template('emails/comment_add.html')
        #     subject = "New Comment For The Topic " + (comment.topic.title)
        #     rendered = t.render(c)
        #     mfrom = settings.DEFAULT_FROM_EMAIL
        #     Memail(mto, mfrom, subject, rendered, email_template_name=None, context=None)

        # for user in comment.mentioned.all():
        #     mto = [user.user.email]
        #     c = Context({'comment': comment, "user": user.user,
        #                  'topic_url': settings.HOST_URL+reverse('myforum:view_topic', kwargs={'slug': comment.topic.slug}),
        #                  "HOST_URL": settings.HOST_URL})
        #     t = loader.get_template('emails/comment_mentioned.html')
        #     subject = "New Comment For The Topic " + (comment.topic.title)
        #     rendered = t.render(c)
        #     mfrom = settings.DEFAULT_FROM_EMAIL
        #     Memail(mto, mfrom, subject, rendered)

        timeline_activity(user=self.request.user, content_object=comment,
                          namespace='commented for the', event_type="comment-create")

        data = {'error': False, 'response': 'Successfully Created Topic'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('myforum:signup'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(CommentAdd, self).get_context_data(**kwargs)
        form = CommentForm(self.request.GET)
        context['form'] = form
        return context


class CommentEdit(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "dashboard/edit_user.html"
    form_class = CommentForm
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def form_valid(self, form):
        comment = self.get_object()
        if self.request.user == comment.commented_by:
            self.get_object().mentioned.all().delete()
            comment = form.save()
            if self.request.POST['parent']:
                comment.parent_id = self.request.POST['parent']
                comment.save()
            if self.request.POST.get('mentioned_user', False):
                data = self.request.POST.get('mentioned_user')
                comment.mentioned = comment_mentioned_users_list(data)
                comment.save()
            timeline_activity(user=self.request.user, content_object=comment,
                              namespace='commented for the', event_type="comment-create")
            data = {'error': False, 'response': 'Successfully Edited User'}
        else:
            data = {
                'error': True, 'response': 'Only Commented User Can edit this comment'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('myforum:users'))

    def get_form_kwargs(self):
        kwargs = super(CommentEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(CommentEdit, self).get_context_data(**kwargs)
        form = CommentForm(self.request.GET)
        context['form'] = form
        return context


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    slug_field = 'comment_id'
    template_name = "forum/comment_delete.html"

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def get_success_url(self):
        return redirect(reverse_lazy("myforum:view_topic", 'topic.slug'))

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if self.request.user == comment.commented_by:
            comment.delete()
            return JsonResponse({'error': False, 'response': 'Successfully Deleted Your Comment'})
        else:
            return JsonResponse({'error': False, 'response': 'Only commented user can delete this comment'})


class TopicLike(LoginRequiredMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('myforum:categories'))

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        user_topics = UserTopics.objects.filter(user=request.user, topic=topic)
        if user_topics:
            user_topic = user_topics[0]
        else:
            user_topic = UserTopics.objects.create(
                user=request.user, topic=topic)
        if user_topic.is_like:
            user_topic.is_like = False
            topic.no_of_likes = topic.no_of_likes - 1
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='unlike the', event_type="unlike-topic")
        else:
            user_topic.is_like = True
            topic.no_of_likes = topic.no_of_likes + 1
            timeline_activity(
                user=self.request.user, content_object=topic, namespace='like the', event_type="like-topic")
        user_topic.save()
        topic.save()

        return redirect(reverse("myforum:topic_list"))


class ForumTagsList(ListView):
    queryset = Tags.objects.filter()
    template_name = 'forum/tags.html'
    context_object_name = "tags"
    paginate_by = '10'

    def post(self, request, *args, **kwargs):
        tags = self.queryset
        if str(request.POST.get('alphabet_value')) != 'all':
            tags = tags.filter(
                title__istartswith=request.POST.get('alphabet_value'))
        return render(request, self.template_name, {'tags': tags})


class ForumBadgeList(ListView):
    queryset = Tags.objects.filter()
    template_name = 'forum/badges.html'
    context_object_name = "badges_list"
    paginate_by = '10'

    def post(self, request, *args, **kwargs):
        tags = self.queryset
        if str(request.POST.get('alphabet_value')) != 'all':
            tags = tags.filter(
                title__istartswith=request.POST.get('alphabet_value'))
        return render(request, self.template_name, {'tags': tags})



class ForumTagsView(TemplateView):
    template_name = 'forum/topic_list.html'

    def get_context_data(self, **kwargs):
        tag = get_object_or_404(Tags, slug=kwargs.get("slug"))
        context = super(ForumTagsView, self).get_context_data(**kwargs)
        topics = tag.get_topics()
        context['topic_list'] = topics
        return context


class TopicDetail(AdminMixin, TemplateView):
    template_name = 'dashboard/view_topic.html'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context['topic'] = self.get_object()
        return context


class TopicStatus(AdminMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    @csrf_protect
    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.status == 'Draft':
            topic.status = 'Published'
        elif topic.status == 'Published':
            topic.status = 'Draft'
        else:
            topic.status = 'Disabled'
        topic.save()
        return JsonResponse({'error': False, 'response': 'Successfully Updated Topic Status'})


class TopicFollow(LoginRequiredMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        user_topics = UserTopics.objects.filter(user=self.request.user, topic=topic)
        if user_topics:
            user_topic = user_topics[0]
        else:
            user_topic = UserTopics.objects.create(
                user=request.user, topic=topic)
        if user_topic.is_followed:
            user_topic.is_followed = False
            user_topic.followed_on = datetime.now()
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='unfollow the', event_type="unfollow-topic")
        else:
            user_topic.is_followed = True
            user_topic.followed_on = datetime.now()
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='follow the', event_type="follow-topic")
        user_topic.save()
        return JsonResponse({'error': False, 'response': 'Successfully Followed the topic',
                             'is_followed': user_topic.is_followed})


class TopicVoteUpView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, slug=kwargs.get("slug"))
        vote = topic.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="U")
            topic.votes.add(vote)
            topic.save()
            status = "up"
        elif vote and vote.type == "D":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})


class TopicVoteDownView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, slug=kwargs.get("slug"))
        vote = topic.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="D")
            topic.votes.add(vote)
            topic.save()
            status = "down"
        elif vote and vote.type == "U":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})

def get_topic_users(self):
        comment_user_ids = Comment.objects.filter(topic=self).values_list('commented_by', flat=True)
        liked_users_ids = UserTopics.objects.filter(topic=self, is_like=True).values_list('user', flat=True)
        followed_users = UserTopics.objects.filter(topic=self, is_followed=True).values_list('user', flat=True)
        all_users = list(comment_user_ids) + list(liked_users_ids) + list(followed_users) + [self.created_by.id]
        users = UserProfile.objects.filter(user_id__in=set(all_users))
        return users

def get_mentioned_user(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'GET':
        topic_users = topic.get_topic_users()
        list_data = []
        for user in topic_users:
            data = {}
            data['username'] = user.email.split('@')[0]
            # data['avatar'] = user.profile_pic.url if user.profile_pic else ''
            data['email'] = user.email
            list_data.append(data)
    return JsonResponse({'data': list_data})


def comment_mentioned_users_list(data):
    mentioned_users = data.split(',')
    mentioned_users_list = [user.strip('@') for user in mentioned_users]
    result = User.objects.filter(username__in=mentioned_users_list)
    return result

class DashboardView(AdminMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

class LoginView(FormView):
    template_name = 'dashboard/dashboard_login.html'
    form_class = AuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('myforum:dashboard')
            else:
                return redirect('myforum:topic_list')
        return super(LoginView, self).dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser:
            login(self.request, form.get_user())
            data = {
                'error': False,
                'response': 'You have successfully logged into the dashboard'
            }
        else:
            data = {
                'error': True,
                'response': 'You dont have access to login to dashboard'
            }
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

class UserList(AdminMixin, ListView):
    model = User
    template_name = 'dashboard/users.html'
    context_object_name = 'users_list'
    queryset = User.objects.filter()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        users_list = self.model.objects.all()
        if request.POST.get('search_text', ''):
            users_list = list(set(users_list.filter(
                user__email__icontains=request.POST.get('search_text')
            ) | users_list.filter(
                user__username__icontains=request.POST.get('search_text')
            )))
        per_page = request.POST.get("filter_per_page") if request.POST.get(
            "filter_per_page") else 10
        return render(request, self.template_name, {'users_list': users_list,
                                                    "per_page": per_page})

class DashboardUserDelete(AdminMixin, DeleteView):
    model = User
    template_name = "dashboard/topic.html"
    slug_name = "user_id"

    def get_success_url(self):
        return redirect(reverse('myforum:users'))

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return JsonResponse({'error': False, 'response': 'Successfully Deleted User'})

class UserStatus(AdminMixin, View):
    model = User
    slug_name = "user_id"

    def get_success_url(self):
        return redirect(reverse('myforum:users'))

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return JsonResponse({'error': False, 'response': 'Successfully Updated User Status'})


class UserDetail(AdminMixin, TemplateView):
    template_name = 'dashboard/view_user.html'

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        context['user_profile'] = get_object_or_404(
            User, user=self.get_object())
        user_topics = UserTopics.objects.filter(user=self.get_object())
        context['user_topics'] = user_topics
        context['user_liked_topics'] = user_topics.filter(is_like=True)
        context['user_followed_topics'] = user_topics.filter(is_followed=True)
        context['user_created_topics'] = Topic.objects.filter(
            created_by=self.get_object())
        return context

class DashboardUserEdit(AdminMixin, UpdateView):
    model = User
    template_name = "dashboard/edit_user.html"
    form_class = UserChangeForm
    context_object_name = 'user_profile'

    def get_object(self):
        return get_object_or_404(User, user_id=self.kwargs['user_id'])

    def get_form_kwargs(self):
        kwargs = super(DashboardUserEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        user_profile = form.save()
        user_profile.badges.clear()
        user_profile.badges.add(*form.cleaned_data['badges'])
        data = {'error': False, 'response': 'Successfully Edited User'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('myforum:users'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(DashboardUserEdit, self).get_context_data(**kwargs)
        form = UserProfileForm(self.request.GET)
        badges = Badge.objects.filter()
        context['form'] = form
        context['badges'] = badges
        context['user_profile'] = self.get_object()
        return context

class ChangePassword(AdminMixin, FormView):
    template_name = 'dashboard/change_password.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        user = self.request.user
        if not check_password(self.request.POST['oldpassword'], user.password):
            return JsonResponse({
                'error': True,
                'response': {'oldpassword': 'Invalid old password'}
            })
        if self.request.POST['newpassword'] != self.request.POST['retypepassword']:
            return JsonResponse({
                'error': True,
                'response': {'newpassword': 'New password and Confirm Passwords did not match'}
            })
        user.set_password(self.request.POST['newpassword'])
        user.save()
        return JsonResponse({'error': False, 'message': 'Password changed successfully'})

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})
