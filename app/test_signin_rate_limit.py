from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import LoginRateLimit, ProfileUser
from .views import SignInIPRateThrottle, SignInRateThrottle


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SignInRateLimitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='first@example.com', email='first@example.com', password='correct'
        )
        ProfileUser.objects.create(username=self.user, login_username='First')
        other = User.objects.create_user(username='second@example.com', password='correct')
        ProfileUser.objects.create(username=other, login_username='Second')
        for target, result in [
            ('verify_captcha', (True, None)),
            ('create_access_token', 'test-access'),
            ('create_refresh_token', 'test-refresh'),
        ]:
            patcher = patch('app.views.' + target, return_value=result)
            patcher.start()
            self.addCleanup(patcher.stop)

    def login(self, username='First', password='wrong', ip='192.0.2.1', admin=False, **extra):
        return self.client.post(
            '/api/signin/admin' if admin else '/api/signin',
            dict(username=username, password=password, captcha_token='test'),
            format='json', REMOTE_ADDR=ip, **extra,
        )

    def test_account_limit_combines_aliases_ips_and_entry_points(self):
        for index in range(5):
            response = self.login(
                username='First' if index % 2 else 'FIRST@example.com',
                ip=f'192.0.2.{index + 1}', admin=bool(index % 2),
            )
            self.assertEqual(response.status_code, 401)
        self.assertEqual(self.login(password='correct', ip='192.0.2.9').status_code, 429)
        self.assertEqual(self.login(username='Second', password='correct').status_code, 200)

    def test_success_resets_account_but_preserves_ip_count(self):
        for _ in range(4):
            self.assertEqual(self.login().status_code, 401)
        self.assertEqual(self.login(password='correct').status_code, 200)
        self.assertEqual(sorted(LoginRateLimit.objects.values_list('attempts', flat=True)), [0, 5])
        for _ in range(5):
            self.assertEqual(self.login().status_code, 401)
        self.assertEqual(self.login().status_code, 429)

    def test_ip_limit_counts_successful_requests_across_accounts(self):
        for index in range(30):
            name = 'First' if index % 2 else 'Second'
            self.assertEqual(self.login(username=name, password='correct').status_code, 200)
        response = self.login(password='correct')
        self.assertEqual(response.status_code, 429)
        self.assertTrue(0 < int(response['Retry-After']) <= 300)
        self.assertEqual(self.login(password='correct', ip='192.0.2.2').status_code, 200)

    def test_invalid_payload_and_captcha_count_only_towards_ip(self):
        self.assertEqual(self.login(username=[]).status_code, 400)
        with patch('app.views.verify_captcha', return_value=(False, 'Invalid CAPTCHA')):
            self.assertEqual(self.login().status_code, 403)
        self.assertEqual(list(LoginRateLimit.objects.values_list('attempts', flat=True)), [2])

    def test_account_window_expires_without_blocked_requests_extending_it(self):
        for _ in range(5):
            self.login()
        self.assertEqual(self.login().status_code, 429)
        account = LoginRateLimit.objects.get(attempts=5)
        started = timezone.now() - timedelta(seconds=181)
        LoginRateLimit.objects.filter(pk=account.pk).update(window_started_at=started)
        response = self.login()
        self.assertEqual(response.status_code, 429)
        self.assertTrue(0 < int(response['Retry-After']) <= 120)
        account.refresh_from_db()
        self.assertEqual(account.window_started_at, started)
        LoginRateLimit.objects.filter(pk=account.pk).update(
            window_started_at=timezone.now() - timedelta(seconds=301)
        )
        self.assertEqual(self.login().status_code, 401)
        account.refresh_from_db()
        self.assertEqual(account.attempts, 1)

    def test_ip_window_expires_and_ignores_untrusted_forwarded_header(self):
        for _ in range(30):
            self.login(username=[])
        response = self.login(HTTP_X_FORWARDED_FOR='192.0.2.99')
        self.assertEqual(response.status_code, 429)
        ip_counter = LoginRateLimit.objects.get()
        original_start = ip_counter.window_started_at
        ip_counter.refresh_from_db()
        self.assertEqual(ip_counter.window_started_at, original_start)
        LoginRateLimit.objects.update(window_started_at=timezone.now() - timedelta(seconds=301))
        self.assertEqual(self.login(password='correct').status_code, 200)

    def test_configured_limits(self):
        account, ip = SignInRateThrottle(), SignInIPRateThrottle()
        self.assertEqual((account.num_requests, account.duration), (5, 300))
        self.assertEqual((ip.num_requests, ip.duration), (30, 300))
