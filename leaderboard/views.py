from django.shortcuts import render, HttpResponseRedirect,redirect
from django.urls import reverse
from .models import Contact,Project,Skill
from .forms import ContactForm, ProjectForm, SkillForm
# Create your views here.


def contact(request):
    form = ContactForm
    if request.method == 'POST' or None:
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        else:
            form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def index(request):
    return render(request, 'leaderboard.html')


def projects_view(request):
    form = ProjectForm()
    return render(request, 'projects.html', {'form':form})


def skills(request):
    form = SkillForm
    if request.method == 'POST'or None:
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project')
        else:
            form = SkillForm()
    return render(request, 'skills.html', {'form':form})


def projects(request):
    form = ProjectForm
    if request.method == 'POST'or None:
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project')
        else:
            form = ProjectForm()

    return render(request, 'projects.html', {'form': form})
