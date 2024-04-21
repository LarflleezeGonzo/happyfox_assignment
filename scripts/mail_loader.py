import os
import pickle
import re
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from common.config import settings
from common.db import Base, Email, engine, get_db

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]
CREDS_FILE = "scripts/common/credentials.json"
TOKEN_FILE = "scripts/common/token.pickle"


Base.metadata.create_all(bind=engine)


def authenticate():
    """Authenticate with Gmail API using OAuth."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds


def fetch_emails(service, max_results=settings.EMAIL_MAX_MESSAGES):
    """Fetch a list of emails from the Inbox."""
    response = (
        service.users().messages().list(userId="me", maxResults=max_results).execute()
    )
    message_ids = [message["id"] for message in response.get("messages", [])]

    messages = []
    # Fetch selected fields for each message ID
    for message_id in message_ids:
        message = service.users().messages().get(userId="me", id=message_id).execute()
        msg_from = next(
            (
                header["value"]
                for header in message["payload"]["headers"]
                if header["name"] == "From"
            ),
            "",
        )
        subject = next(
            (
                header["value"]
                for header in message["payload"]["headers"]
                if header["name"] == "Subject"
            ),
            "",
        )
        date_received_str = next(
            (
                header["value"]
                for header in message["payload"]["headers"]
                if header["name"] == "Date"
            ),
            "",
        )

        # Remove additional information like "(IST)" from the date string
        date_received_str_cleaned = re.sub(r"\s+\(.*\)", "", date_received_str)
        date_received_dt = datetime.strptime(
            date_received_str_cleaned, "%a, %d %b %Y %H:%M:%S %z"
        )
        date_received_iso = date_received_dt.date()
        messages.append(
            {
                "sender": msg_from,
                "subject": subject,
                "date_received": date_received_iso,
                "thread_id": message_id,
            }
        )

    return messages


def store_emails(db: Session, messages: list):
    """Store fetched emails in the database."""
    emails = [
        Email(
            thread_id=message["thread_id"],
            subject=message["subject"],
            date_received=message["date_received"],
            sender=message["sender"],
        )
        for message in messages
    ]
    db.add_all(emails)
    db.commit()


def main():
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)
    messages = fetch_emails(service)
    try:
        with get_db() as db:
            store_emails(db, messages)
        print("Emails fetched and stored successfully.")
    except Exception as e:
        print(f"Error storing emails: {e}")


if __name__ == "__main__":
    main()
