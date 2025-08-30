Finance Tracker

A comprehensive personal finance management application built with Django. Track your income, expenses, accounts, and categories with a beautiful, responsive interface.


Features

Authentication System
- User registration and login
- Secure session management
- Custom user model with additional fields

Account Management
- Multiple account types (Checking, Savings, Credit Card, Cash, Investment)
- Real-time balance calculation
- Account activation/deactivation
- Visual account overview

Transaction Tracking
- Income and expense transactions
- Category-based organization
- Advanced search and filtering
- Pagination for large datasets
- Transaction notes and descriptions

Category System
- Custom categories with icons and colors
- Separate income and expense categories
- Visual category management
- Default categories for new users

Dashboard & Analytics
- Real-time financial overview
- Monthly income/expense summary
- Account balance tracking
- Recent transactions display
- Quick stats and insights

Modern UI/UX
- Responsive Bootstrap 5 design
- Mobile-friendly interface
- Interactive elements and animations
- Professional color scheme
- Icon-based navigation

Quick Start

Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

Installation

1. Clone or download the project
```bash
git clone <repository-url>
cd finance_tracker
```

2. Create virtual environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```


3. Database setup
```bash
# Create and apply migrations
python manage.py makemigrations accounts
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

6. Access the application
- Main Application: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/

 Usage Guide

Getting Started
1. *Sign Up:* Create a new account at the homepage
2. *Automatic Setup:* Default categories and a main account are created automatically
3. *Add Transactions:* Start tracking your income and expenses
4. *View Dashboard:* Monitor your financial overview

Managing Accounts
- Add multiple accounts (bank accounts, credit cards, cash, etc.)
- Set initial balances
- Balances update automatically based on transactions

 Organizing with Categories
- Create custom categories for income and expenses
- Use emojis and colors for visual organization
- Default categories include: Salary, Food, Transport, Entertainment, etc.

Transaction Management
- Add income and expense transactions
- Search and filter by category, account, or description
- View detailed transaction history
- Add notes for better record keeping

🛠️ Technical Details

Technology Stack
- *Backend:* Django 4.2.7
- *Frontend:* HTML5, CSS3, JavaScript
- *Styling:* Bootstrap 5.1.3
- *Icons:* Font Awesome 6.0
- **Database:** SQLite (development) / PostgreSQL (production recommended)

Project Structure
```
finance_tracker/
├── manage.py
├── requirements.txt
├── finance_tracker/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── templates/
│   ├── base.html
│   └── accounts/
│       ├── home.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html
|       ├── accounts_list.html
|       ├── add_account.html
|       ├── add_category.html
|       ├── add_transaction.html
|       ├── categories_list.html
│       └── transactions_list.html
└── static/
    └── css/
        └── custom.css
```

Models Overview

User Model
- Extends Django's AbstractUser
- Additional fields: phone, created_at

#Account Model
- Multiple account types support
- Automatic balance calculation
- User-specific accounts

Category Model
- Income/expense categorization
- Custom icons and colors
- User-specific categories

Transaction Model
- Links to accounts and categories
- Automatic balance updates
- Search and filter capabilities

#Configuration

Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=your-database-url
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Database Configuration
For production, update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance_tracker_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Deployment

Local Development
```bash
python manage.py runserver
```

Production Deployment

Using Heroku
1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn finance_tracker.wsgi
```

3. Add `gunicorn` to requirements.txt
4. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

 Default Features

Default Categories (Auto-created for new users)
*Income*:
- Salary
- Freelance

*Expenses:*
- Food
- Transport
- Entertainment
- Utilities
- Healthcare
- Shopping

Default Account
- Main Account (Checking type)
- GH₵0.00 initial balance

Security Features

- CSRF protection on all forms
- User authentication required for all financial data
- Secure password validation
- SQL injection protection via Django ORM
- XSS protection with Django templates

 *Future Enhancements*

Planned Features
-  Budget planning and tracking
-  Financial goals and progress tracking
-  Data visualization with charts and graphs
-  Export functionality (CSV, PDF)
-  Mobile app (React Native/Flutter)
-  Multi-currency support
-  Recurring transactions
-  Bank integration (Plaid API)
-  Financial reports and analytics

Enhancement Ideas
- Email notifications for sign up & budgets
- Receipt photo uploads
- Investment portfolio tracking
- Bill reminders
- Expense splitting with friends
- Data backup and restore


Support

Need help or have questions?
- Email support: ibrahimah2011@hotmail.com
- Check the Django documentation: https://docs.djangoproject.com/




