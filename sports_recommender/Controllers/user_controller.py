from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from ..Database.user_database import UserDatabase
from ..UI.forms.user_forms import UserRegistrationForm, UserProfileForm, FirstTimePreferencesForm

class UserRegistrationController(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'UI/templates/users/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Send verification email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = self.request.build_absolute_uri(
            f'/users/verify/{uid}/{token}/'
        )
        
        send_mail(
            'Verify your email address',
            f'Please click the following link to verify your email: {verification_url}',
            'noreply@example.com',
            [user.email],
            fail_silently=False,
        )
        
        messages.success(self.request, 'Please check your email to verify your account.')
        return response

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserDatabase.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserDatabase.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        login(request, user)
        messages.success(request, 'Your email has been verified!')
        return redirect('first_time_preferences')
    else:
        messages.error(request, 'Invalid verification link.')
        return redirect('login')

@login_required
def first_time_preferences_controller(request):
    if not request.user.is_first_time:
        return redirect('home')
        
    if request.method == 'POST':
        form = FirstTimePreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_first_time = False
            user.save()
            messages.success(request, 'Your preferences have been saved!')
            return redirect('home')
    else:
        form = FirstTimePreferencesForm(instance=request.user)
    
    return render(request, 'UI/templates/users/first_time_preferences.html', {'form': form})

@login_required
def user_profile_controller(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'UI/templates/users/profile.html', {'form': form})

@login_required
def delete_account_controller(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email != request.user.email:
            messages.error(request, 'Email address does not match your account.')
            return redirect('delete_account')
            
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid password. Please try again.')
            return redirect('delete_account')
            
    return render(request, 'UI/templates/users/delete_account.html')

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = UserDatabase.objects.get(email=email)
            if not user.is_verified:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_url = request.build_absolute_uri(
                    f'/users/verify/{uid}/{token}/'
                )
                
                send_mail(
                    'Verify your email address',
                    f'Please click the following link to verify your email: {verification_url}',
                    'noreply@example.com',
                    [user.email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Verification email has been resent.')
            else:
                messages.info(request, 'Your email is already verified.')
        except UserDatabase.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            
    return redirect('login') 