from datetime import date, timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from decimal import Decimal

from accounts.forms import ProfileForm, TransferForm
from accounts.models import Account, Category, Transaction, User, perform_transfer
from accounts.utils import (
    build_excel_report,
    build_pdf_report,
    category_icon_html,
    normalize_icon,
    pagination_pages,
    process_profile_image,
    resolve_period,
)

FILESYSTEM_STORAGE = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


def _png_file(name='photo.png', size=(80, 40), color='navy'):
    buffer = BytesIO()
    Image.new('RGB', size, color).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class UtilsTests(TestCase):
    def test_normalize_icon_maps_emoji_and_font_awesome(self):
        self.assertEqual(normalize_icon('fa-utensils'), 'fa-utensils')
        self.assertEqual(normalize_icon('🍔'), 'fa-utensils')
        self.assertEqual(normalize_icon(''), 'fa-tag')
        self.assertIn('fa-utensils', category_icon_html('🍔', '#ea580c'))

    def test_period_and_pagination_helpers(self):
        start, end, label = resolve_period('this_month')
        self.assertEqual(label, 'This month')
        self.assertEqual(start.day, 1)
        self.assertLessEqual(end, date.today())

        class FakePage:
            number = 5

            class paginator:
                num_pages = 12

        pages = pagination_pages(FakePage())
        self.assertEqual(pages[0], 1)
        self.assertIsNone(pages[1])
        self.assertIn(5, pages)
        self.assertEqual(pages[-1], 12)

    def test_profile_image_is_squared_jpeg(self):
        processed = process_profile_image(_png_file())
        image = Image.open(processed)
        self.assertEqual(image.size, (512, 512))
        self.assertEqual(image.format, 'JPEG')


