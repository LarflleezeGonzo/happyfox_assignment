import pytest
from unittest.mock import patch
from scripts.mail_loader import fetch_emails, store_emails

@pytest.fixture
def mock_service():
    with patch('scripts.mail_loader.build') as mock_build:
        yield mock_build.return_value

def test_fetch_emails(mock_service):
    mock_messages = [
        {
            "id": "1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "example@example.com"},
                    {"name": "Subject", "value": "Test Email"},
                    {"name": "Date", "value": "Sun, 21 Apr 2024 07:40:00 +0000 (UTC)"},
                ]
            }
        }
    ]
    mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {"messages": mock_messages}

    # Call the fetch_emails function
    emails = fetch_emails(mock_service)

    # Assert the expected behavior
    assert len(emails) == 1
    assert emails[0]["thread_id"] == "1"
    assert emails[0]["sender"] == "example@example.com"
    assert emails[0]["subject"] == "Test Email"


def test_store_emails(mocker):

    mock_db = mocker.MagicMock()

    messages = [
        {
            "thread_id": "1",
            "subject": "Test Email",
            "date_received": "2023-01-01",
            "sender": "example@example.com",
        }
    ]

    store_emails(mock_db, messages)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
