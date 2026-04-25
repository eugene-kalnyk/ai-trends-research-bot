#!/usr/bin/env python3
"""
Test Newsletter Filtering

Tests the configured newsletter filtering to ensure excluded newsletters are properly filtered out.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, '../src')

from gmail_client import GmailClient
from email_processor import EmailProcessor
from dotenv import load_dotenv


def main():
    """Test newsletter filtering configuration."""
    print("🧪 Testing Newsletter Filtering Configuration")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Get configuration
    config = {
        'newsletter_whitelist': [x.strip() for x in os.getenv('NEWSLETTER_WHITELIST', '').split(',') if x.strip()],
        'newsletter_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_BLACKLIST', '').split(',') if x.strip()],
        'newsletter_sender_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_SENDER_BLACKLIST', '').split(',') if x.strip()],
        'newsletter_subject_blacklist': [x.strip() for x in os.getenv('NEWSLETTER_SUBJECT_BLACKLIST', '').split(',') if x.strip()],
    }
    
    print(f"📋 Configuration Loaded:")
    print(f"   • Domain Blacklist: {config['newsletter_blacklist']}")
    print(f"   • Sender Blacklist: {config['newsletter_sender_blacklist']}")
    print(f"   • Subject Blacklist: {config['newsletter_subject_blacklist']}")
    print(f"   • Domain Whitelist: {config['newsletter_whitelist'] or 'None (allow all)'}")
    
    # Initialize processors
    print(f"\n📧 Connecting to Gmail...")
    gmail_client = GmailClient(
        credentials_path='../config/credentials.json',
        token_path='../config/token.json'
    )
    
    if not gmail_client.authenticate():
        print("❌ Failed to authenticate with Gmail")
        return False
    
    print(f"✅ Connected successfully")
    
    # Initialize email processor with configuration
    email_processor = EmailProcessor(
        whitelist=config['newsletter_whitelist'],
        blacklist=config['newsletter_blacklist'],
        sender_blacklist=config['newsletter_sender_blacklist'],
        subject_blacklist=config['newsletter_subject_blacklist']
    )
    
    # Get recent newsletters
    print(f"\n🔍 Fetching newsletters from last 7 days...")
    newsletters = gmail_client.get_newsletters_last_days(7)
    
    if not newsletters:
        print("❌ No newsletters found")
        return False
    
    print(f"📧 Found {len(newsletters)} potential newsletters")
    
    # Test filtering
    print(f"\n🔬 Testing Filtering...")
    
    filtered_newsletters = []
    excluded_newsletters = []
    
    for newsletter in newsletters:
        if email_processor.is_newsletter(newsletter):
            filtered_newsletters.append(newsletter)
        else:
            excluded_newsletters.append(newsletter)
    
    # Results
    print(f"\n📊 FILTERING RESULTS")
    print("-" * 40)
    print(f"✅ Newsletters INCLUDED: {len(filtered_newsletters)}")
    print(f"🚫 Newsletters EXCLUDED: {len(excluded_newsletters)}")
    
    if excluded_newsletters:
        print(f"\n🚫 **EXCLUDED NEWSLETTERS** ({len(excluded_newsletters)} total):")
        print("-" * 80)
        for i, newsletter in enumerate(excluded_newsletters, 1):
            sender = newsletter.get('sender', '')
            subject = newsletter.get('subject', '')
            date_str = newsletter.get('date', datetime.now()).strftime('%Y-%m-%d')
            
            print(f"{i:2d}. [{date_str}] {subject}")
            print(f"    📧 From: {sender}")
            print()
    
    if filtered_newsletters:
        print(f"\n✅ **ALL INCLUDED NEWSLETTERS** ({len(filtered_newsletters)} total):")
        print("-" * 80)
        for i, newsletter in enumerate(filtered_newsletters, 1):
            sender = newsletter.get('sender', '')
            subject = newsletter.get('subject', '')
            date_str = newsletter.get('date', datetime.now()).strftime('%Y-%m-%d')
            
            # Extract domain for easy identification
            if '@' in sender:
                if '<' in sender and '>' in sender:
                    email_part = sender.split('<')[1].split('>')[0]
                    domain = email_part.split('@')[1].lower().strip()
                else:
                    domain = sender.split('@')[1].lower().strip()
            else:
                domain = "unknown"
            
            print(f"{i:2d}. [{date_str}] {subject}")
            print(f"    📧 From: {sender}")
            print(f"    🌐 Domain: {domain}")
            print()
    
    # Summary by domain
    print(f"\n📊 **INCLUDED DOMAINS SUMMARY**")
    print("-" * 40)
    
    domain_counts = {}
    for newsletter in filtered_newsletters:
        sender = newsletter.get('sender', '')
        if '@' in sender:
            # Handle "Name <email@domain.com>" format
            if '<' in sender and '>' in sender:
                email_part = sender.split('<')[1].split('>')[0]
                domain = email_part.split('@')[1].lower().strip()
            else:
                # Handle "email@domain.com" format
                domain = sender.split('@')[1].lower().strip()
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {domain:<25} ({count} emails)")
    
    print(f"\n✨ Filtering test complete!")
    print(f"💡 If the results look good, you're ready for full AI analysis!")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 