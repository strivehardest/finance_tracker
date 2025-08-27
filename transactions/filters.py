import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    # Exact date or range filtering: ?date_after=2025-01-01&date_before=2025-02-01
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')

    # Numeric ranges for amount: ?amount_min=50&amount_max=500
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = [
            'account',          # by id
            'category',         # by id
            'type',             # income/expense
            'date',             # exact date match
            # virtual fields above (date_after/date_before, amount_min/amount_max) are handled by FilterSet
        ]
