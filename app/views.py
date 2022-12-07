import email

# from tkinter import FLAT
from django import forms
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# from django.db.models import ObjectDoesNotExist
from decimal import Decimal
from django.forms.models import model_to_dict
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q


# from .forms import ContactForm
from django.http import JsonResponse
import json
from .forms import FriendForm, GroupForm, NewUserForm, ChangeForm,ProfileUpdateForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.core import serializers
import pandas as pd


def index(request):
    if request.user.is_anonymous:
        return redirect("/login.html")
    else:
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
    print("user obj:", request.user, request.user.id, userobj)
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
        "group_name", "id"
    )
    print("groups_list:", new_groups_list)
    groupslist = []
    for money in groups:
        print("nxt money:", money.money_owed, money.group.group_name)
        mydict = {}
        mydict["name"] = money.group.group_name
        mydict["money_owed"] = money.money_owed
        mydict["id"] = money.group.id
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
        User.objects.filter(id__in=IDS).values_list("username", "email", "id")
    )  # assuming IDS come from the script
    currme = User.objects.get(username=request.user.get_username())
    friends = Friend.objects.filter(person1=currme)
    print("my friends:", result)
    friends_boolean = []
    for y in friends:
        if y.money_owed < 0:
            y.money_owed = (-1) * (y.money_owed)
    print("final frnds:", friends.values("person2", "money_owed"))
    # friends_list = list(friends)
    # oi = OrgInvite.objects.get(token=100)
    oi_dict_money = friends.values("person2", "money_owed")
    OrgInvite = []
    for ele in result:
        for item in oi_dict_money:
            print("my elle:", ele[2], item)
            if ele[2] == item.get("person2"):
                # ele.append(money_owed=item['money_owed'])
                ele = ele[:3] + (item["money_owed"],) + ele[3:]
                if item["money_owed"] < 0:
                    ele = ele[:4] + (0,) + ele[4:]
                else:
                    ele = ele[:4] + (1,) + ele[4:]
                OrgInvite.append(ele)
            # else:
            #     OrgInvite=[]
    print("Final frnds:", OrgInvite)
    # oi_serialized = json.dumps(oi_dict)
    # friends_list = serializers.serialize("json",OrgInvite)

    return JsonResponse({"result": OrgInvite})
    # return JsonResponse({"result": result})


