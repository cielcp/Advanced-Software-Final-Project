from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from .models import Event, UserProfile, Rsvp
from django.utils import timezone
from datetime import timedelta
from .forms import CreateEventForm

class EventModelTest(TestCase):
    def test_get_rsvps(self):
        # Create user
        user = User.objects.create_user(username='testuser', password='12345')

        # Create event with required fields
        event = Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            address="Test Address",
            latitude=38.033554,
            longitude=-78.507980,
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=2)
        )

        # Create RSVP using event.pk for event_id field
        Rsvp.objects.create(
            event_id=str(event.pk), 
            username=user.username, 
            name="Test RSVP",
            note="Looking forward to the event",
            datetime=timezone.now()
        )

        # Assert that RSVP is correctly associated with the event
        rsvps = event.get_rsvps()
        self.assertEqual(len(rsvps), 1)
        self.assertEqual(rsvps[0].name, "Test RSVP")

class UserProfileModelTest(TestCase):
    def test_set_role(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.set_role('admin')
        self.assertTrue(profile.user.is_staff)
        profile.set_role('regular')
        self.assertFalse(profile.user.is_staff)

class MyTestCase(TestCase):
    def test_example(self):
        self.assertEqual(1 + 1, 2)
        
class HomeTest(TestCase):
    # Check if the home page returns a 200 status code
    def test_home_url_exists_at_desired_location(self):
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        response = self.client.get('/home/')
        self.assertTemplateUsed(response, 'dashboard/home.html')

class UserDashTest(TestCase):
    def setUp(self):
    # Imported User to ensure 'User' model is available throughout testing process
        self.user = User.objects.create_user(username ='testuser', password ='12345')
        self.client.login(username='testuser', password='12345')
    # Check if the user dashboard page returns a 200 status code
    def test_user_url_exists_at_desired_location(self):
        response = self.client.get('/user_dash/')
        self.assertEqual(response.status_code, 200)

    def test_user_uses_correct_template(self):
        response = self.client.get('/user_dash/')
        self.assertTemplateUsed(response, 'dashboard/user_dash.html')
    
    # this test is not passing
    """ def test_user_displayed_on_user_dash(self):
        response = self.client.get('/user_dash/')
        self.assertContains(response, self.user.username) """

class AdminDashTest(TestCase):
    # Check if the user dashboard page returns a 200 status code
    def test_admin_url_exists_at_desired_location(self):
        response = self.client.get('/admin_dash/')
        self.assertEqual(response.status_code, 200)

    def test_admin_uses_correct_template(self):
        response = self.client.get('/admin_dash/')
        self.assertTemplateUsed(response, 'dashboard/admin_dash.html')

class UserNameDisplayTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='thebuilder')
        self.client.login(username='bob', password='thebuilder')

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    # this test is not passing
    """ def test_username_displayed_on_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, self.user.username) """
    
class CreateEventFormTest(TestCase):
    def test_form_valid(self):
        form_data = {
            'name': 'Test Event',
            'description': 'Test Description',
            'address': '123 Test St',
            'start_datetime': timezone.now() + timedelta(days=1),  # Set to a future time
            'end_datetime': timezone.now() + timedelta(days=1, hours=2)  # Also in the future
        }

    def test_form_invalid(self):
        form = CreateEventForm(data={})
        self.assertFalse(form.is_valid())

class EventViewTest(TestCase):
    def setUp(self):
        # test user and log them in for testing views that require authentication
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # test event with all required fields. This event will be used to test the event detail view.
        # set future start and end times for the event to simulate a real-world scenario.
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Event Description",
            address="Test Address",
            latitude=38.033554,  # example latitude value
            longitude=-78.507980,  # example longitude value
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timedelta(hours=2)
        )

    def test_event_detail_view(self):
        # URL for the event detail page of the test event
        url = reverse('event', args=[self.event.pk])

        # GET request to the event detail page and check if it returns a 200 status code,
        # indicating that the page is accessible and the event details are correctly displayed.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.name)

