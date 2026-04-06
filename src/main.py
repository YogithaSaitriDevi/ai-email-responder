import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from gmail_auth import get_gmail_service
from email_parser import fetch_and_parse_emails
from crews.email_filter_crew.email_filter_crew import create_filter_crew
from crews.drafting_crew.drafting_crew import create_drafting_crew

def main():
    print("=== AI Email Responder ===\n")

    print("Step 1: Connecting to Gmail...")
    service = get_gmail_service()
    print("Connected!\n")

    print("Step 2: Fetching unread emails...")
    emails = fetch_and_parse_emails(service, max_results=5)
    print(f"Fetched {len(emails)} emails\n")

    if not emails:
        print("No unread emails found!")
        return

    print("Step 3: Classifying emails...")
    classification = create_filter_crew(emails)
    print("\n=== CLASSIFICATION RESULT ===")
    print(classification)

    # Step 4: Filter important emails
    important_emails = []
    lines = classification.lower().split('\n')
    for line in lines:
        parts = line.split('|')
        category = parts[0] if parts else line
        if 'important' in category or 'action required' in category:
            for j, email in enumerate(emails):
                if f"email {j+1}" in category:
                    important_emails.append(emails[j])

    print(f"\nFound {len(important_emails)} important email(s) to reply to.\n")

    if important_emails:
        print("Step 4: Drafting replies...")
        drafts = create_drafting_crew(important_emails)

        print("\n=== DRAFT REPLIES ===")
        for i, draft in enumerate(drafts, 1):
            print(f"\n--- Draft {i} ---")
            print(f"To: {draft['to']}")
            print(f"Subject: {draft['subject']}")
            print(f"Body:\n{draft['body']}")
            print("-" * 50)
    else:
        print("No important emails — no drafts needed.")

    print("\n=== Done! ===")

if __name__ == '__main__':
    main()