def friend(request, f):
    print("test friend:", request, f)
    me = request.user
    print(f)
    friend = User.objects.get(id=f)
    print(friend)
    x = Friend.objects.filter(person1__username=me)
    print(f)
    z = 0
    a = ""
    for y in x:
        if y.person2.username == friend.username:
            zxxx = 0
            ts = Transaction.objects.filter(lender=me, borrower=friend, group=None)
            for t in ts:
                zxxx = zxxx + t.amount
            ts = Transaction.objects.filter(lender=friend, borrower=me, group=None)
            for t in ts:
                zxxx = zxxx - t.amount
            a = str(y.person2)
    groups_list = []
    groups = Membership.objects.filter(friend=me)
    for g in groups:
        if Membership.objects.filter(group=g.group, friend=friend).exists():
            m = Membership.objects.get(group=g.group, friend=friend)
            groups_list.append([m.group, 0])

    for g in groups_list:
        tlist = Transaction.objects.filter(group=g[0], lender=me, borrower=friend)
        for t in tlist:
            g[1] = g[1] + t.amount
        tlist = Transaction.objects.filter(group=g[0], lender=friend, borrower=me)
        for t in tlist:
            g[1] = g[1] - t.amount
    print(groups_list)
    for g in groups_list:
        print(g[0].group_name)
    if request.method == "POST":
        if "settle_up" in request.POST:
            if zxxx > 0:
                t = Transaction(
                    group_transaction_id=Transaction.no_transactions,
                    lender=friend,
                    borrower=me,
                    description="Settling!",
                    amount=zxxx,
                    tag="st",
                    added_by=me,
                    paid_by=friend,
                )
                t.save()
                Transaction.no_transactions = Transaction.no_transactions + 1
            elif zxxx < 0:
                t = Transaction(
                    group_transaction_id=Transaction.no_transactions,
                    lender=me,
                    borrower=friend,
                    description="Settling!",
                    amount=-1 * zxxx,
                    tag="st",
                    added_by=me,
                    paid_by=me,
                )
                t.save()
                Transaction.no_transactions = Transaction.no_transactions + 1
            else:
                pass
            for g in groups_list:
                if g[1] > 0:
                    no = g[0].no_transactions
                    t = Transaction(
                        group=g[0],
                        group_transaction_id=no,
                        lender=friend,
                        borrower=me,
                        description="Settling!",
                        amount=g[1],
                        tag="st",
                        added_by=me,
                        paid_by=friend,
                    )
                    t.save()
                    m1 = Membership.objects.get(group=g[0], friend=me)
                    z = m1.money_owed - g[1]
                    m1.money_owed = z
                    m1.save()
                    m2 = Membership.objects.get(group=g[0], friend=friend)
                    z = m2.money_owed + g[1]
                    m2.money_owed = z
                    m2.save()
                    z = g[0].no_transactions + 1
                    g[0].no_transactions = z
                    g[0].save()
                elif g[1] < 0:
                    no = g[0].no_transactions
                    t = Transaction(
                        group=g[0],
                        group_transaction_id=no,
                        lender=me,
                        borrower=friend,
                        description="Settling!",
                        amount=-1 * g[1],
                        tag="st",
                        added_by=me,
                        paid_by=me,
                    )
                    t.save()
                    m1 = Membership.objects.get(group=g[0], friend=friend)
                    z = m1.money_owed - (-1 * g[1])
                    m1.money_owed = z
                    m1.save()
                    m2 = Membership.objects.get(group=g[0], friend=me)
                    z = m2.money_owed + (-1 * g[1])
                    m2.money_owed = z
                    m2.save()
                    z = g[0].no_transactions + 1
                    g[0].no_transactions = z
                    g[0].save()
                    pass
                else:
                    pass
        f1 = Friend.objects.get(person1=me, person2=friend)
        print("test 1st frnd:", f1)
        f1.money_owed = 0
        f1.save()
        f2 = Friend.objects.get(person1=friend, person2=me)
        print("test 2nd frnd:", f2)
        f2.money_owed = 0
        f2.save()
        idx = str(friend.id)
        # return HttpResponse("payments.html")
        return render(request, "payments.html")

    template = loader.get_template("expanded_friend.html")
    print(zxxx)
    if zxxx >= 0:
        boolean = 1
    else:
        boolean = 0
        zxxx = (-1) * zxxx
    boolean2 = []
    for g in groups_list:
        if g[1] >= 0:
            boolean2.append(1)
        else:
            boolean2.append(0)
            g[1] = (-1) * g[1]
    lst = zip(groups_list, boolean2)
    context = {
        "zxxx": zxxx,
        "boolean": boolean,
        "a": a,
        "friend": friend,
        "lst": lst,
        "f": f
        #'groups_list':groups_list
    }
    return HttpResponse(template.render(context, request))


def get_balances(request):
    me = request.user
    template = loader.get_template("balances.html")
    # g=request.session.get('group')
    g = request.POST.get("groupid")
    group = Group.objects.get(id=g)
    print(group)
    lst = Membership.objects.filter(group=group)
    money = []
    frnds_list = []
    for l in lst:
        if l.friend != me:
            money.append([l.friend.username, l.money_owed, l.friend.id])
            frnds_list.append(l.friend)
    print(money)

    money_friends = []
    for f in frnds_list:
        tlist = Transaction.objects.filter(group=group, lender=me, borrower=f)
        amt = 0
        for t in tlist:
            amt = amt + t.amount
        tlist = Transaction.objects.filter(group=g[0], lender=f, borrower=me)
        for t in tlist:
            amt = amt - t.amount
            money_friends.append([f.username, amt, f.id])
    print(money_friends)

    x = ""
    context = {"money": money, "money_friends": money_friends}
    return HttpResponse(template.render(context, request))


