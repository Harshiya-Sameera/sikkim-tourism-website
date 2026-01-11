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
        email = request.POST.get('username') # Form input field name is 'username'
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.role == 'admin' and not user.is_approved:
                messages.error(request, 'Admin account pending approval.')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            user.login_count += 1
            user.save()
            return redirect_user_dashboard(user)
        else:
            messages.error(request, 'Invalid email or password.')
            
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'tourist')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        user = User.objects.create_user(email=email, password=password, role=role, is_active=False)
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        try:
            send_mail(
                'Verify Your Sikkim Tourism Account',
                f'Your Verification Code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
            )
            request.session['verify_user'] = user.id
            return redirect('verify_otp')
        except Exception:
            messages.error(request, 'Error sending verification email.')

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