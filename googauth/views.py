from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from .models import UserProfile, Event, Rsvp
from django.db import IntegrityError
from .forms import CreateEventForm, RSVPForm #, EventDetailForm
import requests
import json
from django.shortcuts import render, get_object_or_404
from .models import Event, Rsvp
from django.utils import timezone
from django.contrib import messages
from datetime import datetime


@login_required
def choose_role(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    # If the user has already chosen a role, redirect them to the appropriate dashboard
    if user_profile.has_chosen_role:
        if request.user.is_staff:
            return HttpResponseRedirect('/admin_dash/')
        else:
            return HttpResponseRedirect('/user_dash/')
    # If the user is making a POST request (i.e., they're submitting the choose_role form)
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_profile.set_role(user_type)

        # Redirect to the appropriate dashboard based on their role
        if request.user.is_staff:
            return HttpResponseRedirect('/admin_dash/')
        else:
            return HttpResponseRedirect('/user_dash/')
    return render(request, 'account/choose_role.html')

def rsvp(data, username, event_id):
    event = get_object_or_404(Event, pk=event_id)
    message = ""
    status = False
    host = Event.objects.get(pk=event_id).host_user
    user_rsvp = Rsvp.objects.all().filter(event_id=event_id).filter(username=username)
    if user_rsvp.count() >= 1:
        message = "You have already RSVP'd for this event!"
        print(message) # Prevent a user from RSVPing multiple times
        return message, status
    if host == str(username): # Prevent an admin user from rsvping for their own event
        message = "You cannot RSVP to your own event!"
        print(message)
        return message, status
    print("RSVPing...\n")
    r = Rsvp(name=data['name'], datetime = timezone.now(), username=username, event_id=event_id)
    if 'note' in data.keys():
        r.note = data['note']
    r.save()
    status = True
    message = "Successfully RSVP'd!"
    print("- Successfully RSVP'd with data:", "\n- - RSVP Username:",r.username, "\n- - Entered Name:",r.name,"\n- - Time of RSVP:",r.datetime, "\n- - ID of Event:",r.event_id, "\n- - Note (IF AVAIL):",r.note)
    return message, status


# View to create a new event from user input to the Event Form
def create_event(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an event.")
        return redirect('home')  # Replace 'login' with your actual login view's name

    form = CreateEventForm()

    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            # if the admin has made too many events (why do we need to limit this?)
            if len(admin_get_events(request.user)) >= 3:
                messages.error(request, "You have reached the limit of created events.")
                return render(request, 'dashboard/create_event.html', {'form': form})
            
            # if the input end time is before the start time
            if form.cleaned_data['start_datetime'] >= form.cleaned_data['end_datetime']:
                messages.error(request, "Please enter a valid start and end time for your event.")
                return render(request, 'dashboard/create_event.html', {'form': form})
            
            # if they try to input a name with a ' or "
            if ("'" or '"') in form.cleaned_data['name']:
                messages.error(request, "Please input a name without an apostrophe or quotation.")
                return render(request, 'dashboard/create_event.html', {'form': form})

            # Get latitude and longitude from the form address
            latitude, longitude = get_latitude_longitude(form.cleaned_data['address'])
            if latitude is None or longitude is None:
                messages.error(request, "Could not obtain coordinates for the given address. Please make sure the address is correct.")
                return render(request, 'dashboard/create_event.html', {'form': form})

            # Create the event with the validated form data
            event = form.save(commit=False)
            event.host_user = request.user  # Set the current user as the host
            event.latitude = latitude
            event.longitude = longitude

            try:
                event.save()
                messages.success(request, "Event created successfully!")
                return redirect('all_events')  # Replace 'all_events' with your actual view's name
            except IntegrityError as e:
                messages.error(request, f"An error occurred while saving the event: {e}")
                return render(request, 'dashboard/create_event.html', {'form': form})
        else:
            messages.error(request, "There was an error with your form. Please check your input.")

    return render(request, 'dashboard/create_event.html', {'form': form})

def admin_dash(request):
    try:
        print(request.user)    
    except:
        return HttpResponseRedirect('/home/')

    if not request.user.is_staff: # Stops a regular user from accessing admin dash
        return HttpResponseRedirect('/user_dash/')
    user = request.user
    event_list = Event.objects.all().filter(host_user = user)
    # get all of the user's rsvps
    rsvps = Rsvp.objects.all().filter(username = user)
    rsvps_list = []
    for i in rsvps:
        rsvps_list.append(i.event_id)
    # get all of the events corresponding to the rsvps
    rsvpd_list = Event.objects.all().filter(pk__in=rsvps_list)
    context = {'event_list': event_list, 'rsvpd_list': rsvpd_list}
    return render(request, 'dashboard/admin_dash.html', context)

def delete_rsvp(request, rsvp_id, event_id) :

    try:
        print(request.user)    
    except:
        return HttpResponseRedirect('/home/')

    event = get_object_or_404(Event, pk=event_id)

    if request.user.username != event.host_user:    # If someone is trying to delete an rsvp who isn't this event's host, kick them.
        print("You don't have permission to do that!")
        return HttpResponseRedirect("/home")

    status = True
    message = "Successfully Removed RSVP"
    messages.success(request, "Successfully removed RSVP")
    Rsvp.objects.all().get(id=rsvp_id).delete()
    print("Deleting", rsvp_id)
    return render(request, 'dashboard/event.html', {'event': event, 'status':status, 'message': message})


    # return render(request, 'dashboard/event.html', {'event': event, 'status':status, 'message': message})


def delete_event(event_id):
    print("deleting:",event_id)

def user_dash(request):
    # try:
    #     print(request.user)    
    # except:
    #     return HttpResponseRedirect('/home/')

    # if request.user.is_staff: # Stops an admin user from accessing user dash.
    #     return HttpResponseRedirect('/admin_dash/')
    #
    # This is a little bit broken. The query to get the events that the user is attending is getting the wrong pks and I don't really know why.
    # It's probably not a hard fix, but I don't have the energy right now.
    #
    # - Elliott
    #
    user = request.user
    # get all of the user's rsvps
    rsvps = Rsvp.objects.all().filter(username = user)
    rsvps_list = []
    for i in rsvps:
        rsvps_list.append(i.event_id)
    print(rsvps_list)
    # get all of the events corresponding to the rsvps
    event_list = Event.objects.all().filter(pk__in=rsvps_list)
    print(event_list)
    context = {'event_list': event_list}
    return render(request, 'dashboard/user_dash.html', context)

def admin_get_events(username):
    events = [event for event in Event.objects.all().filter(host_user=username)]
    print(events)
    return events

# Function to get coordinates of event based off of the address
def get_latitude_longitude(address):
    # Make a request to the Google Geocoding API to obtain latitude and longitude
    api_key = 'AIzaSyCJG17X5Sxvun2t22U7WkKLx3scp9FfRM0' # new api key, only for geocoding
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': api_key,
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data.get('status') == 'OK':
            # print('okey dokey')
            result = data['results'][0]
            geometry = result['geometry']
            location = geometry['location']
            return location['lat'], location['lng']
    except Exception as e:
        # Handle exceptions (e.g., API request failure, invalid address)
        print("API request failure or invalid address")
        pass
    return None, None


# View to list all events and map with markers for each event
def all_events(request):
    context = {}
    event_list = Event.objects.all()
    #now = datetime.now()

    #curr_events = []
    #for event in event_list:
    #    print("shit:", type(now), type(event.start), type(event.end))
    #    if (event.start <= now and now <= event.end):
    #        curr_events.append(event)
    
    #upcoming_events = []
    #for event in event_list:
    #    if (event.start > now):
    #        upcoming_events.append(event)
    if event_list.count() > 0:
        event_coordinates = [{'lat': str(event.latitude), 'lng': str(event.longitude)} for event in event_list]
        event_names = [{'name': str(event.name)} for event in event_list]
        # Create a list of event URLs for each event in the context
        event_urls = [reverse('event', args=[event.id]) for event in event_list]

        context = {
            'event_list': event_list,
            #'curr_events': curr_events,
            #'upcoming_events': upcoming_events,
            'event_coordinates': json.dumps(event_coordinates),
            'event_names': json.dumps(event_names),
            'event_urls': event_urls  # Pass the list of event URLs in the context
        }

    return render(request, 'dashboard/all_events.html', context)

# Same map for home screen
def home(request):
    event_list = Event.objects.all()
    event_coordinates = [{'lat': str(event.latitude), 'lng': str(event.longitude)} for event in event_list]
    return render(request, 'dashboard/home.html', {'event_list': event_list, 'event_coordinates': json.dumps(event_coordinates)})

    
# View to show event details and allow users to RSVP, leave ratings, etc.
def event_detail(request, pk):
    message = None
    status = False
    form = RSVPForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        message, status = rsvp(data, request.user, pk)
        messages.error(request, message)
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'dashboard/event.html', {'event': event, 'status':status, 'message': message})

# ciel workin on stuff
""" def rsvp_to_event(request, pk):
    event = Event.objects.get(pk=pk)
    user = request.user

    # Check if the user has already RSVPed to the event
    if not rsvp2.objects.filter(user=user, event=event).exists():
        rsvp2.objects.create(user=user, event=event)
        # You can add a success message or other logic here
    else:
        # User has already RSVPed, is now unclicking the button??
        rsvp2.objects.delete(user=user, event=event)
        # You can display an error message or handle it as needed

    return redirect('event_detail', pk=pk) """

# work in progress for pop up:
"""def get_event_data(request):
    events = Event.objects.all()
    event_data = [
        {
            'name': event.name,
            'location': event.location,
            'latitude': float(event.latitude),
            'longitude': float(event.longitude),
        }
        for event in events
    ]

    return JsonResponse(event_data, safe=False)"""
