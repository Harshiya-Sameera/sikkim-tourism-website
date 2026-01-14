from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailOTP
import random 
from django.contrib.auth.views import PasswordResetView
from .utils import redirect_user_dashboard

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username') # The field name in your HTML
        password = request.POST.get('password')
        
        # Check if user exists first to provide a specific 'Inactive' message
        user_exists = User.objects.filter(email=email).first()
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Check for admin approval if applicable
            if hasattr(user, 'role') and user.role == 'admin' and not getattr(user, 'is_approved', True):
                messages.error(request, 'Admin account pending approval.')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            user.login_count = getattr(user, 'login_count', 0) + 1
            user.save()
            return redirect_user_dashboard(user)
        else:
            # If authentication failed, check if it was because the user is inactive
            if user_exists and not user_exists.is_active:
                messages.error(request, 'Please verify your email/OTP first.')
            else:
                messages.error(request, 'Invalid email or password.')
            
    return render(request, 'accounts/login.html')
# accounts/views.py

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'tourist')

        if User.objects.filter(email=email).exists():
            messages.info(request, 'User already exists! Please login instead.')
            return redirect('login') # Changed to login for better UX

        user = User.objects.create_user(email=email, password=password, role=role, is_active=False)
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        try:
            send_mail(
                'Verify Your Sikkim Tourism Account',
                f'Your Verification Code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False, 
            )
            request.session['verify_user'] = user.id
            # This redirect uses the name 'verify_otp' from your urls.py
            return redirect('verify_otp') 
            
        except Exception as e:
            # If email fails, delete the inactive user so they can try again
            user.delete() 
            messages.error(request, f'Error sending verification email: {str(e)}')
            return render(request, 'accounts/signup.html') # Return here to stop execution

    return render(request, 'accounts/signup.html')

def verify_otp_view(request):
    user_id = request.session.get('verify_user')
    if not user_id: return redirect('signup')
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()

        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.is_verified = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')
        else:
            messages.error(request, 'Invalid or expired code.')

    return render(request, 'accounts/verify_otp.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'