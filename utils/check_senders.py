"""
Check Senders Utility

This script connects to Gmail, fetches recent newsletters, and prints a list of
unique senders. This helps verify if specific newsletters (e.g., from Product Hunt)
are being correctly fetched and not filtered out.
"""

import sys
import os
from collections import Counter

# Add src directory to path to allow imports from other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gmail_client import GmailClient
from src.config import load_config

config = load_config()

def check_recent_senders(days=7):
    """
    Connects to Gmail, fetches newsletters from the last `days`, and prints
    a summary of the senders.
    """
    print("Connecting to Gmail to check recent newsletter senders...")

    # Initialize Gmail client and authenticate
    gmail_client = GmailClient(
        credentials_path=config['gmail_credentials_path'],
        token_path=config['gmail_token_path']
    )
    if not gmail_client.authenticate():
        print("🔴 Failed to authenticate with Gmail. Please check your credentials.")
        return

    print(f"✅ Authenticated successfully.")
    print(f"Fetching newsletters from the last {days} days...")

    # Fetch raw newsletters
    try:
        raw_newsletters = gmail_client.get_newsletters_last_days(days)
    except Exception as e:
        print(f"🔴 An error occurred while fetching emails: {e}")
        return

    if not raw_newsletters:
        print("\nNo newsletters found in the last {days} days.")
        return

    print(f"Found {len(raw_newsletters)} total potential newsletters.")

    # Count sender occurrences
    sender_counts = Counter(n['sender'] for n in raw_newsletters)

    print("\n--- Unique Senders Found ---")
    print("Count | Sender")
    print("----------------------------")
    for sender, count in sender_counts.most_common():
        print(f"{count:<5} | {sender}")
    
    print("\n--- Instructions ---")
    print("1. Review the list above for your Product Hunt newsletter senders.")
    print("2. If they appear, you're all set! The bot is receiving them.")
    print("3. If they are missing, they might be filtered out. Check your settings in the `.env` file, especially:")
    print("   - `NEWSLETTER_BLACKLIST`")
    print("   - `NEWSLETTER_SENDER_BLACKLIST`")
    print("4. You may need to remove 'producthunt.com' or related names from the blacklists.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check recent newsletter senders from Gmail.")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back for newsletters. Default is 7."
    )
    args = parser.parse_args()

    check_recent_senders(days=args.days)

