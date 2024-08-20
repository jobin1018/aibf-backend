from django.shortcuts import render
from django.http import HttpResponse

# create a view to return just httpresponse message not from template
def welcome(request):
    return HttpResponse("Welcome to the users app!")




