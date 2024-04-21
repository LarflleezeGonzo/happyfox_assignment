from common.db import get_db, Email
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, and_
import json
from mail_loader import authenticate
from googleapiclient.discovery import build

def read_rules_from_file(file_path):
    with open(file_path, "r") as file:
        rules_data = json.load(file)
    return rules_data

file_path = "scripts/common/rules.json"
rules_data = read_rules_from_file(file_path)


# Mapping for string predicates
string_filters_mapping = {
    "contains": lambda field, value: field.ilike(f"%{value}%"),
    "does_not_contain": lambda field, value: ~field.ilike(f"%{value}%"),
    "equals": lambda field, value: field == value,
    "does_not_equal": lambda field, value: field != value,
}

# Mapping for date predicates
date_filters_mapping = {
    "less_than_days": lambda field, value: field
    < datetime.now() - timedelta(days=int(value)),
    "greater_than_days": lambda field, value: field
    > datetime.now() - timedelta(days=int(value)),
    "less_than_months": lambda field, value: field
    < datetime.now() - relativedelta(months=int(value)),
    "greater_than_months": lambda field, value: field
    > datetime.now() - relativedelta(months=int(value)),
}

set_ops_mapping = {"any": "OR", "all": "AND"}


# Query emails based on rules
def query_emails(rule_set_operator: str, rules_list: list):
    with get_db() as db:
        query = db.query(Email.thread_id)
        filter_conditions = []

        for rule in rules_list:
            field = getattr(Email, rule["field_name"])
            value = rule["value"]
            if rule["field_name"] == "date_received":
                filter_func = date_filters_mapping.get(rule["predicate"])
            else:
                filter_func = string_filters_mapping.get(rule["predicate"])

            if filter_func:
                filter_conditions.append(filter_func(field, value))

        if rule_set_operator == "AND":
            combined_condition = and_(*filter_conditions)
        elif rule_set_operator == "OR":
            combined_condition = or_(*filter_conditions)

        if filter_conditions:
            query = query.filter(combined_condition)
        results =  query.all()
        thread_ids = [result[0] for result in results]
        return thread_ids
    

    

def mark_emails(service, thread_ids, read=True):
    """Mark emails as read or unread."""
    try:
        for thread_id in thread_ids:
            body = {"ids": thread_id, "addLabelIds": ["UNREAD"]} if not read else {"ids": thread_id, "removeLabelIds": ["UNREAD"]}
            service.users().messages().batchModify(userId="me", body=body).execute()
    except Exception as e:
        print(f"An error occurred: {e}")

def move_emails(service, thread_ids, destination):
    """Move emails to a specified destination."""
    try:
        for thread_id in thread_ids:
            body = {"ids": thread_id, "addLabelIds": [destination], "removeLabelIds": ["INBOX"]}
            service.users().messages().batchModify(userId="me", body=body).execute()
    except Exception as e:
        print(f"An error occurred while moving emails: {e}")

def main():
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)
    for main_rule in rules_data:
        rules_list = main_rule["rules"]
        actions = main_rule["actions"]
        rules_predicate = set_ops_mapping.get(main_rule["predicate"].lower(), "AND")
        thread_ids = query_emails(rule_set_operator=rules_predicate, rules_list=rules_list)
        if actions.get("read") is not None:
            mark_emails(service, thread_ids, read=actions["read"])
        if actions.get("move"):
            move_emails(service, thread_ids, destination="Label_9085226052946982835")


if __name__ == "__main__":
    main()


