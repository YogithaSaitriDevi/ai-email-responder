import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_emails(service, max_results=5):
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        txt = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        headers = txt['payload']['headers']
        subject = next((h['value'] for h in headers 
                       if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers 
                      if h['name'] == 'From'), 'Unknown')
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender
        })
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print("-" * 50)
    return emails

if __name__ == '__main__':
    print("Connecting to Gmail...")
    service = get_gmail_service()
    print("Connected! Fetching unread emails...\n")
    emails = fetch_unread_emails(service)
    print(f"\nTotal unread fetched: {len(emails)}")