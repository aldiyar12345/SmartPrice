from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

def verify_google_token(token):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        return idinfo
    except ValueError:
        # Invalid token
        return None
