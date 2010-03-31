# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.contrib import messages

from bundestagger.helper.utils import is_post
from bundestagger.account.auth import logged_in
from bundestagger.account.models import User

@is_post
def logout(request):
    from bundestagger.account.auth import logout as logout_func
    logout_func(request)
    next = "/"
    if "next" in request.POST:
        next = request.POST["next"]
    return redirect(next)

@is_post
@logged_in    
def change_username(request):
    if "username" in request.POST:
        user = request.bundesuser
        username = request.POST["username"]
        if username != user.username:
            if len(username)>20:
                messages.add_message(request, messages.INFO, u"Username ist zu lang")
            elif len(username)==0:
                messages.add_message(request, messages.INFO, u"Username ist zu kurz")
            else:
                uc = User.objects.filter(username=username).count()
                if uc == 0:
                    user.username = request.POST["username"]
                    user.save()
                    request.session["bundesuser"] = user
                    messages.add_message(request, messages.INFO, u"Username geändert")
                else:
                    messages.add_message(request, messages.INFO, u"Username ist schon vergeben")
    next = "/"
    if "next" in request.POST:
        next = request.POST["next"]
    return redirect(next)