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
    preferred_activity_types = forms.MultipleChoiceField(
        choices=UserPreference.ACTIVITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = UserPreference
        fields = ['name', 'age', 'gender', 'preferred_activity_types', 'max_distance', 'indoor_preference']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'max_distance': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1', 'max': '100', 'step': '0.1'}),
            'indoor_preference': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_preferred_activity_types(self):
        """Convert the list of selected activities into a comma-separated string."""
        print("Cleaning preferred_activity_types")  # Debug log
        activities = self.cleaned_data.get('preferred_activity_types', [])
        print(f"Activities from cleaned_data: {activities}")  # Debug log
        
        # Don't return empty string if no activities, return empty list instead
        if not activities:
            return []
            
        # Validate against allowed choices
        valid_activities = [choice[0] for choice in UserPreference.ACTIVITY_CHOICES]
        valid_list = [act for act in activities if act in valid_activities]
        print(f"Valid activities after cleaning: {valid_list}")  # Debug log
        return valid_list  # Return the list directly, let the view handle joining

    def __init__(self, *args, **kwargs):
        print("\n=== Initializing UserPreferenceForm ===")  # Debug log
        super().__init__(*args, **kwargs)
        
        instance = kwargs.get('instance')
        if instance:
            print(f"Instance preferred_activity_types: {instance.preferred_activity_types}")  # Debug log
            if instance.preferred_activity_types:
                # Convert comma-separated string back to list for the form
                activities = instance.get_preferred_activity_types()
                print(f"Setting initial preferred_activity_types to: {activities}")  # Debug log
                self.initial['preferred_activity_types'] = activities

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