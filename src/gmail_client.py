"""
Gmail Client Module

Handles Gmail API authentication and email retrieval operations.
"""

import os
import base64
import email
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import structlog


logger = structlog.get_logger(__name__)


class GmailClient:
    """Handles Gmail API operations for newsletter retrieval."""
    
    # Gmail API scopes - we only need read access
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: str = 'config/credentials.json', 
                 token_path: str = 'config/token.json'):
        """Initialize Gmail client with authentication."""
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(Request())
                else:
                    logger.info("Starting OAuth2 flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            self.authenticated = True
            
            logger.info("Gmail API authentication successful")
            return True
            
        except Exception as e:
            logger.error("Gmail authentication failed", error=str(e))
            return False
    
    def search_emails(self, query: str, max_results: int = 500) -> List[Dict]:
        """
        Search emails using Gmail query syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of emails to return
            
        Returns:
            List[Dict]: List of email data dictionaries
        """
        if not self.authenticated:
            raise RuntimeError("Gmail client not authenticated")
        
        try:
            logger.info(f"Searching emails with query: {query}")
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages matching query")
            
            # Get full message details
            emails = []
            for message in messages:
                email_data = self._get_message_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Successfully retrieved {len(emails)} email details")
            return emails
            
        except HttpError as e:
            logger.error("Gmail API error", error=str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error in email search", error=str(e))
            return []
    
    def get_newsletters_last_days(self, days: int = 30) -> List[Dict]:
        """
        Get potential newsletters from the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List[Dict]: Email data for potential newsletters
        """
        # Build query for newsletter-like emails
        newsletter_query = f"""
        newer_than:{days}d AND (
            from:newsletter OR 
            from:digest OR 
            from:noreply OR 
            from:no-reply OR
            subject:newsletter OR 
            subject:digest OR 
            subject:"weekly" OR 
            subject:"daily" OR
            subject:"AI" OR
            subject:"artificial intelligence" OR
            subject:"machine learning" OR
            subject:"tech" OR
            unsubscribe
        )
        """.replace('\n', ' ').strip()
        
        return self.search_emails(newsletter_query)
    
    def _get_message_details(self, message_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dict: Message details or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {}
            for header in message['payload'].get('headers', []):
                headers[header['name'].lower()] = header['value']
            
            # Extract body content
            body_text, body_html = self._extract_body(message['payload'])
            
            # Parse date
            date_str = headers.get('date', '')
            try:
                # Parse email date format
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except:
                date = datetime.now()
            
            return {
                'id': message_id,
                'sender': headers.get('from', ''),
                'subject': headers.get('subject', ''),
                'date': date,
                'text_content': body_text,
                'html_content': body_html,
                'labels': message.get('labelIds', []),
                'thread_id': message.get('threadId', ''),
                'headers': headers
            }
            
        except Exception as e:
            logger.error(f"Failed to get message details for {message_id}", error=str(e))
            return None
    
    def _extract_body(self, payload: Dict) -> tuple:
        """
        Extract text and HTML body from message payload.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            tuple: (text_content, html_content)
        """
        text_content = ""
        html_content = ""
        
        def extract_from_part(part):
            nonlocal text_content, html_content
            
            mime_type = part.get('mimeType', '')
            body = part.get('body', {})
            
            if body.get('data'):
                content = base64.urlsafe_b64decode(body['data']).decode('utf-8', errors='ignore')
                
                if mime_type == 'text/plain':
                    text_content += content
                elif mime_type == 'text/html':
                    html_content += content
            
            # Handle multipart messages
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_from_part(subpart)
        
        extract_from_part(payload)
        return text_content, html_content
    
    def analyze_senders(self, emails: List[Dict]) -> Dict[str, int]:
        """
        Analyze email senders to identify newsletter sources.
        
        Args:
            emails: List of email data
            
        Returns:
            Dict: Sender email counts
        """
        sender_counts = {}
        
        for email_data in emails:
            sender = email_data.get('sender', '').lower()
            
            # Extract email address from "Name <email@domain.com>" format
            if '<' in sender and '>' in sender:
                sender = sender.split('<')[1].split('>')[0]
            
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        # Sort by frequency
        return dict(sorted(sender_counts.items(), key=lambda x: x[1], reverse=True))
    
    def get_user_profile(self) -> Dict:
        """Get Gmail user profile information."""
        if not self.authenticated:
            raise RuntimeError("Gmail client not authenticated")
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress', ''),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0),
                'history_id': profile.get('historyId', '')
            }
        except Exception as e:
            logger.error("Failed to get user profile", error=str(e))
            return {}
