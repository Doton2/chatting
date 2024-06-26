from django.shortcuts import redirect, render, get_object_or_404
import requests
from .models import User
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
import os
from django.contrib import auth
from django.views.decorators.http import require_http_methods

# Create your views here.

SOCIAL_CALLBACK_URI ="http://127.0.0.1:8000/accounts/login/callback/"

@require_http_methods(["POST"])
def login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email "
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    redirect_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={SOCIAL_CALLBACK_URI}&scope={scope}")
    return redirect(redirect_url)

@require_http_methods(["GET"])
def login_callback(request):
    code = request.GET.get('code')
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    state = os.environ.get('STATE')
    token_req = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": SOCIAL_CALLBACK_URI,
            "state": state,
        },
    )
    token_req_status = token_req.status_code
    if token_req_status != 200:
        context = {"message": '로그인에'}
        return render(request, 'error.html', context)
    token_json =token_req.json()

    access_token = token_json.get('access_token')
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        context = {"message": '로그인에'}
        return render(request, 'error.html', context)


    email_json=email_req.json()
    email = email_json.get('email')
    username = email.split('@')[0]

    try:
        user = User.objects.get(username=username)

        social_user = SocialAccount.objects.get(user=user)

        auth.login(request, user)

        return redirect('index')

    except:

        user = User.objects.create(username=username, email=email)

        social_user = SocialAccount.objects.create(user=user, provider='google', uid=username )

        auth.login(request, user)

        return redirect('index')

    
    
@require_http_methods(["POST"])
def logout(request):
    auth.logout(request)
    return redirect('index')



