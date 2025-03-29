from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import json

from activities.models import Activity, ActivityHistory
from activities.forms import ActivityHistoryForm

@login_required
def workout_history_list_controller(request):
    """Display user's workout history."""
    history_entries = ActivityHistory.objects.filter(user=request.user).order_by('-date_completed')
    context = {
        'history_entries': history_entries,
    }
    return render(request, 'activities/workout_history.html', context)

@login_required
def add_to_history_form_controller(request, pk):
    """Display form for adding activity to history."""
    activity = get_object_or_404(Activity, pk=pk)
    
    if request.method == 'POST':
        form = ActivityHistoryForm(request.POST)
        if form.is_valid():
            history_entry = form.save(commit=False)
            history_entry.user = request.user
            history_entry.activity = activity
            history_entry.save()
            messages.success(request, 'Workout added to history successfully!')
            return redirect('activities:workout_history')
    else:
        form = ActivityHistoryForm()
    
    context = {
        'activity': activity,
        'form': form,
    }
    return render(request, 'activities/add_to_history.html', context)

@login_required
@require_http_methods(["POST"])
def add_to_history_controller(request):
    """Add an activity to user's history via AJAX."""
    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        date_completed = data.get('date_completed')
        duration = data.get('duration', {})
        notes = data.get('notes')
        rating = data.get('rating')
        
        if not activity_id or not date_completed:
            return JsonResponse({
                'success': False,
                'error': 'Activity ID and date are required'
            }, status=400)
        
        activity = Activity.objects.get(id=activity_id)
        
        # Convert duration to timedelta
        duration_timedelta = timedelta(
            hours=duration.get('hours', 0),
            minutes=duration.get('minutes', 0)
        )
        
        # Create history entry
        history_entry = ActivityHistory.objects.create(
            user=request.user,
            activity=activity,
            date_completed=date_completed,
            duration=duration_timedelta,
            notes=notes,
            rating=rating
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Activity added to history successfully'
        })
    except Activity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Activity not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error adding to history: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
def remove_from_history_controller(request, pk):
    """Remove an activity from user's history."""
    try:
        history_entry = ActivityHistory.objects.get(id=pk, user=request.user)
        history_entry.delete()
        messages.success(request, 'Workout removed from history successfully!')
        return JsonResponse({
            'success': True,
            'message': 'Activity removed from history'
        })
    except ActivityHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'History entry not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error removing from history: {str(e)}'
        }, status=500) 