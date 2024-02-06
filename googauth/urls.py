"""
URL configuration for googauth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import permission_required
from . import views

urlpatterns = [
    # POTENTIAL REFERENCES FOR PERMISSIONS LATER
    # @permission_required("polls.add_choice", login_url="/loginpage/")
    # url(r'^$', login_required(views.profile), name='profile'),
    
    path("admin/", admin.site.urls),
    path('home/', views.home, name = 'home',),
    path('user_dash/', views.user_dash, name = 'user_dash'),
    #path('admin_dash/', TemplateView.as_view(template_name = 'dashboard/admin_dash.html'), name = 'admin_dash'),
    path('admin_dash/', views.admin_dash, name="admin_dash"),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('allauth.urls')),
    path('dashboard/social/signup/', views.choose_role),
    path('create_event/', views.create_event, name='create_event'),
    path('all_events/', views.all_events, name='all_events'),
    # mksingh32 for pop up: path('get_event_data/', views.get_event_data, name='get_event_data'),
    path('choose_role/', views.choose_role, name='choose_role'),
    # ex: /event/5/
    path("event/<int:pk>/", views.event_detail, name="event"),
    path("rsvp", views.rsvp, name="rsvp"),
    path("delete_rsvp/<int:rsvp_id>/<int:event_id>/", views.delete_rsvp, name="delete_rsvp"),
    path("delete_event/", views.delete_event, name="delete_event"),
]
