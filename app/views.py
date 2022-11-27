import email
from tkinter import FLAT
from django import forms
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist

# from .forms import ContactForm
from django.http import JsonResponse
import json
from .forms import FriendForm, GroupForm, NewUserForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.core import serializers
import pandas as pd


def index(request):
    # if request.user.is_anonymous:
    #     return redirect("/login.html")l
    return html(request, "index")


def add_friend_form(request):
    me = User.objects.get(username=request.user.get_username())
    if request.method == "POST":
        print("friend", request.method)
        friend_form = FriendForm(request.POST)
        if friend_form.is_valid():
            friend_id = friend_form.cleaned_data["friendname"]
            print(
                "friend_id:",
                friend_id,
                User.objects.filter(username=friend_id).exists(),
            )
            if User.objects.filter(username=friend_id).exists():
                response_data = {}
                friend = User.objects.get(username=friend_id)
                if friend == me:
                    # raise forms.ValidationError("f")
                    print("F")
                    response_data["result"] = "Failed!"
                    response_data["message"] = "Already exists!"
                elif (
                    Friend.objects.filter(person1=me, person2=friend).exists()
                    # or Friend.objects.filter(person1=friend, person2=me).exists()
                ):
                    print("f")
                    response_data["result"] = "Failed!"
                    response_data["message"] = "Already exists!"
                else:
                    f = Friend(person1=me, person2=friend)
                    f1 = Friend(person1=friend, person2=me)

                    print("hi")
                    f.save()
                    f1.save()
                    response_data["result"] = "Success!"
                    response_data["message"] = 'You"re saved'
                return HttpResponse(
                    json.dumps(response_data), content_type="application/json"
                )


def add_group(request):

    userobj = User.objects.filter(id=request.user.id).values("username", "id").first()
    user_id = userobj["id"]
    me = User.objects.get(id=user_id)
    print("me", me)
    # return
    group_form = GroupForm(request.POST)
    print("test data result:", request.method, User, request.POST.getlist("friends"))
    # return
    # if request.method == "POST" and group_form.is_valid():
    #     print('request:',request.POST,request.POST.getlist('friends'))
    # return JsonResponse({"result": 'data response'})

    if group_form.is_valid():
        name = group_form.cleaned_data["group_name"]
        print("request:", request.POST, request.POST.getlist("friends[]"))
        people = request.POST.getlist("friends[]")
        print("people:", people)
        # return
        g = Group(group_name=name)
        g.save()
        # print('me:',me['username'])
        # return
        m = Membership(friend=me, group=g)
        print("memene:", m)
        m.save()
        for p in people:
            preal = User.objects.get(username=p)
            for p1 in people:
                if p != p1:
                    p1real = User.objects.get(username=p1)
                    if not Friend.objects.filter(
                        person1=preal, person2=p1real
                    ).exists():
                        fxxx = Friend(person1=preal, person2=p1real)
                        fxxx1 = Friend(person1=p1real, person2=preal)
                        fxxx.save()
                        fxxx1.save()
            for p in people:
                member = User.objects.get(username=p)
                m = Membership(friend=member, group=g)
                m.save()
            # print(member)
            return JsonResponse({"result": "Success!"})


def getGroups(request):
    me = User.objects.get(id=request.user.id)
    groups = Membership.objects.filter(friend=me)
    groups_boolean = []
    for g in groups:
        print("inner money group:", g.money_owed)
        if g.money_owed < 0:
            g.money_owed = -1 * g.money_owed
            groups_boolean.append(0)
        else:
            groups_boolean.append(1)
    # print("test grps:", list(groups))
    ids = groups.values_list("group", flat=True)
    new_groups_list = Group.objects.filter(id__in=list(ids)).values_list(
        "group_name", flat=True
    )
    print("groups_list:", new_groups_list)
    groupslist = []
    for money in groups:
        print("nxt money:", money.money_owed, money.group.group_name)
        mydict = {}
        mydict["name"] = money.group.group_name
        mydict["money_owed"] = money.money_owed
        groupslist.append(mydict)
    # groups_list = zip(new_groups_list,groups_boolean)
    # result_list = list(groups_list)
    # # print('testind info:',result_list)
    # b = [item for item in result_list]
    # mylist = []
    # print(b)
    # for n in b:
    #     print('test data for:',n)
    #     mydict = {}
    #     mydict['name'] = n[0]
    #     mydict['price'] = n[1]
    #     mylist.append(mydict)
    # print('test data:',mylist)
    return JsonResponse({"result": "Success!", "data": groupslist})


# @csrf_exempt
def loop_friends(request):
    print("test frnd request:", request.POST)
    # return
    me = User.objects.filter(id=request.user.id).values("username", "id").first()
    _friends_data = list(Friend.objects.filter(person1=me["id"]).values("person2_id"))
    # _friends_data = list(Friend.objects.values('person2_id'))
    IDS = []
    for element in _friends_data:
        IDS.append(element["person2_id"])
    result = list(
        User.objects.filter(id__in=IDS).values_list("username", "email")
    )  # assuming IDS come from the script
    return JsonResponse({"result": result})


# @csrf_exempt
def getusersforFriendspage(request):
    current_user = request.user
    result = list(
        User.objects.filter(is_superuser=False).exclude(id=current_user.id).values()
    )
    print("result:", result)
    return JsonResponse({"result": result})


# @csrf_exempt
def update_friend_data(request):
    t = Friend.objects.get(id=1)
    t.value = 999  # change field
    t.save()  # this will update only
    print("hello")


def delete_friend(request):
    response_data = {}
    login_user = (
        User.objects.filter(id=request.user.id).values("username", "id").first()
    )
    if request.method == "POST":
        username = request.POST["friendname"]
        frndIdObj = User.objects.filter(username=username).values("id").first()
        print("frnd id:", User.objects.filter(username=username).values("id").first())
        instance = Friend.objects.filter(
            person1=login_user["id"], person2=frndIdObj["id"]
        )
        # instance = Friend.objects.get(username=username)
        instance.delete()
        response_data["result"] = "Success!"
        response_data["message"] = "Deleted successfully."
        return JsonResponse(response_data, status=200)


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
