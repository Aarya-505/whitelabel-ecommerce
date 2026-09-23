import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_auth_separation():
    client = Client()
    
    # 1. Create or get regular customer and staff vendor
    customer, _ = User.objects.get_or_create(username='shopper_rahul', defaults={
        'email': 'rahul@example.com',
        'first_name': 'Rahul',
        'is_staff': False,
        'is_superuser': False
    })
    customer.set_password('CustomerPass123!')
    customer.save()

    vendor, _ = User.objects.get_or_create(username='vendor_admin', defaults={
        'email': 'vendor@aurastore.com',
        'first_name': 'AuraVendor',
        'is_staff': True,
        'is_superuser': True
    })
    vendor.set_password('VendorAdminPass123!')
    vendor.save()

    print(">>> 1. Checking unauthenticated homepage navbar links...")
    resp = client.get(reverse('storefront:home'))
    assert resp.status_code == 200
    content = resp.content.decode('utf-8')
    assert "Hello, User" in content or "Sign In" in content
    assert "admin-action-btn" in content
    assert "Shop Vendor" in content
    print(" [PASS] Unauthenticated navbar shows Hello User and distinct Shop Vendor Admin button")

    print("\n>>> 2. Testing Customer Login flow...")
    login_resp = client.post(reverse('storefront:user_login'), {
        'username_or_email': 'shopper_rahul',
        'password': 'CustomerPass123!'
    }, follow=True)
    assert login_resp.status_code == 200
    home_content = client.get(reverse('storefront:home')).content.decode('utf-8')
    assert "Hello, Rahul" in home_content or "Account & Orders" in home_content
    print(" [PASS] Customer logged in successfully and navbar reflects 'Hello, Rahul'")

    print("\n>>> 3. Verifying Customer visiting /admin-panel/login/ gets Access Restricted prompt...")
    admin_login_resp = client.get(reverse('admin_dashboard:login'))
    assert admin_login_resp.status_code == 200
    login_html = admin_login_resp.content.decode('utf-8')
    assert "No Access to This Portal" in login_html
    assert "name=\"username\"" not in login_html
    assert "Looking for customer shopping sign in" not in login_html
    print(" [PASS] Logged-in Customer sees 'No Access to This Portal' without login form or shopping sign-in prompt")

    print("\n>>> 4. Verifying Customer visiting /admin-panel/overview/ is blocked...")
    admin_dash_resp = client.get(reverse('admin_dashboard:overview'), follow=True)
    assert admin_dash_resp.status_code == 200
    dash_content = admin_dash_resp.content.decode('utf-8')
    assert "No Access to This Portal" in dash_content or "Access Denied" in dash_content
    print(" [PASS] Customer cannot access /admin-panel/overview/ and is redirected with Access Denied notice")

    print("\n>>> 5. Verifying Customer Sign In page has no Store Vendor prompt...")
    client.logout()
    cust_login_page = client.get(reverse('storefront:user_login')).content.decode('utf-8')
    assert "Store Vendor / Shopkeeper" not in cust_login_page
    assert "Go to Shop Vendor Admin Portal" not in cust_login_page
    print(" [PASS] Customer Sign In page has no Store Vendor link")

    print("\n>>> 6. Verifying unauthenticated /admin-panel/login/ is clean...")
    unauth_admin_login = client.get(reverse('admin_dashboard:login')).content.decode('utf-8')
    assert "name=\"username\"" in unauth_admin_login
    assert "Looking for customer shopping sign in" not in unauth_admin_login
    assert "Currently logged in as Customer" not in unauth_admin_login
    print(" [PASS] Unauthenticated Admin Portal Login has clean vendor form without customer prompt")

    print("\n>>> 7. Verifying Customer credentials fail when submitted to Vendor Login...")
    vendor_login_attempt = client.post(reverse('admin_dashboard:login'), {
        'username': 'shopper_rahul',
        'password': 'CustomerPass123!'
    }, follow=True)
    vlogin_content = vendor_login_attempt.content.decode('utf-8')
    assert "Access Denied" in vlogin_content
    print(" [PASS] Submitting customer credentials to Vendor Login is strictly rejected with Access Denied error")

    print("\n>>> 8. Verifying Vendor Admin Login succeeds and loads dashboard...")
    vendor_login = client.post(reverse('admin_dashboard:login'), {
        'username': 'vendor_admin',
        'password': 'VendorAdminPass123!'
    }, follow=True)
    assert vendor_login.status_code == 200
    v_content = vendor_login.content.decode('utf-8')
    assert "Store Owner" in v_content or "Vendor Admin" in v_content or "Overview" in v_content
    print(" [PASS] Vendor Admin logged in successfully to Store Owner Dashboard")

    print("\n==========================================")
    print("ALL AUTHENTICATION SEPARATION TESTS PASSED!")
    print("==========================================")

if __name__ == '__main__':
    test_auth_separation()
