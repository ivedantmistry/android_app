from django.test import TestCase

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class OTPVerificationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')

    def test_signup_and_otp_verification(self):
        # Step 1: User Signup
        signup_response = self.client.post(self.signup_url, {
            "first_name": "string",
            "last_name": "string",
            "email": "testuser@gmail.com",
            "password": "strong_password",
            "password2": "strong_password"
        })
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        user_id = signup_response.json()['data']['id']  # Get user ID

        # Step 2: Get OTP from email
        otp = self.get_otp_from_email()

        # Step 3: OTP Verification
        verify_url = self.otp_verify_url = reverse('account-verification', args=[user_id, otp])
        verify_response = self.client.get(verify_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def get_otp_from_email(self):
        email = mail.outbox[0]  # Access the email sent
        otp = email.body.split('is: ')[1].split()[0]  # Extract OTP (adjust if needed)
        return otp

class SignUpTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')

    def test_signup(self):
        data = {
            "first_name": "string",
            "last_name": "string",
            "email": "testuser@gmail.com",
            "password": "strong_password",
            "password2": "strong_password"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.json()['data'])  # Ensures user ID is returned


class SignInTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signin_url = reverse('signin')
        self.signup_url = reverse('signup')

    def signup_and_otp_verification(self):
        # Step 1: User Signup
        signup_response = self.client.post(self.signup_url, {
            "first_name": "string",
            "last_name": "string",
            "email": "testuser@gmail.com",
            "password": "strong_password",
            "password2": "strong_password"
        })
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        user_id = signup_response.json()['data']['id']  # Get user ID

        # Step 2: Get OTP from email
        otp = self.get_otp_from_email()

        # Step 3: OTP Verification
        verify_url = self.otp_verify_url = reverse('account-verification', args=[user_id, otp])
        verify_response = self.client.get(verify_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def get_otp_from_email(self):
        email = mail.outbox[0]  # Access the email sent
        otp = email.body.split('is: ')[1].split()[0]  # Extract OTP (adjust if needed)
        return otp

    def test_signin(self):
        self.signup_and_otp_verification()
        data = {
            'email': 'testuser@gmail.com',
            'password': 'strong_password'
        }
        response = self.client.post(self.signin_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.json()['data'])
