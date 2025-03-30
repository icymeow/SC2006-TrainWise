from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Activity
from apps.recommendations.models import FavoriteActivity

def activity_list(request):
    activities = Activity.objects.all()
    return render(request, 'activities/activity_list.html', {'activities': activities})

def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteActivity.objects.filter(user=request.user, activity=activity).exists()
    return render(request, 'activities/activity_detail.html', {
        'activity': activity,
        'is_favorite': is_favorite
    })

@login_required
def toggle_favorite(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    favorite, created = FavoriteActivity.objects.get_or_create(user=request.user, activity=activity)
    if not created:
        favorite.delete()
    return JsonResponse({'is_favorite': created}) 