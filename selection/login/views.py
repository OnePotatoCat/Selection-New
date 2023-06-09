from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Passowrd")


# Create your views here.
def index(request):
    return render(request, "login/index.html" ,{
        "form" : LoginForm()
    })


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # user = authenticate(request, username=form.username, password=form.password)
        if form.username is not None:
            print(form.username)
            # return redirect('home')  # Replace 'home' with the name of your desired homepage URL pattern
        else:
            # Invalid username or password
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html',{})