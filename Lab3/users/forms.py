from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserDatabase

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
    favorite_sports = forms.MultipleChoiceField(
        choices=[
            ('running', 'Running/Jogging/Walking'),
            ('swimming', 'Swimming'),
            ('badminton', 'Badminton'),
            ('basketball', 'Basketball'),
            ('tennis', 'Tennis'),
            ('table_tennis', 'Table Tennis'),
            ('volleyball', 'Volleyball'),
            ('pickleball', 'Pickleball'),
            ('gym', 'Gym'),
            ('soccer', 'Soccer'),
            ('squash', 'Squash'),
            ('netball', 'Netball'),
            ('lawn_bowl', 'Lawn Bowl'),
            ('hockey', 'Hockey'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = UserDatabase
        fields = ['age', 'favorite_sports', 'preferred_intensity', 'preferred_weather']
        widgets = {
            'age': forms.NumberInput(attrs={'min': 1, 'max': 120}),
        } 