from rest_framework import viewsets, permissions
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Transaction
from .serializers import TransactionSerializer
from .filters import TransactionFilter

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Only the current user's transactions
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    # 🔎 filtering / searching / ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = [
        'description',       # full-text search
        'category__name',    # search by category name
        'account__name',     # search by account name
    ]
    ordering_fields = ['date', 'amount', 'type']   # e.g. ?ordering=-date or ?ordering=amount
    ordering = ['-date']                           # default newest first

from django.shortcuts import render

def transactions_page(request):
    return render(request, "transactions/transactions.html")

def categories_page(request):
    return render(request, "transactions/categories.html")

# transactions/views.py
from rest_framework import generics
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated

class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def transactions_page(request):
    return render(request, "transactions/transactions.html")

@login_required
def categories_page(request):
    return render(request, "transactions/categories.html")
