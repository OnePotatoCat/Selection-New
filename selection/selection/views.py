from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login")
    
    context = {
        "username" :request.user.username,
        "admin" : request.user.is_staff,
    }
    return HttpResponseRedirect("/selecting")