import os
from crewai import Agent, Task, Crew
from crewai.llm import LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def create_filter_crew(emails: list) -> str:
    classifier = Agent(
        role="Email Classifier",
        goal="Classify emails into categories accurately",
        backstory="You are an expert at reading emails and categorizing them.",
        llm=llm,
        verbose=False
    )

    email_text = ""
    for i, email in enumerate(emails, 1):
        email_text += f"""
Email {i}:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body'][:300]}
---
"""

    task = Task(
    description=f"""
Classify each email into ONE category and assign a priority level.

Categories:
- Interview Invite
- Online Test / Assessment
- Job Offer
- Rejection
- HR Follow-up
- Promotional
- Newsletter
- Spam

Priority Levels:
- P1 (URGENT) → Interview Invite, Job Offer
- P2 (HIGH)   → Online Test / Assessment, HR Follow-up
- P3 (MEDIUM) → Rejection
- P4 (LOW)    → Promotional, Newsletter, Spam

Emails:
{email_text}

Return format (strictly follow):
Email 1: <category> | Priority: <P1/P2/P3/P4> | Reason: <one line>
Email 2: <category> | Priority: <P1/P2/P3/P4> | Reason: <one line>
...
""",
    expected_output="Numbered list with category, priority, and reason.",
    agent=classifier
)

    crew = Crew(agents=[classifier], tasks=[task], verbose=False)
    result = crew.kickoff()
    return str(result)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'src')
    from email_parser import fetch_and_parse_emails
    from gmail_auth import get_gmail_service
    
    service = get_gmail_service()
    emails = fetch_and_parse_emails(service)

    print("Classifying emails...\n")
    result = create_filter_crew(emails)
    print(result)