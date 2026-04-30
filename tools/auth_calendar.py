"""One-time OAuth2 authentication for Google Calendar API.

Run this script once to authorize Guidelight AI to access your Google Calendar:

    python3 tools/auth_calendar.py

Prerequisites:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create an OAuth 2.0 Client ID (Desktop App type)
3. Download the JSON and save as `credentials.json` in the project root
4. Enable the Google Calendar API in your project

This will open a browser window for authentication and save the token locally.
"""

import sys
from pathlib import Path

# Add parent dir to path so we can find credentials
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

TOKEN_PATH = ROOT / "token.json"
CREDENTIALS_PATH = ROOT / "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: Required packages not installed. Run:")
        print("  pip install google-auth-oauthlib google-api-python-client")
        sys.exit(1)

    if not CREDENTIALS_PATH.exists():
        print(f"ERROR: '{CREDENTIALS_PATH}' not found.")
        print()
        print("To set up Google Calendar integration:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create an OAuth 2.0 Client ID (type: Desktop App)")
        print("3. Download the JSON file")
        print(f"4. Save it as: {CREDENTIALS_PATH}")
        print("5. Enable Google Calendar API at:")
        print("   https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")
        sys.exit(1)

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        print("✓ Already authenticated! Token is valid.")
        print(f"  Token file: {TOKEN_PATH}")
        return

    if creds and creds.expired and creds.refresh_token:
        print("Token expired, refreshing...")
        creds.refresh(Request())
    else:
        print("Opening browser for Google Calendar authorization...")
        print("(Select the Google account you want to add events to)")
        print()
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_PATH), SCOPES
        )
        creds = flow.run_local_server(port=0)

    # Save token
    TOKEN_PATH.write_text(creds.to_json())
    print()
    print(f"✓ Authentication successful! Token saved to: {TOKEN_PATH}")
    print()
    print("Guidelight AI will now create events in your Google Calendar.")
    print("You can revoke access anytime at: https://myaccount.google.com/permissions")


if __name__ == "__main__":
    main()
