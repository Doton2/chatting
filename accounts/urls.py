from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path("login/", views.login, name='login'),
    path("login/callback/", views.login_callback, name="login_callback"),
    path("logout/", views.logout, name='logout')
]