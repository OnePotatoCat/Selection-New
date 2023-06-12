from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse


class LoginForm(forms.Form):
    username = forms.CharField(label="username")
    password = forms.CharField(label="passowrd")


# Create your views here.
def index(request):
    return render(request, 'login/index.html' ,{
        "form" : LoginForm()
    })


def login_user(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print('hello')
            return redirect('selecting:newselection')            
            
        else:
            messages.success(request, ("Incorrect username or password. Please try again."))
            return redirect('login:login_user')
    else:
        return render(request, 'login/index.html',{
            "form" : LoginForm()
        })