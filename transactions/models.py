from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
from categories.models import Category

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.type} - {self.amount}"

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def transactions_page(request):
    return render(request, "transactions.html")

@login_required
def categories_page(request):
    return render(request, "categories.html")
