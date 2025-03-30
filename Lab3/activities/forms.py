from django import forms
from .models import ActivityHistory, UserPreference, Activity

class ActivityHistoryForm(forms.ModelForm):
    """Form for adding an activity to workout history."""
    class Meta:
        model = ActivityHistory
        fields = ['date_completed', 'duration', 'rating', 'notes']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 

class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['name', 'age', 'gender', 'preferred_activity_types', 'max_distance', 'indoor_preference']
        widgets = {
            'preferred_activity_types': forms.CheckboxSelectMultiple(choices=[
                ('Gym', 'Gym'),
                ('Swimming', 'Swimming'),
                ('Running', 'Running'),
                ('Cycling', 'Cycling'),
                ('Basketball', 'Basketball'),
                ('Tennis', 'Tennis'),
                ('Yoga', 'Yoga'),
                ('Dance', 'Dance')
            ])
        }

    def clean_preferred_activity_types(self):
        activities = self.cleaned_data.get('preferred_activity_types')
        if activities:
            return ','.join(activities)
        return ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.preferred_activity_types:
            self.initial['preferred_activity_types'] = instance.get_preferred_activity_types()

class ActivitySearchForm(forms.Form):
    SORT_CHOICES = [
        ('distance', 'Distance'),
        ('popularity', 'Popularity'),
        ('recommended', 'Recommended'),
    ]
    
    LOCATION_CHOICES = [
        ('', 'All Locations'),
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]
    
    # Search query
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search activities...'
        })
    )
    
    # Filters
    activity_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Activity.ACTIVITY_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    location_type = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Location
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput())
    address = forms.CharField(required=False, widget=forms.HiddenInput())
    
    # Sorting
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Distance radius (in kilometers)
    radius = forms.FloatField(
        required=False,
        min_value=0.1,
        max_value=100.0,
        initial=10.0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    ) 