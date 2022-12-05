"""student URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bootstrap import settings
from django.conf.urls.static import static
from app import views

# from app.views import *


urlpatterns = [
    path("admin/", admin.site.urls),
    path("<filename>.html", views.html),
    path("", views.index),
    path("registartion_form", views.registration_form, name="registartion_form"),
    path("login_request", views.login_request, name="login_request"), # type: ignore
    path("addfriend", views.add_friend_form, name="addfriend"),# type: ignore
    path("getfriends", views.loop_friends, name="getfriends"),
    path("getusersforFriendspage", views.getusersforFriendspage, name="getusersforFriendspage"),
    path("updatefriend", views.update_friend_data, name="updatefriend"),# type: ignore
    path("deletefriend",views.delete_friend,name="deletefriend"),# type: ignore
    path("addgroup",views.add_group,name="addgroup"),# type: ignore
    path("getgroups",views.getGroups,name="getgroups"),
    path("addexpense",views.transaction_form,name="addexpense"),
    path("getCurrentUser",views.get_current_user,name="getCurrentUser"),
    path("getbalances",views.get_balances,name="getbalances"),
    path("getIndividualFriend/<str:f>/",views.friend,name="getIndividualFriend"),
    path("password_reset", views.password_reset_request, name="password_reset"),# type: ignore

    # update_friend_data
    # getusersforFriendspage
    path("logout", views.user_logout, name="logout"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
