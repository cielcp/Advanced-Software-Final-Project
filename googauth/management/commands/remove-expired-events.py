
from django.core.management.base import BaseCommand
from googauth.models import Event, Rsvp
from datetime import datetime

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-a', "--all", action="store_true")


    def handle(self, *args, **options):
        print(" (*) Attempting to clear expired events...")
        print(" (*) Current time:   ",datetime.now())
        exp_events = Event.objects.all().filter(end_datetime__lt=datetime.now())
        if exp_events.count() == 0:
            print("(*) No expired events found.")
        else:
            for event in exp_events:
                print("(*) Found expired event:",event.name)
                if not (options['all']):
                    inp = input("(*) Are you sure you want to delete this event? (y/n) ")
                    match inp:
                        case 'y':
                            print("(*) Deleting",event.name+"...")
                            event.delete()
                        case 'n':
                            print("(*) Keeping",event.name+"...")
                            continue
                else:
                    print("(*) Deleting",event.name+"...")
                    event.delete()


        


