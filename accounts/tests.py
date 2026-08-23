from datetime import date, timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from accounts.forms import ProfileForm
from accounts.models import Account, Category, Transaction, User
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
