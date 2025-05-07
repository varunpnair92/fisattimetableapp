from django.shortcuts import render
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from sympy import latex, symbols, solve, simplify
from sympy.parsing.latex import parse_latex
from django.views.decorators.csrf import csrf_exempt
import traceback






from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Direct paths to credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'credentials', 'token.json')

def send_email(subject, message, to_email):
    
    # Load credentials
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Refresh the token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    # Create the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Prepare the email message
    mime_message = MIMEText(message)
    mime_message['to'] = to_email
    mime_message['subject'] = subject
    encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    # Send the email
    try:
        send_message = service.users().messages().send(
            userId='me', body={'raw': encoded_message}).execute()
        print(f"Message sent: {send_message['id']}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False






@api_view(['POST'])
def emailAny(request):
    data = request.data
    emailid = data.get("emailid")
    subject = data.get("subject")
    message = data.get("message")
    
    if send_email(subject, message, emailid):
        return Response({"status": "Success"})
    else:
        return Response({"status": "Error"}, status=500)
