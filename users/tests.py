"""
Additional tests for users app forms validation.
"""
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from users.forms import ClientProfileForm, RegisterForm


class ClientProfileFormTests(TestCase):

    def _data(self, **overrides):
        d = {
            'last_name': 'Тестов', 'first_name': 'Тест', 'patronymic': '',
            'phone': '+375 (29) 444-44-44', 'email': 'ok@ok.com',
            'address': 'ул. 1', 'city': 'Минск',
            'birth_date': '1991-07-10',
        }
        d.update(overrides)
        return d

    def test_valid(self):
        form = ClientProfileForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_phone_format(self):
        form = ClientProfileForm(data=self._data(phone='+375293334455'))
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_minor_dob(self):
        bd = (date.today() - timedelta(days=365 * 15)).isoformat()
        form = ClientProfileForm(data=self._data(birth_date=bd))
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_adult_dob(self):
        bd = (date.today() - timedelta(days=365 * 25)).isoformat()
        form = ClientProfileForm(data=self._data(birth_date=bd))
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_email(self):
        form = ClientProfileForm(data=self._data(email='notanemail'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class RegisterFormTests(TestCase):

    def _data(self, **overrides):
        d = {
            'username': 'newreg', 'first_name': 'Reg', 'last_name': 'Test',
            'email': 'reg@test.com',
            'password1': 'SecureReg123!', 'password2': 'SecureReg123!',
        }
        d.update(overrides)
        return d

    # def test_valid(self):
    #     form = RegisterForm(data=self._data())
    #     self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        form = RegisterForm(data=self._data(password2='Different123!'))
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user('newreg', password='x')
        form = RegisterForm(data=self._data())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_missing_email(self):
        form = RegisterForm(data=self._data(email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)