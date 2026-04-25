"""
Email Processor Module

Handles email parsing, newsletter detection, and content extraction.
"""

import re
import email
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from bs4 import BeautifulSoup
import structlog


logger = structlog.get_logger(__name__)


@dataclass
class Newsletter:
    """Represents a parsed newsletter email."""
    sender: str
    subject: str
    date: datetime
    content: str
    html_content: str
    is_newsletter: bool
    source_domain: str


class EmailProcessor:
    """Handles email processing and newsletter detection."""
    
    def __init__(self, whitelist: List[str] = None, blacklist: List[str] = None, 
                 sender_blacklist: List[str] = None, subject_blacklist: List[str] = None):
        """Initialize email processor with filtering options."""
        self.whitelist = whitelist or []
        self.blacklist = blacklist or []
        self.sender_blacklist = sender_blacklist or []
        self.subject_blacklist = subject_blacklist or []
        self.newsletter_patterns = [
            r'newsletter',
            r'weekly\s+digest',
            r'daily\s+brief',
            r'trend\s+report',
            r'ai\s+news',
            r'machine\s+learning',
            r'artificial\s+intelligence',
            r'tech\s+digest',
            r'unsubscribe',
            r'newsletter@',
            r'noreply@',
            r'no-reply@'
        ]
    
    def is_newsletter(self, email_data: Dict) -> bool:
        """
        Determine if an email is a newsletter based on various criteria.
        
        Args:
            email_data: Dictionary containing email metadata
            
        Returns:
            bool: True if email is likely a newsletter
        """
        # Check subject line patterns
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '').lower()
        
        # Check subject blacklist first
        for blocked_subject in self.subject_blacklist:
            if blocked_subject.lower() in subject.lower():
                return False
        
        # Check sender blacklist
        sender_name = self._extract_sender_name(sender)
        if sender_name in self.sender_blacklist:
            return False
        
        # Check domain blacklist
        sender_domain = self._extract_domain(sender)
        if sender_domain in self.blacklist:
            return False
        
        # Check whitelist (if specified, sender domain must be in it)
        if self.whitelist and sender_domain not in self.whitelist:
            return False
        
        # Check for newsletter patterns
        for pattern in self.newsletter_patterns:
            if re.search(pattern, subject, re.IGNORECASE):
                return True
            if re.search(pattern, sender, re.IGNORECASE):
                return True
            
        return True
    
    def _extract_domain(self, email_address: str) -> str:
        """Extract domain from email address."""
        try:
            # Handle "Name <email@domain.com>" format
            if '<' in email_address and '>' in email_address:
                email_part = email_address.split('<')[1].split('>')[0]
                return email_part.split('@')[1].lower().strip()
            else:
                # Handle "email@domain.com" format
                return email_address.split('@')[1].lower().strip()
        except (IndexError, AttributeError):
            return ""
    
    def _extract_sender_name(self, sender: str) -> str:
        """Extract sender name from email address (before @)."""
        try:
            # Handle "Name <email@domain.com>" format
            if '<' in sender and '>' in sender:
                email_part = sender.split('<')[1].split('>')[0]
                return email_part.split('@')[0].lower()
            else:
                # Handle "email@domain.com" format
                return sender.split('@')[0].lower()
        except (IndexError, AttributeError):
            return ""
    
    def parse_email_content(self, email_data: Dict) -> str:
        """
        Parse email content and extract clean text.
        
        Args:
            email_data: Dictionary containing email content
            
        Returns:
            str: Clean text content
        """
        html_content = email_data.get('html_content', '')
        text_content = email_data.get('text_content', '')
        
        if html_content:
            return self._extract_text_from_html(html_content)
        else:
            return text_content
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content, preserving links as markdown [text](url)."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Replace <a> tags with markdown links
            for a in soup.find_all('a'):
                href = a.get('href')
                text = a.get_text(strip=True)
                if href and text:
                    markdown_link = f'[{text}]({href})'
                    a.replace_with(markdown_link)
                elif href:
                    a.replace_with(href)
                else:
                    a.unwrap()

            # Extract text
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error("Failed to parse HTML content", error=str(e))
            return ""
    
    def process_newsletters(self, emails: List[Dict]) -> List[Newsletter]:
        """
        Process a list of emails and return newsletters.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List[Newsletter]: Processed newsletters
        """
        newsletters = []
        
        for email_data in emails:
            try:
                if self.is_newsletter(email_data):
                    newsletter = Newsletter(
                        sender=email_data.get('sender', ''),
                        subject=email_data.get('subject', ''),
                        date=email_data.get('date', datetime.now()),
                        content=self.parse_email_content(email_data),
                        html_content=email_data.get('html_content', ''),
                        is_newsletter=True,
                        source_domain=self._extract_domain(email_data.get('sender', ''))
                    )
                    newsletters.append(newsletter)
                    
            except Exception as e:
                logger.error("Failed to process email", 
                           sender=email_data.get('sender', ''),
                           subject=email_data.get('subject', ''),
                           error=str(e))
        
        logger.info(f"Processed {len(newsletters)} newsletters from {len(emails)} emails")
        return newsletters
    
    def filter_by_date_range(self, newsletters: List[Newsletter], 
                           days_back: int = 7) -> List[Newsletter]:
        """
        Filter newsletters by date range.
        
        Args:
            newsletters: List of newsletters
            days_back: Number of days to look back
            
        Returns:
            List[Newsletter]: Filtered newsletters
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        filtered = [n for n in newsletters if n.date >= cutoff_date]
        
        logger.info(f"Filtered {len(filtered)} newsletters from last {days_back} days")
        return filtered 