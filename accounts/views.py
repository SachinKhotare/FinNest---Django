from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserLoginForm
from tenant.forms import TenantLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.views import expenses_view
from dashboard.models import Tenant

from .models import CustomUser

def home(request):
    return render(request, 'home.html')  # Or 'core/home.html' or wherever your file is

def rentals_view(request):
    # Sample data – this can be replaced with data from a database
    rentals = [
        {'property': 'Apartment A', 'tenant': 'Rahul Mehta', 'rent': 12000, 'due': '2025-08-10'},
        {'property': 'Apartment B', 'tenant': 'Sonia Patel', 'rent': 15000, 'due': '2025-08-15'},
    ]
    return render(request, 'rentals.html', {'rentals': rentals})

#login
def user_login(request):
    error = None  # For tenant login errors

    if request.method == "POST":
        login_type = request.POST.get("login_type")  # 'user' or 'tenant'

        # ================== USER LOGIN ==================
        if login_type == "user":
            user_form = UserLoginForm(request.POST)
            if user_form.is_valid():
                user_id = user_form.cleaned_data['id']
                password = user_form.cleaned_data['password']
                user= CustomUser.objects.get(id=user_id)
                #user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    request.session['user_id'] = user.id
                    return redirect("investment-Final")  # Replace with your user dashboard
                else:
                    messages.error(request, "Invalid username or password for User.")
            else:
                messages.error(request, "Please enter valid User credentials.")

        elif login_type == "tenant":
            # Tenant login logic
            form = TenantLoginForm(request.POST)
            if form.is_valid():
                tenant_id = form.cleaned_data['id']
                password = form.cleaned_data['password']

                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                    if tenant.password == password:  # ⚠️ Plain text, ideally hash it
                        request.session['tenant_id'] = tenant.id
                        return redirect('pay_rent')  # Replace with your tenant dashboard
                    else:
                        error = "Incorrect password"
                except Tenant.DoesNotExist:
                    error = "Tenant ID not found"
            else:
                error = "Please enter valid tenant credentials"

        else:
            messages.error(request, "Please select User or Tenant.")

    else:
        # GET request, instantiate empty forms
        user_form = UserLoginForm()
        tenant_form = TenantLoginForm()

    return render(
        request,
        "login copy.html",
        {
            "user_form": UserLoginForm(),
            "tenant_form": TenantLoginForm(),
            "error": error
        }
    )

#@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')  # Or success page
        else:
            print("Form Errors:", form.errors)  # DEBUG
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})