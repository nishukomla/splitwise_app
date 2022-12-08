from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.contrib.auth.base_user import AbstractBaseUser
from django.conf import settings
from datetime import datetime


# Create your models here.


class Contact(AbstractBaseUser):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100,blank=True)
    last_name = models.CharField(max_length=100,blank=True)
    password = models.CharField(max_length=50)
    email = models.EmailField()


class Friend(models.Model):
    person1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="person1"
    )
    person2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="person2"
    )
    money_owed = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return self.person2.username


class Message(models.Model):
    person1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mperson1"
    )
    person2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mperson2"
    )
    message = models.CharField(max_length=500)
    date = models.DateTimeField(default=datetime.now)


class Group(models.Model):
    group_name = models.CharField(max_length=30)
    no_transactions = models.IntegerField(default=0)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Membership")

    def __str__(self):
        return self.group_name


class Membership(models.Model):
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    money_owed = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return self.friend.username + " " + self.group.group_name


class Transaction(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    group_transaction_id = models.IntegerField(default=0)
    lender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lender"
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrower"
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="added_by",
        null=True,
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paid_by",
        null=True,
    )
    description = models.CharField(max_length=30)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    no_transactions = 0
    MOVIES = "mv"
    FOOD = "fd"
    TRAVEL = "tr"
    ELECTRONICS = "ee"
    MEDICAL = "md"
    SHOPPING = "sp"
    SERVICES = "sv"
    SETTLE = "st"
    OTHERS = "ot"
    TAG_CHOICES = [
        (MOVIES, "Movies"),
        (FOOD, "Food"),
        (TRAVEL, "Travel"),
        (ELECTRONICS, "Electronics"),
        (MEDICAL, "Medical"),
        (SHOPPING, "Shopping"),
        (SERVICES, "Services"),
        (SETTLE, "Settle"),
        (OTHERS, "Others"),
    ]
    tag = models.CharField(max_length=2, choices=TAG_CHOICES)
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return (
            self.lender.username
            + " lent "
            + str(self.amount)
            + " to "
            + self.borrower.username
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    # location = models.CharField(max_length=30, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    image = models.ImageField(
        upload_to="profile_image", blank=True, default="default_face.png"
    )
    no_of_messages = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

def __str__(self):
    return self
