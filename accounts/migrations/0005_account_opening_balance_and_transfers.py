from decimal import Decimal

from django.db import migrations, models
from django.db.models import Sum


def backfill_opening_balances(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    Transaction = apps.get_model('accounts', 'Transaction')
    for account in Account.objects.all():
        income = Transaction.objects.filter(
            account=account, category__type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        expenses = Transaction.objects.filter(
            account=account, category__type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        Account.objects.filter(pk=account.pk).update(
            opening_balance=account.balance - (income - expenses)
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_category_budget_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='opening_balance',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_transfer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transfer_group',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_opening_balances, noop),
    ]
