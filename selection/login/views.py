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
    if request.user.is_authenticated:
        return redirect('selecting:index')    

    if request.method == 'POST':
        # request.session["username"] = request.POST["username"]
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"{username} -- logined")
            user_dict = {
                'username': username,
                'full_name': user.get_full_name(),
                'first_name': user.get_short_name(),
            }
            request.session["user"] = user_dict
            return redirect('selecting:index')            
            
        else:
            messages.success(request, ("Incorrect username or password. Please try again."))
            return redirect('login:login_user')
    else:
        if "username" not in request.session:
            request.session["user"]=[]
        return render(request, 'login/index.html',{
            "form" : LoginForm()
        })
    

def logout_user(request):
    logout(request)
    request.session = [] 
    return redirect('login:login_user')

