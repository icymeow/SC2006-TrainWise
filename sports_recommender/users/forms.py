from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserDatabase
from ..activities.models import UserPreference

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserDatabase
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserDatabase
        fields = ['username', 'email', 'age', 'notification_enabled']

class FirstTimePreferencesForm(forms.ModelForm):
    preferred_activity_types = forms.MultipleChoiceField(
        choices=UserPreference.ACTIVITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        help_text="Select the activities you're interested in"
    )
    
    class Meta:
        model = UserPreference
        fields = ['age', 'preferred_activity_types', 'indoor_preference']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 120}),
            'indoor_preference': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean_preferred_activity_types(self):
        """Convert the list of selected activities into a comma-separated string."""
        activities = self.cleaned_data.get('preferred_activity_types', [])
        if not activities:
            raise forms.ValidationError("Please select at least one activity.")
        # Validate against allowed choices
        valid_activities = [choice[0] for choice in UserPreference.ACTIVITY_CHOICES]
        valid_list = [act for act in activities if act in valid_activities]
        return ','.join(valid_list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.preferred_activity_types:
            # Convert comma-separated string back to list for the form
            self.initial['preferred_activity_types'] = instance.get_preferred_activity_types() 