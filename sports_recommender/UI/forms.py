from django import forms
from .models import ActivityHistory

class ActivityHistoryForm(forms.ModelForm):
    class Meta:
        model = ActivityHistory
        fields = ['date_completed', 'duration', 'notes', 'rating']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
        } 