from django.shortcuts import render, redirect, get_object_or_404
from .forms import TenantForm, AddStockForm, AddSIPForm, TransactionForm, UpdateStockForm,UpdateSIPForm
from .models import Tenant, AddStock, AddSIP, CustomUser, Transaction
from django.http import JsonResponse
from datetime import timedelta, datetime
import calendar
from django.contrib.auth.decorators import login_required
from tenant.models import RaiseIssue, VacateNotice, RaiseIssue, Payment
from django.utils.timezone import now
from .models import Transaction







# Create your views here.
def base_view(request):
    return render(request, 'base.html')

#Addon_View
def addon_view(request):
    return render(request, 'Add-On Final.html')

#Investement_view
@login_required
def investment_view(request):
    stock_form = AddStockForm()
    update_stock_form = UpdateStockForm()
    sip_form = AddSIPForm()
    update_sip_form = UpdateSIPForm()

    if request.method == 'POST':
        # --- STOCK: Add ---
        if 'add_stock' in request.POST:
            stock_form = AddStockForm(request.POST)
            if stock_form.is_valid():
                stock = stock_form.save(commit=False)
                stock.user = request.user
                stock.save()
                return redirect('investment-Final')

        # --- STOCK: Update ---
        elif 'update_stock' in request.POST:
            update_stock_form = UpdateStockForm(request.POST)
            update_stock_form.fields['stock'].queryset = AddStock.objects.filter(user=request.user)

            if update_stock_form.is_valid():
                stock = update_stock_form.cleaned_data['stock']
                new_qty = update_stock_form.cleaned_data['new_quantity']
                new_buy_price = update_stock_form.cleaned_data['new_buy_price']

                total_existing_value = stock.quantity * stock.buy_price
                total_new_value = new_qty * new_buy_price
                new_total_qty = stock.quantity + new_qty

                stock.buy_price = (total_existing_value + total_new_value) / new_total_qty
                stock.quantity = new_total_qty
                stock.save()

                return redirect('investment-Final')

        # --- SIP: Add ---
        elif 'add_sip' in request.POST:
            sip_form = AddSIPForm(request.POST)
            if sip_form.is_valid():
                sip = sip_form.save(commit=False)
                sip.user = request.user
                sip.save()
                return redirect('investment-Final')
        
        elif 'delete_stock' in request.POST:
            stock_id = request.POST.get("stock_id")
            if stock_id:  # ensure it's not empty
                AddStock.objects.filter(id=int(stock_id), user=request.user).delete()
                return redirect('investment-Final')

        # --- SIP: Update ---
        elif 'update_sip' in request.POST:
            update_sip_form = UpdateSIPForm(request.POST)
            update_sip_form.fields['sip'].queryset = AddSIP.objects.filter(user=request.user)

            if update_sip_form.is_valid():
                sip = update_sip_form.cleaned_data['sip']
                sip.monthly_amount = update_sip_form.cleaned_data['new_monthly_amount']
                sip.due_date = update_sip_form.cleaned_data['new_due_date']
                sip.save()
                return redirect('investment-Final')

        # --- SIP: Delete ---
        elif 'delete_sip' in request.POST:
            sip_id = request.POST.get("sip_id")
            AddSIP.objects.filter(id=sip_id, user=request.user).delete()
            return redirect('investment-Final')

    # Fetch user data
    stocks = AddStock.objects.filter(user=request.user)
    sips = AddSIP.objects.filter(user=request.user)

    # Bind querysets
    update_stock_form.fields['stock'].queryset = stocks
    update_sip_form.fields['sip'].queryset = sips

    return render(request, 'investment-Final.html', {
        'stock_form': stock_form,
        'update_stock_form': update_stock_form,
        'sip_form': sip_form,
        'update_sip_form': update_sip_form,
        'stocks': stocks,
        'sips': sips,
    })


# ✅ AJAX: Get SIP details
def get_sip_details(request, sip_id):
    sip = get_object_or_404(AddSIP, id=sip_id, user=request.user)
    data = {
        'monthly_amount': float(sip.monthly_amount),
        'due_date': sip.due_date.strftime('%Y-%m-%d'),
    }
    return JsonResponse(data)

