from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    CURRENCY_CHOICES = (
        ('GHS', 'Ghana Cedis (₵)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('NGN', 'Nigerian Naira (₦)'),
    )
    
    COUNTRY_CODES = (
        ('+1', 'United States (+1)'),
        ('+44', 'United Kingdom (+44)'),
        ('+33', 'France (+33)'),
        ('+49', 'Germany (+49)'),
        ('+234', 'Nigeria (+234)'),
        ('+233', 'Ghana (+233)'),
        ('+27', 'South Africa (+27)'),
        ('+254', 'Kenya (+254)'),
        ('+256', 'Uganda (+256)'),
        ('+39', 'Italy (+39)'),
        ('+34', 'Spain (+34)'),
        ('+31', 'Netherlands (+31)'),
        ('+32', 'Belgium (+32)'),
        ('+41', 'Switzerland (+41)'),
        ('+43', 'Austria (+43)'),
        ('+45', 'Denmark (+45)'),
        ('+46', 'Sweden (+46)'),
        ('+47', 'Norway (+47)'),
        ('+358', 'Finland (+358)'),
        ('+30', 'Greece (+30)'),
        ('+48', 'Poland (+48)'),
        ('+420', 'Czech Republic (+420)'),
        ('+36', 'Hungary (+36)'),
        ('+40', 'Romania (+40)'),
        ('+359', 'Bulgaria (+359)'),
        ('+385', 'Croatia (+385)'),
        ('+381', 'Serbia (+381)'),
        ('+355', 'Albania (+355)'),
        ('+386', 'Slovenia (+386)'),
        ('+389', 'North Macedonia (+389)'),
        ('+61', 'Australia (+61)'),
        ('+64', 'New Zealand (+64)'),
        ('+65', 'Singapore (+65)'),
        ('+60', 'Malaysia (+60)'),
        ('+62', 'Indonesia (+62)'),
        ('+63', 'Philippines (+63)'),
        ('+66', 'Thailand (+66)'),
        ('+84', 'Vietnam (+84)'),
        ('+81', 'Japan (+81)'),
        ('+82', 'South Korea (+82)'),
        ('+86', 'China (+86)'),
        ('+91', 'India (+91)'),
        ('+92', 'Pakistan (+92)'),
        ('+880', 'Bangladesh (+880)'),
        ('+966', 'Saudi Arabia (+966)'),
        ('+971', 'United Arab Emirates (+971)'),
        ('+20', 'Egypt (+20)'),
        ('+212', 'Morocco (+212)'),
        ('+55', 'Brazil (+55)'),
        ('+56', 'Chile (+56)'),
        ('+57', 'Colombia (+57)'),
        ('+51', 'Peru (+51)'),
        ('+54', 'Argentina (+54)'),
        ('+598', 'Uruguay (+598)'),
    )
    
    preferred_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='GHS'
    )
    
    # Profile fields
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Upload a clear profile picture (PNG or JPG, max 5MB)'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Your date of birth'
    )
    country_code = models.CharField(
        max_length=5,
        choices=COUNTRY_CODES,
        default='+233',
        help_text='Country code for phone number'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text='Phone number without country code'
    )
    occupation = models.CharField(
        max_length=100,
        blank=True,
        help_text='Your occupation or job title'
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text='Short bio about yourself (max 500 characters)'
    )
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    CATEGORY_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='💰')
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'user')

    def __str__(self):
        return f"{self.name} ({self.type})"

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit', 'Credit Card'),
        ('cash', 'Cash'),
        ('investment', 'Investment'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₵{self.balance}"

    def update_balance(self):
        from django.db.models import Sum
        
        income = Transaction.objects.filter(
            account=self,
            category__type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        expenses = Transaction.objects.filter(
            account=self,
            category__type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        self.balance = income - expenses
        self.save()

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        sign = '+' if self.category.type == 'income' else '-'
        return f"{sign}₵{self.amount} - {self.description}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.account.update_balance()
