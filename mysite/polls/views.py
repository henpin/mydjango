# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic

from .models import Question

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'q_list'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class ResultView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(req, q_id):
    # get selected
    selected = get_object_or_404(Question, pk=q_id).choice_set.get(pk=req.POST["choice"])

    # incre vote index
    selected.votes += 1
    selected.save()

    return HttpResponseRedirect(reverse("results", args=(selected.id,) ))

def get_js(req, form_name):
    src = """
    window.onload = function(){ alert("goooood"); }
    """
    return HttpResponse(src, content_type="text/javascript")
