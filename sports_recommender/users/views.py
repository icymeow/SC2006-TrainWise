from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import logout

@login_required
def delete_account(request):
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text')
        if confirm_text == 'DELETE':
            # Delete the user account
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, _('Your account has been successfully deleted.'))
            return redirect('/accounts/login/')  # Redirect to login page
        else:
            messages.error(request, _('Please type DELETE to confirm account deletion.'))
    
    return render(request, 'account/delete_account.html') 