def group(request, g):
    print("test group:", request)
    me = request.user
    group = Group.objects.get(id=g)
    all_transactions = Transaction.objects.filter(group=g).order_by("date")
    no = group.no_transactions
    ms = Membership.objects.filter(group=g)
    frnd_list = ()
    for m in ms:
        if m.friend != me:
            frnd_list = frnd_list + ((m.friend.username, m.friend.username),)
    template = loader.get_template("expandedgroup.html")
    x = ""
    trans_list = []
    request.session["group"] = g
    for i in range(no):
        if all_transactions.filter(group_transaction_id=i).exists():
            ts = all_transactions.filter(group_transaction_id=i)
            shares_list = []
            paid_amt = 0
            for t in ts:
                date = [str(t.date)]
                paid_by = [t.paid_by.username]
                x = tag(t.tag)
                tag1 = [x]
                desc = [t.description]
                contri = t.amount
                paid_amt = paid_amt + contri
                borrower = t.borrower.username
                shares_list.append([borrower, contri])
            lst = (date, paid_by, tag1, desc, shares_list, paid_amt)
            trans_list.append(lst)

    change_form = ChangeForm(frnd_list)
    if request.method == "POST":
        if "balances" in request.POST:
            print("hi")
        if "settle_up" in request.POST:
            change_form = ChangeForm(frnd_list, request.POST)
            if change_form.is_valid():
                people = change_form.cleaned_data["friends"]
                for p in people:
                    f = User.objects.get(username=p)
                    amt = 0
                    if all_transactions.filter(lender=me, borrower=f).exists():
                        ts = all_transactions.filter(lender=me, borrower=f)
                        for t in ts:
                            amt = amt + t.amount
                    if all_transactions.filter(lender=f, borrower=me).exists():
                        ts = all_transactions.filter(lender=f, borrower=me)
                        for t in ts:
                            amt = amt - t.amount
                    if amt > 0:
                        no = group.no_transactions
                        t = Transaction(
                            group=group,
                            group_transaction_id=no,
                            lender=f,
                            borrower=me,
                            description="Settling!",
                            amount=amt,
                            tag="st",
                            added_by=me,
                            paid_by=f,
                        )
                        t.save()
                        m1 = Membership.objects.get(group=group, friend=me)
                        z = m1.money_owed - amt
                        m1.money_owed = z
                        m1.save()
                        m2 = Membership.objects.get(group=group, friend=f)
                        z = m2.money_owed + amt
                        m2.money_owed = z
                        m2.save()
                        f2 = Friend.objects.get(person1=me, person2=f)
                        z = f2.money_owed - amt
                        f2.money_owed = z
                        f2.save()
                        f1 = Friend.objects.get(person1=f, person2=me)
                        z = f1.money_owed + amt
                        f1.money_owed = z
                        f1.save()
                        z = group.no_transactions + 1
                        group.no_transactions = z
                        group.save()
                    elif amt < 0:
                        no = group.no_transactions
                        t = Transaction(
                            group=group,
                            group_transaction_id=no,
                            lender=me,
                            borrower=f,
                            description="Settling!",
                            amount=-1 * amt,
                            tag="st",
                            added_by=me,
                            paid_by=me,
                        )
                        t.save()
                        m1 = Membership.objects.get(group=group, friend=me)
                        z = m1.money_owed + (-1 * amt)
                        m1.money_owed = z
                        m1.save()
                        m2 = Membership.objects.get(group=group, friend=f)
                        z = m2.money_owed - (-1 * amt)
                        m2.money_owed = z
                        m2.save()
                        f2 = Friend.objects.get(person1=me, person2=f)
                        z = f2.money_owed + (-1 * amt)
                        f2.money_owed = z
                        f2.save()
                        f1 = Friend.objects.get(person1=f, person2=me)
                        z = f1.money_owed - (-1 * amt)
                        f1.money_owed = z
                        f1.save()
                        z = group.no_transactions + 1
                        group.no_transactions = z
                        group.save()
                    else:
                        pass
                return HttpResponseRedirect("/splitwise/success/")

    else:
        change_form = ChangeForm(frnd_list)
    context = {"trans_list": trans_list, "g": g, "change_form": change_form}

    return HttpResponse(template.render(context, request))


