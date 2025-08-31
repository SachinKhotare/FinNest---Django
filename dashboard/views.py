from django.shortcuts import render, redirect, get_object_or_404
from .forms import TenantForm, AddStockForm, AddSIPForm, TransactionForm, UpdateStockForm,UpdateSIPForm, SavingsGoalForm
from .models import Tenant, AddStock, AddSIP, CustomUser, Transaction, SavingsGoal, ExpenseBudget
from django.http import JsonResponse
from datetime import timedelta, datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from tenant.models import RaiseIssue, VacateNotice, RaiseIssue, Payment
from django.utils.timezone import now
from django.utils import timezone
from .models import Transaction
from django.contrib import messages
from django.contrib.messages import get_messages
from decimal import Decimal







# Create your views here.
def base_view(request):
    return render(request, 'base.html')


#Investement_view


@login_required
def investment_view(request):
    stock_form = AddStockForm()
    update_stock_form = UpdateStockForm()
    sip_form = AddSIPForm()
    update_sip_form = UpdateSIPForm()
    notifications = []  # store alerts here
    from datetime import datetime, date
    if request.method == 'POST':
        # --- STOCK: Add ---
        if 'add_stock' in request.POST:
            stock_form = AddStockForm(request.POST)
            if stock_form.is_valid():
                stock = stock_form.save(commit=False)
                stock.user = request.user
                stock.save()
                messages.success(request,  f"[{datetime.now().strftime('%I:%M %p')}] ✅ Stock '{stock.stock_name}' added successfully.")
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
                messages.info(request,  f"[{datetime.now().strftime('%I:%M %p')}] ✏️ Stock '{stock.stock_name}' updated successfully.")
                return redirect('investment-Final')

        # --- SIP: Add ---
        elif 'add_sip' in request.POST:
            sip_form = AddSIPForm(request.POST)
            if sip_form.is_valid():
                sip = sip_form.save(commit=False)
                sip.user = request.user
                sip.save()
                messages.success(request,  f"[{datetime.now().strftime('%I:%M %p')}] ✅ SIP '{sip.sip_name}' added successfully.")
                return redirect('investment-Final')
        
        elif 'delete_stock' in request.POST:
            stock_id = request.POST.get("stock_id")
            if stock_id:  # ensure it's not empty
                deleted = AddStock.objects.filter(id=int(stock_id), user=request.user).first()
                if deleted:
                    messages.error(request,  f"[{datetime.now().strftime('%I:%M %p')}] ❌ Stock '{deleted.stock_name}' deleted.")
                    deleted.delete()
                
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
                messages.info(request,  f"[{datetime.now().strftime('%I:%M %p')}] ✏️ SIP '{sip.sip_name}' updated successfully.")
                return redirect('investment-Final')

        # --- SIP: Delete ---
        elif 'delete_sip' in request.POST:
            sip_id = request.POST.get("sip_id")
            deleted = AddSIP.objects.filter(id=sip_id, user=request.user).first()
            if deleted:
                messages.error(request,  f"[{datetime.now().strftime('%I:%M %p')}] ❌ SIP '{deleted.sip_name}' deleted.")
                deleted.delete()
            return redirect('investment-Final')

    # Fetch user data
    stocks = AddStock.objects.filter(user=request.user)
    sips = AddSIP.objects.filter(user=request.user)

    # --- SIP Due Alerts ---
    from datetime import date, datetime
    today = date.today()
    for sip in sips:
        days_left = (sip.due_date - today).days
        time_str = datetime.now().strftime("%I:%M %p")
        if days_left == 0:
            notifications.append( f"[{time_str}] ⚠️ SIP '{sip.sip_name}' is due today!")
        elif days_left == 1:
            notifications.append( f"[{time_str}] ⚠️ SIP '{sip.sip_name}' is due tomorrow.")
        elif days_left < 0:
            notifications.append( f"[{time_str}] ❌ SIP '{sip.sip_name}' is overdue ({abs(days_left)} days).")



    if request.method == 'POST':
    # --- CLEAR ALL ---
        if 'clear_all' in request.POST:
        # Clear Django messages
            list(messages.get_messages(request))  # iterates & clears storage
        # Clear SIP alerts (just ignore them in context)
            notifications = []
            return redirect('investment-Final')


    # Bind querysets
    update_stock_form.fields['stock'].queryset = stocks
    update_sip_form.fields['sip'].queryset = sips



    # Count activity messages
    storage = get_messages(request)
    message_count = len(list(storage))   # consuming messages, so we need to re-add them
    storage.used = False  # mark as unused so Django still shows them

    # Total count = alerts + activities
    notification_count = len(notifications) + message_count



    return render(request, 'investment-Final.html', {
        'stock_form': stock_form,
        'update_stock_form': update_stock_form,
        'sip_form': sip_form,
        'update_sip_form': update_sip_form,
        'stocks': stocks,
        'sips': sips,
        'notifications': notifications,   # send to template
        'notification_count': notification_count
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
                tenant = form.save()
                messages.success(request, f"✅ New tenant '{tenant.name}' added (Adhar No {tenant.aadhar_number})")
                return redirect('owner-rental')

        # Handle delete tenant
        elif 'delete_tenant' in request.POST:
            tenant_id = request.POST.get('tenant_id')
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.name
            tenant_adhar = tenant.aadhar_number
            tenant.delete()
            messages.error(request, f"❌ Tenant '{tenant_name}' removed (Adhar No {tenant_adhar})")            
            return redirect('owner-rental')

    tenants = Tenant.objects.all()  # fetch all tenants

    # Gather other alerts (Issues, Vacates, etc.)
    alerts = []
    for tenant in tenants:
        for issue in RaiseIssue.objects.filter(tenant=tenant):
            alerts.append({
                "type": "Issue",
                "message": f"Issue Raised: {issue.title} ({issue.status})",
                "date": issue.created_at.strftime("%d-%b-%Y"),
            })
        for notice in VacateNotice.objects.filter(tenant=tenant):
            alerts.append({
                "type": "Vacate Notice",
                "message": f"Vacate Notice: {notice.name} ({notice.status})",
                "date": notice.date.strftime("%d-%b-%Y"),
            })

    notification_count = len(alerts) + messages.get_messages(request).__len__()
    
    return render(request, 'owner-rental.html', {
        'form': form,
        'tenants': tenants,
        'alerts': alerts,   # ✅ send alerts to template
        'notification_count': notification_count,  # ✅ badge count
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
        .values("id", "title", "created_at", "status", "details", "category", "urgency", "estimated_resolution_date", "owner_status")
    )

    # ================== Vacate Notices ==================
    vacate_notices = list(
        VacateNotice.objects.filter(tenant=rental_details)
        .values("id", "reason", "date", "flat_no", "name", "status", "rejection_reason")   # ✅ added correct fields
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


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def update_vacate_notice(request, notice_id):
    if request.method == "POST":
        data = json.loads(request.body)
        status = data.get("status")
        reason = data.get("rejection_reason", "")

        try:
            notice = VacateNotice.objects.get(id=notice_id)
            notice.status = status
            if status == "Rejected":
                notice.rejection_reason = reason
            notice.save()
            return JsonResponse({"success": True})
        except VacateNotice.DoesNotExist:
            return JsonResponse({"success": False, "error": "Notice not found"})


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # (or use proper CSRF in AJAX later)
@require_POST
def resolve_issue(request, issue_id):
    issue = get_object_or_404(RaiseIssue, id=issue_id)
    issue.status = "Resolved"
    issue.owner_status = "Resolved by Owner"
    issue.save()
    return JsonResponse({"success": True, "message": "Issue resolved successfully"})


#Expenses_View
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now

def expenses_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ✅ Delete Expense
        if action == "delete":
            expense_id = request.POST.get("expense_id")
            expense = get_object_or_404(Transaction, id=expense_id, user=request.user)
            expense.delete()
            messages.success(request, "Expense deleted successfully!")
            return redirect("expenses")

        # ✅ Update Expense
        elif action == "update":
            expense_id = request.POST.get("expense_id")
            expense = get_object_or_404(Transaction, id=expense_id, user=request.user)
            expense.amount = Decimal(request.POST.get("amount") or "0.00")
            expense.category = request.POST.get("category") or expense.category
            expense.date = request.POST.get("date") or expense.date
            expense.note = request.POST.get("note", "")
            expense.save()
            messages.success(request, "Expense updated successfully!")
            return redirect("expenses")

        # ✅ Add Expense
        elif action == "add":
            form = TransactionForm(request.POST)
            if form.is_valid():
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                messages.success(request, "Expense added successfully!")
                return redirect("expenses")

        # ✅ Set Budget
        elif action == "set_budget":
            category = request.POST.get("category")
            amount = request.POST.get("budget_amount")
            if category and amount:
                ExpenseBudget.objects.update_or_create(
                    user=request.user,
                    category=category,
                    month=now().month,
                    year=now().year,
                    defaults={"amount": Decimal(amount)}
                )
                messages.success(request, f"Budget set for {category}")
            return redirect("expenses")

    else:
        form = TransactionForm()

    # --- Transactions ---
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    current_month_transactions = transactions.filter(date__month=now().month, date__year=now().year)
    last_month_transactions = transactions.filter(date__month=now().month - 1, date__year=now().year)

    categories = Transaction.objects.values_list("category", flat=True).distinct()

    current_month_total = sum(tx.amount for tx in current_month_transactions if tx.transaction_type == "Expense")
    overall_total = sum(tx.amount for tx in transactions if tx.transaction_type == "Expense")
    last_month_total = sum(tx.amount for tx in last_month_transactions if tx.transaction_type == "Expense")

    # --- Budgets ---
    budgets = ExpenseBudget.objects.filter(user=request.user, month=now().month, year=now().year)
    budget_status = {}
    alerts = []

    for b in budgets:
        spent = current_month_transactions.filter(category=b.category, transaction_type="Expense").aggregate(
            total=Sum("amount"))["total"] or Decimal("0")
        budget_status[b.category] = {"set": b.amount, "spent": spent, "remaining": b.amount - spent}

        if spent > b.amount:
            alerts.append(f"🚨 You exceeded your {b.category} budget! (₹{spent}/₹{b.amount})")

    # --- Expiry Notice ---
    existing_budgets = ExpenseBudget.objects.filter(user=request.user).order_by("-created_at").first()
    budget_expired = False
    if existing_budgets and (existing_budgets.month != now().month or existing_budgets.year != now().year):
        budget_expired = True
        alerts.append("⚠️ Your last month's budgets expired. Please set new budgets.")

    # --- Tips Section ---
    tips = []
    total_months = transactions.dates("date", "month").count()
    avg_monthly_spend = (overall_total / total_months) if total_months else Decimal("0")

    # Compare with average monthly spend
    if avg_monthly_spend > 0:
        if current_month_total > avg_monthly_spend * Decimal("1.2"):
            tips.append("💡 This month's total spending is 20% higher than your average month. Track recurring costs.")
        elif current_month_total < avg_monthly_spend * Decimal("0.8"):
            tips.append("✅ Great! This month's spending is below your average. Keep saving!")

    # Compare with last month
    if last_month_total:
        if current_month_total > last_month_total:
            tips.append("📈 You're spending more than last month. Review lifestyle or impulse buys.")
        else:
            tips.append("📉 Spending is lower than last month. Good progress!")

    # Category/Sub-category wise budget checks
    for category, data in budget_status.items():
        spent, set_budget = data["spent"], data["set"]
        if set_budget > 0:
            utilization = spent / set_budget
            if utilization >= Decimal("1"):
                tips.append(f"⚠️ You exceeded your {category} budget this month.")
            elif utilization >= Decimal("0.9"):
                tips.append(f"🔔 {category} spending is at 90% of its budget this month.")
            elif utilization >= Decimal("0.75"):
                tips.append(f"📊 {category} expenses are at 75% of its budget already.")

    # Specific Expense tips
    if "Food" in budget_status and budget_status["Food"]["spent"] > budget_status["Food"]["set"] * Decimal("0.8"):
        tips.append("🍔 Food expenses are nearing your budget. Try home cooking or meal prepping this month.")
    if "Travel" in budget_status and budget_status["Travel"]["spent"] > budget_status["Travel"]["set"] * Decimal("0.8"):
        tips.append("✈️ Travel costs are high this month. Consider public transport, pooling, or off-peak travel.")
    if "Rent" in budget_status and budget_status["Rent"]["spent"] > 0:
        tips.append("🏠 Rent is fixed. Balance it by reducing discretionary spends like entertainment.")
    if "Entertainment" in budget_status and budget_status["Entertainment"]["spent"] > budget_status["Entertainment"]["set"] * Decimal("0.7"):
        tips.append("🎬 Entertainment spending is high. Consider free/low-cost activities this month.")

    # Income tips
    if "Salary" in budget_status and budget_status["Salary"]["spent"] > 0:
        tips.append("💼 Salary credited. Move part of it to savings/investments early.")
    if "Bonus" in budget_status and budget_status["Bonus"]["spent"] > 0:
        tips.append("🎉 You received a bonus. Allocate some to investments, not just spending.")
    if "Investment" in budget_status and budget_status["Investment"]["spent"] > 0:
        tips.append("📈 Investment income added. Reinvest part of it for compounding growth.")

    # Transfer tips
    if "Bank transfer" in budget_status and budget_status["Bank transfer"]["spent"] > 0:
        tips.append("🏦 You made bank transfers. Ensure they're aligned with savings/investment goals.")
    if "Wallet" in budget_status and budget_status["Wallet"]["spent"] > 0:
        tips.append("📱 You used wallet transfers. Check if cashback offers are available.")

    # --- Context ---
    percentage_month = (current_month_total / overall_total * Decimal("100")) if overall_total else Decimal("0")
    context = {
        "transactions": transactions,
        "form": form,
        "categories": categories,
        "current_month_total": current_month_total,
        "overall_total": overall_total,
        "percentage_month": percentage_month,
        "budgets": budget_status,
        "budget_expired": budget_expired,
        "alerts": alerts,
        "tips": tips,
    }
    return render(request, "Expenses.html", context)



#Saving Goal code 
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import SavingsGoal
from .forms import SavingsGoalForm
from decimal import Decimal

@login_required
def saving_goal_dashboard(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    form = SavingsGoalForm()
    return render(request, "goals_dashboard.html", {"goals": goals, "form": form})



@login_required
def goal_handler(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # ✅ Add new goal
        if action == "add_goal":
            form = SavingsGoalForm(request.POST)
            if form.is_valid():
                goal = form.save(commit=False)
                goal.user = request.user
                goal.save()
                return JsonResponse({
                    "success": True,
                    "message": "Goal added successfully 🎉",
                    "goal": {
                        "id": goal.id,
                        "goal_name": goal.goal_name,
                        "target_amount": str(goal.target_amount),
                        "saved_amount": str(goal.saved_amount),
                        "progress": goal.progress,
                        "status": goal.status,
                    }
                })
            return JsonResponse({"success": False, "message": "Invalid goal data ❌"})

        # ✅ Add money to existing goal
        elif action == "add_money":
            goal_id = request.POST.get("goal_id")
            amount = request.POST.get("amount")
            try:
                goal = SavingsGoal.objects.get(id=goal_id, user=request.user)
                goal.saved_amount += Decimal(amount)  # 🔥 FIXED decimal issue
                goal.save()
                return JsonResponse({
                    "success": True,
                    "message": f"₹{amount} added to {goal.goal_name} 🎉",
                    "goal": {
                        "id": goal.id,
                        "saved_amount": str(goal.saved_amount),
                        "progress": goal.progress,
                        "status": goal.status,
                    }
                })
            except SavingsGoal.DoesNotExist:
                return JsonResponse({"success": False, "message": "Goal not found ❌"})

        # ✅ Delete goal
        elif action == "delete_goal":
            goal_id = request.POST.get("goal_id")
            try:
                goal = SavingsGoal.objects.get(id=goal_id, user=request.user)
                goal.delete()
                return JsonResponse({"success": True, "message": "Goal deleted ❌"})
            except SavingsGoal.DoesNotExist:
                return JsonResponse({"success": False, "message": "Goal not found ❌"})

    return JsonResponse({"success": False, "message": "Invalid request ❌"})



# Center Dashboard code below start

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from datetime import date, timedelta
import calendar
from .models import AddStock, AddSIP, Transaction, SavingsGoal, Tenant
from .forms import AddStockForm, UpdateStockForm, AddSIPForm, UpdateSIPForm, TransactionForm, SavingsGoalForm

# ---------------- DASHBOARD VIEW -----------------
@login_required
def center_dashboard_view(request):
    # Just render template; all data loaded via AJAX
    return render(request, "dashboard.html")

# ---------------- DASHBOARD DATA API -----------------
@login_required
def dashboard_data_api(request):
    user = request.user
    today = date.today()
    first_day_this_month = today.replace(day=1)
    last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_month.replace(day=1)

    # ---------------- Stocks -----------------
    stocks = AddStock.objects.filter(user=user)
    stock_labels = [s.stock_name for s in stocks]
    stock_values = [float(s.quantity * s.buy_price) for s in stocks]
    total_stock_value = sum(stock_values)
    total_stock_last_month = total_stock_value  # replace if historical data available
    stock_change_percent = round((total_stock_value - total_stock_last_month) / total_stock_last_month * 100, 2) if total_stock_last_month else 0

    # ---------------- SIPs -----------------
    sips = AddSIP.objects.filter(user=user)
    sip_labels = [s.sip_name for s in sips]
    sip_values = [float(s.monthly_amount) for s in sips]
    total_sip_value = sum(sip_values)
    total_sip_last_month = total_sip_value  # replace if historical data available
    sip_change_percent = round((total_sip_value - total_sip_last_month) / total_sip_last_month * 100, 2) if total_sip_last_month else 0

    # ---------------- Expenses -----------------
    transactions = Transaction.objects.filter(user=user, transaction_type="Expense")
    categories = list(transactions.values_list("category", flat=True).distinct())
    category_sums = [
        float(transactions.filter(category=cat).aggregate(total=Sum("amount"))["total"] or 0)
        for cat in categories
    ]
    total_expense = sum(category_sums)
    total_expense_last_month = float(
        transactions.filter(date__month=last_month.month, date__year=last_month.year)
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    expense_change_percent = round((total_expense - total_expense_last_month) / total_expense_last_month * 100, 2) if total_expense_last_month else 0

    # Expense trend
    expense_trend_labels = []
    expense_trend_values = []
    for month_index in range(1, 13):
        monthly_sum = float(
            transactions.filter(date__month=month_index, date__year=today.year)
            .aggregate(total=Sum("amount"))["total"] or 0
        )
        expense_trend_labels.append(calendar.month_abbr[month_index])
        expense_trend_values.append(monthly_sum)

    # ---------------- Savings Goals -----------------
    goals = SavingsGoal.objects.filter(user=user)
    goal_labels = [g.goal_name for g in goals]
    goal_progress = [float(g.saved_amount / g.target_amount * 100 if g.target_amount else 0) for g in goals]

    # ---------------- Tenants -----------------
    tenant_count = Tenant.objects.count()

    return JsonResponse({
        "stock_labels": stock_labels,
        "stock_values": stock_values,
        "total_stock_value": total_stock_value,
        "stock_change_percent": stock_change_percent,
        "sip_labels": sip_labels,
        "sip_values": sip_values,
        "total_sip_value": total_sip_value,
        "sip_change_percent": sip_change_percent,
        "categories": categories,
        "category_sums": category_sums,
        "total_expense": total_expense,
        "expense_change_percent": expense_change_percent,
        "expense_trend_labels": expense_trend_labels,
        "expense_trend_values": expense_trend_values,
        "goal_labels": goal_labels,
        "goal_progress": goal_progress,
        "tenant_count": tenant_count,
    })

# ---------------- AJAX CRUD for Stocks -----------------
@login_required
def add_stock_ajax(request):
    if request.method == "POST":
        form = AddStockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            return JsonResponse({"success": True, "message": f"Stock '{stock.stock_name}' added!"})
    return JsonResponse({"success": False, "message": "Invalid data"})

@login_required
def update_stock_ajax(request):
    if request.method == "POST":
        stock_id = request.POST.get("stock_id")
        stock = get_object_or_404(AddStock, id=stock_id, user=request.user)
        new_qty = Decimal(request.POST.get("new_quantity", 0))
        new_buy_price = Decimal(request.POST.get("new_buy_price", 0))
        total_existing_value = stock.quantity * stock.buy_price
        total_new_value = new_qty * new_buy_price
        new_total_qty = stock.quantity + new_qty
        stock.buy_price = (total_existing_value + total_new_value) / new_total_qty if new_total_qty else stock.buy_price
        stock.quantity = new_total_qty
        stock.save()
        return JsonResponse({"success": True, "message": f"Stock '{stock.stock_name}' updated!"})

@login_required
def delete_stock_ajax(request):
    if request.method == "POST":
        stock_id = request.POST.get("stock_id")
        stock = get_object_or_404(AddStock, id=stock_id, user=request.user)
        stock_name = stock.stock_name
        stock.delete()
        return JsonResponse({"success": True, "message": f"Stock '{stock_name}' deleted!"})

# ---------------- AJAX CRUD for SIPs -----------------
@login_required
def add_sip_ajax(request):
    if request.method == "POST":
        form = AddSIPForm(request.POST)
        if form.is_valid():
            sip = form.save(commit=False)
            sip.user = request.user
            sip.save()
            return JsonResponse({"success": True, "message": f"SIP '{sip.sip_name}' added!"})
    return JsonResponse({"success": False, "message": "Invalid data"})

@login_required
def update_sip_ajax(request):
    if request.method == "POST":
        sip_id = request.POST.get("sip_id")
        sip = get_object_or_404(AddSIP, id=sip_id, user=request.user)
        sip.monthly_amount = Decimal(request.POST.get("monthly_amount", sip.monthly_amount))
        sip.due_date = request.POST.get("due_date", sip.due_date)
        sip.save()
        return JsonResponse({"success": True, "message": f"SIP '{sip.sip_name}' updated!"})

@login_required
def delete_sip_ajax(request):
    if request.method == "POST":
        sip_id = request.POST.get("sip_id")
        sip = get_object_or_404(AddSIP, id=sip_id, user=request.user)
        sip_name = sip.sip_name
        sip.delete()
        return JsonResponse({"success": True, "message": f"SIP '{sip_name}' deleted!"})

# ---------------- AJAX CRUD for Expenses -----------------
@login_required
def add_expense_ajax(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return JsonResponse({"success": True, "message": "Expense added!"})
    return JsonResponse({"success": False, "message": "Invalid data"})

@login_required
def update_expense_ajax(request):
    if request.method == "POST":
        expense_id = request.POST.get("expense_id")
        expense = get_object_or_404(Transaction, id=expense_id, user=request.user)
        expense.amount = Decimal(request.POST.get("amount", expense.amount))
        expense.category = request.POST.get("category", expense.category)
        expense.date = request.POST.get("date", expense.date)
        expense.note = request.POST.get("note", expense.note)
        expense.save()
        return JsonResponse({"success": True, "message": "Expense updated!"})

@login_required
def delete_expense_ajax(request):
    if request.method == "POST":
        expense_id = request.POST.get("expense_id")
        expense = get_object_or_404(Transaction, id=expense_id, user=request.user)
        expense.delete()
        return JsonResponse({"success": True, "message": "Expense deleted!"})
