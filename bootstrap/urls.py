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
    path("login_request", views.login_request, name="login_request"),
    path("addfriend", views.add_friend_form, name="addfriend"),
    path("getfriends", views.loop_friends, name="getfriends"),
    path("getusersforFriendspage", views.getusersforFriendspage, name="getusersforFriendspage"),
    # getusersforFriendspage
    path("logout", views.user_logout, name="logout"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
