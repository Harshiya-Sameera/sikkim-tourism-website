from django.shortcuts import redirect

def redirect_user_dashboard(user):
    if user.is_superuser or user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('landing') # Tourists go to the explore landing page