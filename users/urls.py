from django.contrib import admin
from django.urls import path
from users import views

# url patterns for users app
urlpatterns = [
    path("", views.welcome, name="welcome"),
]

