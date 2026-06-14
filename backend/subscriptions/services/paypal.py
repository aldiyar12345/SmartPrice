import os
import requests
from requests.auth import HTTPBasicAuth

PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

def get_access_token():
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("PayPal credentials not configured")
        
    url = f"{PAYPAL_API_BASE}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    data = {
        "grant_type": "client_credentials"
    }
    
    response = requests.post(url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret))
    response.raise_for_status()
    return response.json()["access_token"]

def create_order(amount: float):
    access_token = get_access_token()
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # PayPal не поддерживает KZT, поэтому для демонстрации конвертируем в USD (примерно / 500)
    # Если сумма 0, то оплата не требуется
    amount_usd = float(amount) / 500.0 if float(amount) > 0 else 0
    # PayPal требует ровно 2 знака после запятой
    amount_str = f"{amount_usd:.2f}"
    
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": amount_str
                }
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def capture_order(order_id: str):
    access_token = get_access_token()
    url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()
