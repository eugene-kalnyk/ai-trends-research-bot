#!/usr/bin/env python3
"""
Newsletter Scanner Utility

Scans Gmail for newsletters from the last 30 days and shows what's available.
This helps users identify which newsletters to include/exclude in their analysis.
"""

import sys
import os
from collections import defaultdict
from datetime import datetime

# Add src to path
sys.path.insert(0, '../src')

from gmail_client import GmailClient


def main():
    """Scan and display newsletters from the last 30 days."""
    print("🔍 AI Trends Research Bot - Newsletter Scanner")
    print("=" * 50)
    
    # Initialize Gmail client
    print("\n📧 Connecting to Gmail...")
    gmail_client = GmailClient(
        credentials_path='../config/credentials.json',
        token_path='../config/token.json'
    )
    
    # Authenticate
    if not gmail_client.authenticate():
        print("❌ Failed to authenticate with Gmail API")
        print("\nMake sure you have:")
        print("1. credentials.json file in the current directory")
        print("2. Gmail API enabled in Google Cloud Console")
        return False
    
    # Get user profile
    profile = gmail_client.get_user_profile()
    print(f"✅ Connected to: {profile.get('email', 'Unknown')}")
    print(f"📊 Total messages in account: {profile.get('messages_total', 0):,}")
    
    print("\n🔎 Scanning newsletters from the last 30 days...")
    
    # Get newsletters
    newsletters = gmail_client.get_newsletters_last_days(30)
    
    if not newsletters:
        print("❌ No newsletters found in the last 30 days")
        print("\nTry checking:")
        print("1. Your search filters might be too restrictive")
        print("2. You might not have newsletters in the last 30 days")
        return False
    
    print(f"📧 Found {len(newsletters)} potential newsletters")
    
    # Analyze senders
    sender_counts = gmail_client.analyze_senders(newsletters)
    
    # Group by domain
    domain_stats = defaultdict(lambda: {'count': 0, 'senders': set()})
    
    for sender, count in sender_counts.items():
        if '@' in sender:
            domain = sender.split('@')[1].lower()
            domain_stats[domain]['count'] += count
            domain_stats[domain]['senders'].add(sender)
    
    # Sort domains by email count
    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 NEWSLETTER ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\n🗓️  **Analysis Period**: Last 30 days")
    print(f"📧 **Total Newsletters Found**: {len(newsletters)}")
    print(f"🏢 **Unique Domains**: {len(domain_stats)}")
    print(f"👤 **Unique Senders**: {len(sender_counts)}")
    
    print("\n🏆 **TOP NEWSLETTER DOMAINS**")
    print("-" * 40)
    
    for i, (domain, stats) in enumerate(sorted_domains[:15], 1):
        print(f"{i:2d}. {domain:<25} ({stats['count']:3d} emails)")
        
        # Show top senders for this domain
        domain_senders = [(s, sender_counts[s]) for s in stats['senders']]
        domain_senders.sort(key=lambda x: x[1], reverse=True)
        
        for sender, count in domain_senders[:3]:  # Top 3 senders per domain
            sender_name = sender.split('@')[0] if '@' in sender else sender
            print(f"    • {sender_name:<20} ({count} emails)")
    
    # Recent newsletter subjects
    print(f"\n📝 **RECENT NEWSLETTER SUBJECTS** (Last 10)")
    print("-" * 40)
    
    # Sort by date and show recent subjects
    newsletters_by_date = sorted(newsletters, key=lambda x: x['date'], reverse=True)
    
    for i, newsletter in enumerate(newsletters_by_date[:10], 1):
        date_str = newsletter['date'].strftime('%Y-%m-%d')
        subject = newsletter['subject'][:50] + "..." if len(newsletter['subject']) > 50 else newsletter['subject']
        sender_domain = newsletter['sender'].split('@')[1] if '@' in newsletter['sender'] else newsletter['sender']
        print(f"{i:2d}. [{date_str}] {subject}")
        print(f"    From: {sender_domain}")
    
    # Recommendations
    print(f"\n💡 **RECOMMENDATIONS**")
    print("-" * 40)
    
    # Find likely promotional domains
    promotional_domains = []
    for domain, stats in sorted_domains:
        if stats['count'] > 10 or any(word in domain.lower() for word in ['promo', 'deal', 'sale', 'marketing']):
            promotional_domains.append(domain)
    
    if promotional_domains:
        print("🚫 **Domains you might want to EXCLUDE** (high volume/promotional):")
        for domain in promotional_domains[:5]:
            print(f"   • {domain}")
    
    # Find AI/tech domains
    ai_domains = []
    for domain, stats in sorted_domains:
        if any(word in domain.lower() for word in ['ai', 'tech', 'data', 'ml', 'research']):
            ai_domains.append(domain)
    
    if ai_domains:
        print("\n✅ **Domains that look AI/tech related** (good candidates):")
        for domain in ai_domains[:10]:
            print(f"   • {domain}")
    
    # Configuration suggestions
    print(f"\n⚙️  **CONFIGURATION SUGGESTIONS**")
    print("-" * 40)
    print("Add to your .env file:")
    print()
    
    if promotional_domains:
        blacklist = ','.join(promotional_domains[:5])
        print(f"# Exclude high-volume promotional domains")
        print(f"NEWSLETTER_BLACKLIST={blacklist}")
        print()
    
    if ai_domains:
        whitelist = ','.join(ai_domains[:10])
        print(f"# Include AI/tech focused domains")
        print(f"NEWSLETTER_WHITELIST={whitelist}")
    
    print(f"\n✨ Scan complete! Use this information to configure your newsletter filtering.")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Scan cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 