class ProfilePhotoTests(TestCase):
    def setUp(self):
        self.media = TemporaryDirectory()
        self.override = override_settings(
            MEDIA_ROOT=self.media.name,
            DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
            STORAGES=FILESYSTEM_STORAGE,
        )
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(self.media.cleanup)
        self.user = User.objects.create_user(
            username='waliu',
            email='waliu@example.com',
            password='secret12345',
            first_name='Waliu',
        )

    def test_saving_profile_without_new_photo_keeps_existing_file(self):
        self.user.profile_picture = process_profile_image(_png_file('avatar.png'))
        self.user.save()
        name = self.user.profile_picture.name
        form = ProfileForm(
            data={
                'first_name': 'Waliu',
                'last_name': 'A',
                'email': self.user.email,
                'preferred_currency': 'GHS',
                'country_code': '+233',
            },
            files={},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(saved.profile_picture.name, name)

    def test_new_upload_is_accepted(self):
        form = ProfileForm(
            data={
                'first_name': 'Waliu',
                'last_name': 'A',
                'email': self.user.email,
                'preferred_currency': 'GHS',
                'country_code': '+233',
            },
            files={'profile_picture': _png_file('new.png')},
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertTrue(saved.profile_picture.name.endswith('.jpg'))


class ExportAndTransactionsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='exporter',
            email='export@example.com',
            password='secret12345',
        )
        self.account = Account.objects.create(user=self.user, name='Cash', type='cash', balance=100)
        self.category = Category.objects.create(
            user=self.user, name='Food', type='expense', icon='🍔', color='#ea580c'
        )
        today = date.today()
        for i in range(15):
            Transaction.objects.create(
                user=self.user,
                account=self.account,
                category=self.category,
                amount=10 + i,
                description=f'Lunch {i}',
                date=today - timedelta(days=i),
            )
        self.client.login(username='exporter', password='secret12345')

    def test_excel_and_pdf_are_real_files(self):
        qs = Transaction.objects.filter(user=self.user)
        excel = build_excel_report(self.user, qs, 'This month')
        pdf = build_pdf_report(self.user, qs, 'This month')
        self.assertTrue(excel.startswith(b'PK'))
        self.assertTrue(pdf.startswith(b'%PDF'))

    def test_export_page_period_and_download(self):
        page = self.client.get(reverse('export_transactions'), {'period': 'this_month'})
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Send by email')
        self.assertContains(page, 'This month')
        self.assertContains(page, 'will be included')
        self.assertNotContains(page, 'card h-100')

        download = self.client.post(reverse('export_transactions'), {
            'period': 'this_month',
            'format': 'excel',
            'action': 'download',
        })
        self.assertEqual(download.status_code, 200)
        self.assertIn('spreadsheetml', download['Content-Type'])

        pdf = self.client.post(reverse('export_transactions'), {
            'period': 'last_30',
            'format': 'pdf',
            'action': 'download',
        })
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.content.startswith(b'%PDF'))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_export_email_attaches_file(self):
        from django.core import mail
        response = self.client.post(reverse('export_transactions'), {
            'period': 'this_month',
            'format': 'pdf',
            'action': 'email',
            'email': 'export@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)

    def test_transactions_next_keeps_filters(self):
        response = self.client.get(reverse('transactions_list'), {'search': 'Lunch', 'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Next')
        self.assertContains(response, 'search=Lunch')
        page_two = self.client.get(reverse('transactions_list'), {'search': 'Lunch', 'page': 2})
        self.assertEqual(page_two.status_code, 200)
        self.assertContains(page_two, 'Previous')
        self.assertContains(page_two, 'fas fa-utensils')
        self.assertContains(page_two, 'Page 2 of')
        self.assertNotContains(page_two, 'tx-pager-pages')

    def test_dashboard_uses_sidebar_shell(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'app-sidebar')
        self.assertContains(response, 'sidebar-link')
        self.assertContains(response, 'display: flex !important')
        self.assertNotContains(response, 'nav flex-column')
        self.assertContains(response, 'Log out')
        self.assertContains(response, 'site-footer')
        self.assertNotContains(response, 'Overview')
        self.assertContains(response, 'sidebar-logout')


class TransferTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='mover',
            email='mover@example.com',
            password='secret12345',
        )
        self.cash = Account.objects.create(
            user=self.user, name='Cash', type='cash', balance=Decimal('200.00')
        )
        self.bank = Account.objects.create(
            user=self.user, name='Bank', type='checking', balance=Decimal('500.00')
        )
        self.food = Category.objects.create(
            user=self.user, name='Food', type='expense', icon='fa-utensils', color='#ea580c'
        )
        Transaction.objects.create(
            user=self.user,
            account=self.cash,
            category=self.food,
            amount=Decimal('20.00'),
            description='Lunch',
            date=date.today(),
        )
        self.client.login(username='mover', password='secret12345')

    def test_accounts_page_offers_transfer(self):
        response = self.client.get(reverse('accounts_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Transfer')
        self.assertContains(response, reverse('transfer'))

    def test_same_account_is_rejected(self):
        form = TransferForm(
            data={
                'from_account': self.cash.pk,
                'to_account': self.cash.pk,
                'amount': '10.00',
                'date': date.today().isoformat(),
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())

    def test_one_account_cannot_open_transfer(self):
        self.bank.delete()
        response = self.client.get(reverse('transfer'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts_list'))

    def test_transfer_moves_money_without_changing_income_or_expense(self):
        response = self.client.post(reverse('transfer'), {
            'from_account': self.cash.pk,
            'to_account': self.bank.pk,
            'amount': '50.00',
            'date': date.today().isoformat(),
            'notes': 'Move cash',
        })
        self.assertEqual(response.status_code, 302)
        self.cash.refresh_from_db()
        self.bank.refresh_from_db()
        self.assertEqual(self.cash.balance, Decimal('130.00'))
        self.assertEqual(self.bank.balance, Decimal('550.00'))
        self.assertEqual(Transaction.objects.filter(user=self.user, is_transfer=True).count(), 2)

        dashboard = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.context['monthly_expenses_converted'], 20.0)
        self.assertEqual(dashboard.context['monthly_income_converted'], 0.0)

    def test_deleting_a_transfer_restores_both_accounts(self):
        outgoing, _incoming = perform_transfer(
            self.user, self.cash, self.bank, Decimal('40.00'), date.today(), 'Undo me'
        )
        self.cash.refresh_from_db()
        self.bank.refresh_from_db()
        self.assertEqual(self.cash.balance, Decimal('140.00'))
        self.assertEqual(self.bank.balance, Decimal('540.00'))

        response = self.client.post(reverse('delete_transaction', args=[outgoing.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Transaction.objects.filter(user=self.user, is_transfer=True).count(), 0)
        self.cash.refresh_from_db()
        self.bank.refresh_from_db()
        self.assertEqual(self.cash.balance, Decimal('180.00'))
        self.assertEqual(self.bank.balance, Decimal('500.00'))


class BudgetPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='budgeter',
            email='budget@example.com',
            password='secret12345',
        )
        self.food = Category.objects.create(
            user=self.user, name='Food', type='expense', icon='fa-utensils', color='#ea580c'
        )
        self.client.login(username='budgeter', password='secret12345')

    def test_budget_page_can_add_a_category_budget(self):
        page = self.client.get(reverse('budget'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Add budget')
        self.assertContains(page, 'Food')

        response = self.client.post(reverse('budget'), {
            'category': self.food.pk,
            'amount': '250.00',
        })
        self.assertEqual(response.status_code, 302)
        self.food.refresh_from_db()
        self.assertEqual(self.food.budget_limit, Decimal('250.00'))

        listed = self.client.get(reverse('budget'))
        self.assertContains(listed, '250.00')
        self.assertNotContains(listed, 'Add budget')


class SignupPageTests(TestCase):
    def test_signup_uses_wide_auth_card(self):
        response = Client().get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'auth-card-wide')
        self.assertContains(response, 'Create account')
        self.assertNotContains(response, 'col-lg-5')