# ✅ AJAX view to fetch stock details
def get_stock_details(request, stock_id):
    stock = get_object_or_404(AddStock, id=stock_id, user=request.user)
    data = {
        'quantity': stock.quantity,
        'buy_price': float(stock.buy_price),
    }
    return JsonResponse(data)


#Owner-Rental_View
@login_required
def owner_rental(request):
    form = TenantForm()  # always initialize form

    if request.method == 'POST':
        # Handle add tenant
        if 'add_tenant' in request.POST:
            form = TenantForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('owner-rental')

        # Handle delete tenant
        elif 'delete_tenant' in request.POST:
            tenant_id = request.POST.get('tenant_id')
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant.delete()
            return redirect('owner-rental')

    tenants = Tenant.objects.all()  # fetch all tenants

    return render(request, 'owner-rental.html', {
        'form': form,
        'tenants': tenants,
    })


def get_agreement_details(request, tenant_id):
    rental_details = get_object_or_404(Tenant, id=tenant_id)

    # ================== Rent Records ==================
    rent_records = []
    payments = Payment.objects.filter(tenant=rental_details).order_by("month")

    if payments.exists():
        for pay in payments:
            rent_records.append({
                "month": pay.month,
                "amount": pay.amount,
                "status": pay.status,
                
            })
    else:
        current_date = rental_details.start_date
        for i in range(11):
            month_name = current_date.strftime("%B %Y")
            rent_records.append({
                "month": month_name,
                "amount": rental_details.monthly_rent,
                "status": "Not Paid",
                
            })
            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            current_date += timedelta(days=days_in_month)

    # ================== Issues ==================
    issues = list(
        RaiseIssue.objects.filter(tenant=rental_details)
        .values("id", "title", "created_at", "status", "details")
    )

    # ================== Vacate Notices ==================
    vacate_notices = list(
        VacateNotice.objects.filter(tenant=rental_details)
        .values("id", "reason", "date", "flat_no", "name")   # ✅ added correct fields
    )

    # ================== Final Response ==================
    data = {
        "rent": f"{rental_details.monthly_rent}",
        "start_date": rental_details.start_date.strftime("%d-%b-%Y"),
        "end_date": rental_details.end_date.strftime("%d-%b-%Y"),
        "contact": rental_details.contact_number,
        "address": rental_details.address,
        "agreement_file": request.build_absolute_uri(rental_details.agreement_file.url) if rental_details.agreement_file else "",
        "aadhar_photo": request.build_absolute_uri(rental_details.aadhar_photo.url) if rental_details.aadhar_photo else "",
        "rent_records": rent_records,
        "issues": issues,
        "vacate_notices": vacate_notices,
    }
    return JsonResponse(data)


@login_required
def get_issues_by_tenant(request):
    tenant_id = request.GET.get("tenant_id")
    if tenant_id:
        issues = RaiseIssue.objects.filter(tenant_id=tenant_id).order_by("-created_at")
    else:
        issues = RaiseIssue.objects.all().order_by("-created_at")

    data = []
    for issue in issues:
        data.append({
            "tenant": issue.tenant.username,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status,
            "created_at": issue.created_at.strftime("%Y-%m-%d %H:%M")
        })

    return JsonResponse({"issues": data})


#Expenses_View
@login_required
def expenses_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)  # don't save yet
            transaction.user = request.user        # assign logged-in user
            transaction.save()                     # now save
            return redirect('expenses')
        else:
            print("Form errors:", form.errors)  # ✅ Debug here
    else:
        form = TransactionForm()

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')  # show only logged-in user's data
    current_month_transactions = transactions.filter(date__month=now().month, date__year=now().year)
    categories  = Transaction.objects.values_list("category", flat=True).distinct()
    current_month_total = sum(tx.amount for tx in current_month_transactions if tx.transaction_type == "Expense")
    overall_total = sum(tx.amount for tx in transactions if tx.transaction_type == "Expense")

    context = {
        'transactions': transactions,
        'form': form,
        "categories": categories,
        'current_month_total': current_month_total,
        'overall_total': overall_total,
        'percentage_month': (current_month_total / overall_total * 100) if overall_total else 0,
    }
    return render(request, "Expenses.html", context)


