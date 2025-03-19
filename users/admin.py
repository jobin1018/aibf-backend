from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Event, Registration 

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'name', 'address', 'is_staff', 'is_active')  # Customize the list display
    search_fields = ('email', 'name')  # Customize the search fields
    ordering = ('email',)

class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display = ('name', 'start_date', 'end_date', 'venue', 'capacity')  # Customize the list display
    search_fields = ('name', 'start_date')  # Customize the search fields
    ordering = ('-start_date',)

class RegistrationAdmin(admin.ModelAdmin):
    model = Registration
    list_display = ('event', 'user', 'selected_package')  # Customize the list display
    search_fields = ('event', 'user')  # Customize the search fields
    ordering = ('registration_date',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