def activity_tab(request):
    me = request.user
    template = loader.get_template("activity_tab.html")
    x = Transaction.objects.filter(Q(lender=me) | Q(borrower=me)).order_by("-date")
    a = 0
    print(len(x))
    i = 0
    desc = []
    money = []
    additional_info = []
    transactions = []
    boolean = []
    no_of_activities = 0
    exit = False
    while i < len(x):
        # print(x[i])
        if x[i].lender == me and x[i].borrower == me:
            i = i + 1
        else:
            if x[i].lender == me:
                money.append(x[i].amount)
            else:
                money.append((-1) * x[i].amount)

            desc.append(x[i].description)
            transactions.append(x[i])
            if x[i].group_id is None:
                additional_info.append(
                    "group does not exist xxxxxxwkebjkerjbkjengksdbkejbg"
                )
            else:
                additional_info.append(x[i].group.group_name)
            j = i + 1
            if j >= len(x):
                exit = True
                break
                # print(j)
            while (
                x[j].group_id == x[i].group_id
                and x[j].group_transaction_id == x[i].group_transaction_id
            ):
                if j < len(x):
                    if x[j].lender == me and x[j].borrower == me:
                        j = j + 1
                        if j >= len(x):
                            exit = True
                            break
                        pass
                    else:
                        if x[j].lender == me:
                            money[no_of_activities] += x[j].amount
                        else:
                            money[no_of_activities] -= x[j].amount
                        j = j + 1
                        if j >= len(x):
                            exit = True
                            break
                else:
                    exit = True
                    break
            i = j
            no_of_activities = no_of_activities + 1
            if exit == True:
                break
    # for i in range(len(desc)):
    # print(str(desc[i])+" "+str(money[i]))
    # print(x.transaction
    # send_list = [desc, money]#, additional_info]
    for i in range(len(money)):
        if money[i] >= 0:
            boolean.append(1)
        else:
            boolean.append(0)
            money[i] = -1 * money[i]
    send_list = zip(money, desc, additional_info, transactions, boolean)
    # print(send_list)
    context = {"send_list": send_list}
    return HttpResponse(template.render(context, request))


def detailed_activity1(request, i):
    y = Transaction.objects.filter(group=None, group_transaction_id=i)
    # print(y)
    person = []
    share = []
    payer = ""
    total_amount = 0
    print(len(y))
    if len(y) == 1:
        payer = y[0].lender.username
        total_amount = y[0].amount
        person.append(y[0].borrower.username)
        share.append(total_amount)
    else:
        for z in y:
            person.append(z.borrower.username)
            share.append(z.amount)
            total_amount = total_amount + z.amount
            if z.lender.username == z.borrower.username:
                payer = z.lender.username
    lst = zip(person, share)
    context = {"lst": lst, "payer": payer, "total_amount": total_amount}
    template = loader.get_template("expanded_activity.html")
    return HttpResponse(template.render(context, request))
    # return HttpResponse('success')


def detailed_activity2(request, i, j):
    x = Group.objects.get(id=i)
    y = Transaction.objects.filter(group=x, group_transaction_id=j)
    # print(y)
    person = []
    share = []
    payer = ""
    total_amount = 0
    for z in y:
        person.append(z.borrower.username)
        share.append(z.amount)
        total_amount = total_amount + z.amount
        if z.lender.username == z.borrower.username:
            payer = z.lender.username
    lst = zip(person, share)
    context = {"lst": lst, "payer": payer, "total_amount": total_amount}
    template = loader.get_template("expanded_activity.html")
    return HttpResponse(template.render(context, request))


def deletegroup(request):
    if request.method == "POST":
        for g in Group.objects.all():
            print('Group new:',g,request.POST,g.group_name)
            if g.group_name == request.POST.get("group_name"):
                money = 0
                m = Membership.objects.filter(group=g)
                for x in m:
                    if x.money_owed != 0:
                        money = 1
                if money == 0:
                    g.delete()
                    context = {"status": "Success!","Message":"Deleted successfully."}
                    return JsonResponse({"result": context})
                else :
                    context = {"status": "Failed!","Message":"Failed to delete."}
                    return JsonResponse({"result": context})



