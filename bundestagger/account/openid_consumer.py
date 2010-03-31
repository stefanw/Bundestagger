# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.conf import settings
from django_openid.consumer import SessionConsumer
from django.contrib import messages

from bundestagger.account.auth import login, logout

class BundesOpenidConsumer(SessionConsumer):
    session_key = 'openid'
    openid_required_message = 'Gib eine OpenID ein'
    xri_disabled_message = 'i-names werden nicht unterstützt'
    openid_invalid_message = 'Die OpenID ist nicht gültig'
    request_cancelled_message = 'Die Anfrage wurde abgebrochen'
    message_loggedin = "Erfolgreich eingeloggt"
    message_loggedout = "Erfolgreich ausgeloggt"
    failure_message = 'Fehler: %s'
    setup_needed_message = 'Setup benötigt'
    sign_next_param = False
    salt_next = '07n98kpajapd290?(H"N=)(czar3)' # Adds extra saltiness to the ?next= salt
    xri_enabled = False
    on_complete_url = None
    trust_root = settings.SITE_DOMAIN # If None, full URL to endpoint is used
    logo_path = None # Path to the OpenID logo, as used by the login view
    
    def show_error(self, request, message, exception=None):
        messages.error(request, message)
        return HttpResponseRedirect("/")

    def show_message(self, request, title, message):
        messages.info(request, message)
        return HttpResponseRedirect("/")

    def on_success(self, request, identity_url, openid_response):
        messages.info(request, self.message_loggedin)
        login(request, identity_url)
        return super(BundesOpenidConsumer,self).on_success(request, identity_url, openid_response)
    
    def do_logout(self, request):
        logout(request)
        response =  super(BundesOpenidConsumer,self).do_logout(request)
        messages.info(request, self.message_loggedout)
        return response