import base64
from gmail_auth import get_gmail_service

def extract_body(payload):
    """Recursively extract plain text body from email payload."""
    if 'parts' in payload:
        for part in payload['parts']:
            result = extract_body(part)
            if result:
                return result
    else:
        mime_type = payload.get('mimeType', '')
        if mime_type == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return None

def fetch_and_parse_emails(service, max_results=5):
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
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender  = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        body    = extract_body(txt['payload']) or 'No body found'

        emails.append({
            'id':      msg['id'],
            'subject': subject,
            'sender':  sender,
            'body':    body.strip()
        })

    return emails

if __name__ == '__main__':
    service = get_gmail_service()
    emails  = fetch_and_parse_emails(service)

    for i, email in enumerate(emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"From:    {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Body preview: {email['body'][:200]}")
        print("-" * 50)

    print(f"\nTotal parsed: {len(emails)}")