def balances(request):
    if request.user.is_authenticated:
        me = request.user
        template = loader.get_template("balances.html")
        g = request.session.get("group")
        group = Group.objects.get(id=g)
        print(group, g)
        lst = Membership.objects.filter(group=group)
        money = []
        frnds_list = []
        for l in lst:
            if l.friend != me:
                money.append([l.friend.username, l.money_owed, l.friend.id])
                frnds_list.append(l.friend)
        print(money)

        money_friends = []
        for f in frnds_list:
            tlist = Transaction.objects.filter(group=group, lender=me, borrower=f)
            amt = 0
            for t in tlist:
                amt = amt + t.amount
            tlist = Transaction.objects.filter(group=g[0], lender=f, borrower=me)
            for t in tlist:
                amt = amt - t.amount
            money_friends.append([f.username, amt, f.id])
        print(money_friends)

        x = ""
        context = {"money": money, "money_friends": money_friends}
        return HttpResponse(template.render(context, request))
    else:
        # return JsonResponse({"result": context})
        return render(request, "404.html")

def sendNotification(request):
    me = User.objects.get(username=request.user.get_username())
    other = User.objects.get(id=request.POST["frndId"])
    if request.method == 'POST':
                    print('f')
                    message1 = request.POST['message']
                    print(message1)
                    mess = Message(person1=me, person2=other, message=message1)
                    mess.save()
                    context = {"status": "Success!", "message": "Notification sent successfully."}
                    return JsonResponse({"result":context })
    else:
        context = {"status": "Fail!", "message": "Failed to send notification."}
        return JsonResponse({"result":context })


def getnotification(request):
    me = request.user
    sent_messages = Message.objects.filter(person1=me).order_by('date')
    received_messages = Message.objects.filter(person2=me).order_by('date')
    print('received_messages',received_messages,'sent_messages',sent_messages)
    data_received_messages = serializers.serialize('json', received_messages)
    data_sent_messages = serializers.serialize('json', sent_messages)
    context={'sent_messages' : data_sent_messages,'received_messages' : data_received_messages}

    # month_list = [11, 3, 1, 10,12]

    # rest=Transaction.objects.filter(*(Q(date__month=month) for month in month_list))
    # print('test data:',rest)

    return JsonResponse({"result":context},content_type="application/json")


# def showallnotification():

def showallnotification(request):
	me = request.user
	sent_messages = Message.objects.filter(person1=me).order_by('date')
	received_messages = Message.objects.filter(person2=me).order_by('date')
	context = {
		'sent_messages' : sent_messages,
		'received_messages' : received_messages
	}
	template = loader.get_template('notifications.html')
	return(HttpResponse(template.render(context,request)))

def showprofile(request):
    edit_profile_form = ProfileUpdateForm()
    template = loader.get_template('profile.html')
    context = {
		'edit_profile_form' : edit_profile_form,
        }
    return HttpResponse(template.render(context, request))


def editprofile(request):
    edit_profile_form = ProfileUpdateForm()
    if request.method == 'POST':
        if 'edit_profile' in request.POST:
                # print(request.user.profile.bio)
                edit_profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
                if edit_profile_form.is_valid():
                    edit_profile_form.save()
                    #print(bio)
    else:
        edit_profile_form=ProfileUpdateForm()
    template = loader.get_template('profile.html')
    context = {
		'edit_profile_form' : edit_profile_form,
        }
    return HttpResponse(template.render(context, request))

