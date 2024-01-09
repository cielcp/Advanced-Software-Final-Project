from django import forms
from django.forms.widgets import NumberInput
from django.forms import ModelForm, SplitDateTimeField, SplitDateTimeWidget
from .models import Event, Rsvp
from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput


class CreateEventForm(ModelForm, forms.Form):
    start_datetime = SplitDateTimeField(widget=SplitDateTimeWidget(date_attrs={"type": "date"}, time_attrs={"type": "time"}))
    end_datetime = SplitDateTimeField(widget=SplitDateTimeWidget(date_attrs={"type": "date"}, time_attrs={"type": "time"}))
    class Meta:
        model = Event
        exclude = ['latitude', 'longitude', 'host_user', 'event_id']
      #  widgets = {
      #         "startdate" :DatePickerInput(options={"format": "MM-DD-YYYY"}),
      #          "start" : TimePickerInput(options={"format": "HH:mm"}),
      #          "end" : TimePickerInput(options={"format": "HH:mm"}),
      #  }

        
class RSVPForm(ModelForm):
    class Meta:
        model = Rsvp
        fields = ['name', 'note']
        exclude = ['host_user', 'username']
