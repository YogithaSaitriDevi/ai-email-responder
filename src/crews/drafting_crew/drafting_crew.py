import os
import sys
sys.path.insert(0, 'src')

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def create_drafting_crew(emails: list) -> list:
    drafter = Agent(
        role="Email Reply Drafter",
        goal="Draft professional and concise replies to important emails",
        backstory="You are an expert at writing clear, professional email replies.",
        llm=llm,
        verbose=False
    )

    drafts = []

    for email in emails:
        task = Task(
    description=f"""
Draft a professional reply for this job-related email.

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body'][:400]}

Reply rules based on email type:
- Interview Invite → Confirm availability, ask for date/time/format
- Online Test → Acknowledge, confirm you will attempt it
- Job Offer → Express enthusiasm, ask next steps
- HR Follow-up → Polite status update request
- Rejection → Graceful thank you, ask for feedback

General rules:
- 3-5 sentences max
- Professional tone
- Start with "Hello," or "Dear [Name],"
- End with "Best regards,\\nYogitha"
""",
    expected_output="A short professional job-hunt email reply.",
    agent=drafter
)

        crew = Crew(agents=[drafter], tasks=[task], verbose=False)
        result = crew.kickoff()

        drafts.append({
            'subject': f"Re: {email['subject']}",
            'to': email['sender'],
            'body': str(result)
        })

    return drafts


if __name__ == '__main__':
    from email_parser import fetch_and_parse_emails
    from gmail_auth import get_gmail_service

    service = get_gmail_service()
    emails = fetch_and_parse_emails(service, max_results=2)

    print("Drafting replies...\n")
    drafts = create_drafting_crew(emails)

    for i, draft in enumerate(drafts, 1):
        print(f"\n--- Draft {i} ---")
        print(f"To: {draft['to']}")
        print(f"Subject: {draft['subject']}")
        print(f"Body:\n{draft['body']}")
        print("-" * 50)