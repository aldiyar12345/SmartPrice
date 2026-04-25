from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import AccountCredential
from django.test import TestCase

class AccountsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test@example.com", email="test@example.com", password="password123")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "test@example.com")
        self.assertEqual(self.user.email, "test@example.com")
        
    def test_credential_submit(self):
        response = self.client.post("/api/auth/submit/", {"email": "submit@example.com", "password": "abc"})
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())
        self.assertTrue(AccountCredential.objects.filter(email="submit@example.com").exists())

    def test_login_success(self):
        response = self.client.post("/api/auth/login/", {"email": "test@example.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_login_fail(self):
        response = self.client.post("/api/auth/login/", {"email": "test@example.com", "password": "wrongpassword"})
        self.assertEqual(response.status_code, 401)

    def test_credential_verify_success(self):
        cred = AccountCredential.objects.create(email="new@example.com", password="pwd", generated_code="123456")
        response = self.client.post("/api/auth/verify/", {"id": cred.id, "code": "123456"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["verified"])

    def test_credential_verify_fail(self):
        cred = AccountCredential.objects.create(email="fail@example.com", password="pwd", generated_code="123456")
        response = self.client.post("/api/auth/verify/", {"id": cred.id, "code": "000000"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["verified"])

    def test_me_view_unauthenticated(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 401)
