from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import TransactionForm
from .models import Transaction
from django.utils import timezone
from collections import defaultdict
import json


# ✅ User registration (signup) view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after registration
    else:
        form = UserCreationForm()
    return render(request, 'transactions/register.html', {'form': form})


# ✅ Home/dashboard view
@login_required
def home(request):
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Filter this user's transactions by selected month and year
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).order_by('-date')

    # Calculate totals
    income_total = sum(t.amount for t in transactions if t.type == 'income')
    expense_total = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income_total - expense_total

    # Group expenses by category for pie chart
    category_totals = defaultdict(float)
    for tx in transactions:
        if tx.type == 'expense' and tx.category:
            category_totals[str(tx.category)] += float(tx.amount)

    chart_labels = list(category_totals.keys())
    chart_data = list(category_totals.values())

    context = {
        'transactions': transactions,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'month': month,
        'year': year,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'transactions/home.html', context)


# ✅ Add Transaction View (Missing Earlier)
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('home')
    else:
        form = TransactionForm()

    return render(request, 'transactions/add_transaction.html', {'form': form})
