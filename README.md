
# Email Processor

## Introduction

This repository contains Python scripts for automating email processing using the Gmail API and a rule engine.

## Requirements

- Python installed (version >= 3.6)
- Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials file (`credentials.json`) for Gmail API access
- SQLite database (created automatically by the scripts)
- Internet access for OAuth authentication with Google

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/LarflleezeGonzo/happyfox_assignment.git
   ```

2. Navigate to the project directory:

   ```bash
   cd happyfox_assignment
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy your `credentials.json` file to `scripts/common/credentials.json`.

## Usage

1. Run the email loader script to fetch emails from Gmail:

   ```bash
   python scripts/mail_loader.py
   ```

2. Run the rule engine script to apply rules on the loaded emails:

   ```bash
   python scripts/rule_engine.py
   ```

## Configuration

- Configure email loading settings in `scripts/common/settings.py`.
- Define email processing rules in `scripts/common/rules.json`.
- Define number of emails to load in `.env` file if it needs to be changed.