def transaction_form(request):
    # me = User.objects.filter(id=request.user.id).values("username", "id").first()
    me = request.user
    people = request.POST.getlist("people[]")
    print("people:", people)
    final_choices = ()
    # final_choices = final_choices + ((me['username'], me['username']),)
    for p in people:
        thistuple = (str(p), str(p))
        final_choices = final_choices + (thistuple,)
        # for i in final_choices:
        #     data = request.POST.getlist('shareData[]')[i]
        #     shares[str(i[0])]=data
    # choices = request.POST.getlist('choices[]')
    # template = loader.get_template('transaction_form.html')
    # transaction_form = TransactionForm(final_choices)
    print("request.method", request.method)
    if request.method == "POST":
        # if 'transaction' in request.POST:
        # transaction_form=TransactionForm(final_choices, request.POST)
        # if transaction_form.is_valid():
        desc = request.POST["description"]
        who_paid = request.POST.getlist("who_paid[]")
        # array_data = request.POST['shareData']
        # data = json.loads(array_data)
        # print(data)
        # shareData=request.POST['shareData']
        # print("share data:", request.POST["shareData"])
        amt = int(request.POST["amount"])
        split = request.POST["split"]
        tag = request.POST["tag"]
        shares = {}
        index = 0
        # for i in final_choices:
        for index, value in enumerate(final_choices):
            print("check val is:", index, value, value[0], final_choices)
            array_data = request.POST["shareData"]
            newdata = json.loads(array_data)
            print("data:", newdata[index], newdata[index][value[0]])
            data = newdata[index][value[0]]
            shares[str(value[0])] = data
        payer = User.objects.get(username=who_paid[0])

        if split == "equal":
            share_amt = amt / len(final_choices)
            print("share_amt:", share_amt)
            t1 = Transaction(
                group_transaction_id=Transaction.no_transactions,
                lender=payer,
                borrower=payer,
                description=desc,
                amount=share_amt,
                tag=tag,
                added_by=me,
                paid_by=payer,
            )
            t1.save()
            for p in final_choices:

                # print(p[0])
                user = User.objects.get(username=p[0])
                if user != payer:
                    t = Transaction(
                        group_transaction_id=Transaction.no_transactions,
                        lender=payer,
                        borrower=user,
                        description=desc,
                        amount=share_amt,
                        tag=tag,
                        added_by=me,
                        paid_by=payer,
                    )
                    t.save()
                    f1 = Friend.objects.get(person1=payer, person2=user)
                    x = f1.money_owed + Decimal(share_amt)
                    f1.money_owed = x
                    f1.save()
                    f2 = Friend.objects.get(person1=user, person2=payer)
                    y = f2.money_owed - Decimal(share_amt)
                    f2.money_owed = y
                    f2.save()

        else:
            for p in final_choices:
                share_amt = int(shares[str(p[0])]) / 100 * amt
                user = User.objects.get(username=p[0])
                t = Transaction(
                    group_transaction_id=Transaction.no_transactions,
                    lender=payer,
                    borrower=user,
                    description=desc,
                    amount=share_amt,
                    tag=tag,
                    added_by=me,
                    paid_by=payer,
                )
                t.save()
                if user != payer:
                    f1 = Friend.objects.get(person1=payer, person2=user)
                    print("first frnd:", f1)
                    x = f1.money_owed + Decimal(share_amt)
                    f1.money_owed = x
                    f1.save()
                    f2 = Friend.objects.get(person1=user, person2=payer)
                    y = f2.money_owed - Decimal(share_amt)
                    f2.money_owed = y
                    f2.save()

        # print(share_amt)
        Transaction.no_transactions = Transaction.no_transactions + 1
        print(Transaction.no_transactions)
    # return HttpResponseRedirect('/splitwise/success/')

    context = {"status": "Success!"}
    return JsonResponse({"result": context})


def get_current_user(request):
    current_user = User.objects.filter(id=request.user.id).values()
    return JsonResponse({"result": list(current_user)})


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


def password_reset_request(request):
    if request.method == "POST":
        # password_reset_form = PasswordResetForm(request.POST)
        # if password_reset_form.is_valid():
        data = request.POST["email"]
        associated_users = User.objects.filter(Q(email=data))
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                # email_template_name = "/templates/password_reset_email.txt"
                c = {
                    "email": user.email,
                    "domain": "127.0.0.1:8000",
                    "site_name": "Website",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "http",
                }
                # email = render_to_string(c)
                try:
                    send_mail(
                        subject,
                        user.email,
                        "admin@example.com",
                        [user.email],
                        fail_silently=False,
                    )
                    response_data = {}
                    response_data["result"] = "Success!"
                    response_data["message"] = "Sent successfully."
                    print(response_data)
                    return JsonResponse(response_data)
                except BadHeaderError:
                    return HttpResponse("Invalid header found.")


def registration_form(request):
    is_ajax = request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    # print("is ajax", is_ajax, request.POST)
    if request.method == "POST" and is_ajax:
        form = NewUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            form.save()
            return JsonResponse({"email": email}, status=200)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)

    return render(request, "login.html", {"form": form})  # type: ignore


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
