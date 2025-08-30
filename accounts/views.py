from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
from .models import User, Account, Category, Transaction
from .forms import SignUpForm, TransactionForm, AccountForm, CategoryForm

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_default_categories(user)
            Account.objects.create(
                name="Main Account",
                type="checking",
                balance=Decimal('0.00'),
                user=user
            )
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user, is_active=True)
    total_balance = accounts.aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')
    
    recent_transactions = Transaction.objects.filter(user=request.user)[:5]
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_income = Transaction.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year,
        category__type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        date__month=current_month,
        date__year=current_year,
        category__type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'total_balance': total_balance,
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'net_income': monthly_income - monthly_expenses,
        'total_accounts': accounts.count(),
        'total_categories': categories.count(),
        'total_transactions': Transaction.objects.filter(user=request.user).count(),
    }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def transactions_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    category_filter = request.GET.get('category')
    if category_filter:
        transactions = transactions.filter(category_id=category_filter)
    
    account_filter = request.GET.get('account')
    if account_filter:
        transactions = transactions.filter(account_id=account_filter)
    
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) | 
            Q(notes__icontains=search)
        )
    
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'categories': Category.objects.filter(user=request.user),
        'accounts': Account.objects.filter(user=request.user, is_active=True),
        'current_category': category_filter,
        'current_account': account_filter,
        'search_term': search,
    }
    
    return render(request, 'accounts/transactions_list.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transactions_list')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'accounts/add_transaction.html', {'form': form})

@login_required
def accounts_list(request):
    accounts = Account.objects.filter(user=request.user)
    return render(request, 'accounts/accounts_list.html', {'accounts': accounts})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, 'Account added successfully!')
            return redirect('accounts_list')
    else:
        form = AccountForm()
    
    return render(request, 'accounts/add_account.html', {'form': form})

@login_required
def categories_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'accounts/categories_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('categories_list')
    else:
        form = CategoryForm()
    
    return render(request, 'accounts/add_category.html', {'form': form})

def create_default_categories(user):
    default_categories = [
        {'name': 'Salary', 'type': 'income', 'icon': '💰', 'color': '#28a745'},
        {'name': 'Freelance', 'type': 'income', 'icon': '💻', 'color': '#17a2b8'},
        {'name': 'Food', 'type': 'expense', 'icon': '🍽️', 'color': '#fd7e14'},
        {'name': 'Transport', 'type': 'expense', 'icon': '🚗', 'color': '#6610f2'},
        {'name': 'Entertainment', 'type': 'expense', 'icon': '🎬', 'color': '#e83e8c'},
        {'name': 'Utilities', 'type': 'expense', 'icon': '⚡', 'color': '#dc3545'},
        {'name': 'Healthcare', 'type': 'expense', 'icon': '🏥', 'color': '#20c997'},
        {'name': 'Shopping', 'type': 'expense', 'icon': '🛍️', 'color': '#ffc107'},
    ]
    
    for cat_data in default_categories:
        Category.objects.create(user=user, **cat_data)