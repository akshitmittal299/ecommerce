from django.urls import path, include
from .views import *
urlpatterns= [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view())
]