from django.contrib import admin
from .models import Event


class EventAdmin(admin.ModelAdmin):
    # fieldsets = [(None, {"fields": ["question_text"]}),("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),]
    list_display = ('id','name', 'description', 'address', 'latitude', 'longitude')
    # list_filter = ('address')  # Add filters for better navigation
    search_fields = ('name', 'address')  # Enable search by name or address
    # list_per_page = 20  # Control the number of items displayed per page

admin.site.register(Event, EventAdmin)