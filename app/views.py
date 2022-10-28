import email
from django import forms
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist

# from .forms import ContactForm
from django.http import JsonResponse
import json
from .forms import FriendForm, NewUserForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .models import *


def index(request):
    # if request.user.is_anonymous:
    #     return redirect("/login.html")l
    return html(request, "index")


def add_friend_form(request):
    me = User.objects.get(username=request.user.get_username())
    if request.method == "POST":
        print('friend',request.method)
        friend_form = FriendForm(request.POST)
        if friend_form.is_valid():
            friend_id = friend_form.cleaned_data['friendname']
            print('friend_id:',friend_id,User.objects.filter(username=friend_id).exists())
            if User.objects.filter(username=friend_id).exists():
                response_data={}
                friend = User.objects.get(username=friend_id)
                if friend == me:
                    # raise forms.ValidationError("f")
                    print('F')
                    response_data["result"] = "Failed!"
                    response_data["message"] = "Already exists!"
                elif Friend.objects.filter(person1=me,person2=friend).exists() or Friend.objects.filter(person1=friend,person2=me).exists():
                    print("f")
                    response_data["result"] = "Failed!"
                    response_data["message"] = "Already exists!"
                else:
                    f = Friend(person1=me,person2=friend)
                    f1 = Friend(person1=friend,person2=me)

                    print('hi')
                    f.save()
                    f1.save()
                    response_data["result"] = "Success!"
                    response_data["message"] = 'You"re saved'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

def loop_array(request):
    arr=['C','O','D','E','S','P','E','E','D','Y']

    return HttpResponse(json.dumps({"result":arr}), content_type="application/json")


# @csrf_exempt
def registration_form(request):
    print("request:", request.method, request.POST)
    # form = NewUserForm()
    is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    print("is ajax", is_ajax, request.POST)
    if request.method == "POST" and is_ajax:
        form = NewUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.save()
            return JsonResponse({"email": email}, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

    return render(request, "login.html", {"form": form})


# @csrf_exempt
def login_request(request):
    print("login req:", request)
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # user = authenticate(request, username=username, password=password)
        # print("user auth:", user)
        try:
            username = User.objects.get(username=username).username
        except User.DoesNotExist:
            return HttpResponse("Invalid")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Logged in")
        else:
            print("not logged in")

        response_data = {}
        if user:
            response_data["result"] = "Success!"
            response_data["message"] = 'You"re logged in'
            print("auth:", user is not None, user)
            login(request, user)
        else:
            response_data["result"] = "failed"
            response_data["message"] = "You messed up"

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def user_logout(request):
    context = {}
    logout(request)
    context["status"] = "Success"
    # return JsonResponse(context, status=200)
    return render(request, "login.html", {"status": context})


# if request.method == "POST":
# 	form = NewUserForm(request.POST)
# 	if form.is_valid():
# 		user = form.save()
# 		login(request, user)
# 		messages.success(request, "Registration successful." )
# 		return redirect("main:homepage")
# 	messages.error(request, "Unsuccessful registration. Invalid information.")
# form = NewUserForm()
# return render (request=request, template_name="register.html", context={"register_form":form})


def html(request, filename):
    context = {"filename": filename, "collapse": ""}
    # if request.user.is_anonymous and filename != "login":
    #     return redirect("/login.html")
    if filename == "logout":
        logout(request)
        return redirect("/")
    if filename == "login" and request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            if "@" in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
            # user = authenticate(request, username=user.username, password=password)
            # if user is not None:
            #     login(request, user)
            #     return redirect("/")
            # else:
            #     context["error"] = "Wrong password"
        except ObjectDoesNotExist:
            context["error"] = "User not found"

        print("login")
        print(username, password)
    print(filename, request.method)
    if filename in ["buttons", "cards"]:
        context["collapse"] = "components"
    if filename in [
        "utilities-color",
        "utilities-border",
        "utilities-animation",
        "utilities-other",
    ]:
        context["collapse"] = "utilities"
    if filename in ["404", "blank"]:
        context["collapse"] = "pages"

    return render(request, f"{filename}.html", context=context)
