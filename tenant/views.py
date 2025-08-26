from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, RaiseIssue, VacateNotice
from .forms import TenantLoginForm, RaiseIssueForm, VacateNoticeForm
from django.contrib import messages
import razorpay
from django.core.mail import send_mail
from FinNest.settings import RAZORPAY_ID, RAZORPAY_SECRET, EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import calendar



def pay_rent(request):
    return render(request, 'Tenant/Pay_Rent.html')

def tenant_login(request):
    error = None
    if request.method == "POST":
        form = TenantLoginForm(request.POST)
        if form.is_valid():
            tenant_id = form.cleaned_data['id']
            password = form.cleaned_data['password']

            try:
                tenant = Tenant.objects.get(id=tenant_id)

                if tenant.password == password:  
                    request.session['tenant_id'] = tenant.id  # ✅ Store tenant id in session
                    return redirect('pay_rent')  # No need to pass tenant_id here
                else:
                    error = "Incorrect password"
            except Tenant.DoesNotExist:
                error = "Tenant ID not found"
    else:
        form = TenantLoginForm()

    return render(request, "Tenant/login_page.html", {"form": form, "error": error})


def tenant_logout(request):
    # Clear the session completely
    request.session.flush()  
    
    # Or just remove tenant_id only (if you want to keep other session data)
    # request.session.pop("tenant_id", None)

    return redirect("login_page")  # Redirect to login page



def dashboard_view(request):
    # Check if tenant is logged in
    if not request.session.get("tenant_id"):
        return redirect("login_page")  # redirect if not logged in

    # No need to fetch tenant here, context processor already provides tenant_info
    return render(request, "Tenant/Aggrement_copy.html")


def raise_issue(request):
    # Check if tenant is logged in
    if not request.session.get("tenant_id"):
        return redirect("login_page")  # Redirect if not logged in

    # tenant_info comes automatically from context processor
    tenant = None
    if hasattr(request, "ttenant_data"):
        tenant = request.tenant_info  # but safer to use context dict (see below)

    # or directly from context processor data
    from accounts.context_processors import user_info
    tenant_info = user_info(request).get("tenant_data")

    if request.method == "POST":
        form = RaiseIssueForm(request.POST, request.FILES)
        if form.is_valid() and tenant_info:
            issue = form.save(commit=False)
            issue.tenant = tenant_info   # ✅ use tenant from context processor
            issue.save()
            messages.success(request, "Issue raised successfully!")
            return redirect("raise-issue")
    else:
        form = RaiseIssueForm()

    # 🔹 Fetch only this tenant’s issues
    issues = []
    if tenant_info:
        issues = RaiseIssue.objects.filter(tenant=tenant_info).order_by("-created_at")

    return render(
        request,
        "Tenant/Raise Issue & Vacate Notice.html",
        {"form": form, "issues": issues}
    )

#vacate 

def submit_vacate_notice(request):
    # Check if tenant is logged in
    if not request.session.get("tenant_id"):
        return redirect("login_page")  

    # Get tenant info from context processor
    from accounts.context_processors import user_info
    tenant_info = user_info(request).get("tenant_data")

    if not tenant_info:
        return redirect("login_page")

    # ✅ Check if tenant already submitted a notice
    if hasattr(tenant_info, "vacate_notice"):
        messages.warning(request, "You have already submitted a vacate notice.")
        return redirect("raise-issue")

    if request.method == "POST":
        form = VacateNoticeForm(request.POST)
        if form.is_valid():
            vacate_notice = form.save(commit=False)
            vacate_notice.tenant = tenant_info   # ✅ use tenant from context processor
            vacate_notice.save()
            messages.success(request, "Vacate notice submitted successfully!")
            return redirect("raise-issue")
        else:
            print("❌ Form Errors:", form.errors)  # Debugging line
    else:
        form = VacateNoticeForm()

    return render(
        request,
        "Tenant/Raise Issue & Vacate Notice.html",
        {"form": form}
    )


#Payment

# Payment View

from .models import Payment
import calendar
from datetime import datetime

def payment(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("tenant_login")

    tenant = get_object_or_404(Tenant, id=tenant_id)

    from accounts.context_processors import user_info
    tenant_info = user_info(request).get("tenant_data")

    amount = int(tenant.monthly_rent) if tenant.monthly_rent else 500

    client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))
    data = {
        "amount": amount * 100,
        "currency": "INR",
        "receipt": f"tenant_{tenant_id}"
    }
    order = client.order.create(data=data)

    # ✅ Save initial payment (PENDING)
    if request.method == "POST":
        selected_month = request.POST.get("month")  # get month from form
    else:
        selected_month = datetime.now().strftime("%B")

 

    # Assume tenant has a `rent_start_date` field
    start_date = tenant.start_date  

    # Generate 11 months from rent_start_date
    from dateutil.relativedelta import relativedelta

    months = []
    for i in range(11):
        month_date = start_date + relativedelta(months=i)
        months.append(month_date.strftime("%B %Y"))


    # Fetch already paid months from RentPayment table
    paid_months = Payment.objects.filter(tenant=tenant, status="SUCCESS").values_list("month", flat=True)

    # Exclude paid months
    remaining_months = [m for m in months if m not in paid_months]

    context = {
        "payment": order,
        "razorpay_id": RAZORPAY_ID,
        "tenant": tenant,
        "tenant_id": tenant_id,
        "amount": amount,
        "tenant_info": tenant_info,
        "months": remaining_months,
        "current_month": selected_month,
    }
    return render(request, "Tenant/Pay_Rent.html", context)


from .models import Payment

def payment_success(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("tenant_login")

    tenant = get_object_or_404(Tenant, id=tenant_id)

    payment_id = request.GET.get("payment_id")
    order_id = request.GET.get("order_id")
    signature = request.GET.get("signature")
    month = request.GET.get("month")  # from JS

    # ✅ Create or update payment
    payment_obj, created = Payment.objects.get_or_create(
        order_id=order_id,
        tenant=tenant,
        defaults={
            "payment_id": payment_id,
            "signature": signature,
            "status": "SUCCESS",
            "month": month,
            "amount": tenant.monthly_rent,
        }
    )

    if not created:  # If already exists, just update
        payment_obj.payment_id = payment_id
        payment_obj.signature = signature
        payment_obj.status = "SUCCESS"
        payment_obj.month = month
        payment_obj.save()

    return render(request, "Tenant/payment_success.html", {
        "tenant": tenant,
        "payment_id": payment_id,
        "order_id": order_id,
        "signature": signature
    })



#rent history

def rent_history(request):
    tenant_id = request.session.get("tenant_id")
    if not tenant_id:
        return redirect("tenant_login")

    tenant = get_object_or_404(Tenant, id=tenant_id)

    # Fetch all payments for this tenant
    payments = Payment.objects.filter(tenant=tenant).order_by('-created_at')

    # Assuming you track payments for 11 months
    total_months = 11
    paid_months = payments.filter(status="SUCCESS").count()
    pending_months = total_months - paid_months

    return render(request, 'Tenant/Rent_History.html', {
        "tenant": tenant,
        "rent_history": payments,
        "pending_months": pending_months
    })

