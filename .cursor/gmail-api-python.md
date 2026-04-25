# Gmail API Python Documentation

## Overview
Gmail API allows developers to programmatically access Gmail mailboxes and perform actions like reading, sending, deleting, and organizing emails. This documentation covers Python implementation using the official Google API client library.

## Prerequisites

### Requirements
- Python 3.7 or higher
- A Google account with Gmail enabled
- Google Cloud Project
- OAuth 2.0 credentials

### Dependencies
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install beautifulsoup4  # For HTML email parsing
```

## Google Cloud Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or use existing project
3. Enter project name and click "Create"

### 2. Enable Gmail API
1. Navigate to "APIs and Services" > "Library"
2. Search for "Gmail API"
3. Click on Gmail API and press "Enable"

### 3. Configure OAuth Consent Screen
1. Go to "APIs and Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill required information:
   - App name: Your application name
   - User support email: Your email
   - Developer contact email: Your email
4. In "Scopes" step, add Gmail scopes if needed
5. Add test users (email addresses that can use the API)
6. Complete the setup

### 4. Create OAuth Credentials
1. Go to "APIs and Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as application type
4. Enter a name for the credential
5. Download the JSON file and rename it to `credentials.json`

## Authentication Implementation

### Basic Authentication Setup
```python
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes determine what permissions your app requests
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',   # Modify emails
    'https://www.googleapis.com/auth/gmail.send'      # Send emails
]

def gmail_authenticate():
    """Authenticate and return Gmail API service object"""
    creds = None
    
    # token.pickle stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, get user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

# Initialize service
service = gmail_authenticate()
```

### Advanced Authentication with Environment Variables
```python
import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GmailAuth:
    def __init__(self, credentials_path=None, token_path=None):
        self.credentials_path = credentials_path or 'credentials.json'
        self.token_path = token_path or 'token.json'
        self.scopes = ['https://www.googleapis.com/auth/gmail.modify']
    
    def authenticate(self):
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path, self.scopes)
        
        # Refresh or create new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)

# Usage
auth = GmailAuth()
service = auth.authenticate()
```

## Core Operations

### 1. Searching for Emails
```python
def search_messages(service, query, max_results=100):
    """
    Search for messages using Gmail search syntax
    
    Args:
        service: Gmail API service object
        query: Gmail search query (e.g., "from:sender@example.com")
        max_results: Maximum number of messages to return
    
    Returns:
        List of message objects with id and threadId
    """
    try:
        result = service.users().messages().list(
            userId='me', 
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = result.get('messages', [])
        
        # Handle pagination for large result sets
        while 'nextPageToken' in result:
            page_token = result['nextPageToken']
            result = service.users().messages().list(
                userId='me',
                q=query,
                pageToken=page_token,
                maxResults=max_results
            ).execute()
            messages.extend(result.get('messages', []))
        
        return messages
    
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

# Example usage
newsletters = search_messages(service, "label:newsletters", max_results=50)
recent_emails = search_messages(service, "newer_than:7d")
from_specific = search_messages(service, "from:example@domain.com")
```

### 2. Reading Email Content
```python
import base64
from bs4 import BeautifulSoup

def get_message_content(service, message_id):
    """
    Get full content of an email message
    
    Args:
        service: Gmail API service object
        message_id: Gmail message ID
    
    Returns:
        Dict with message content and metadata
    """
    try:
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='full'
        ).execute()
        
        payload = message['payload']
        headers = payload.get('headers', [])
        
        # Extract basic information
        msg_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'snippet': message.get('snippet', ''),
            'date': None,
            'from': None,
            'to': None,
            'subject': None,
            'body_text': '',
            'body_html': '',
            'attachments': []
        }
        
        # Parse headers
        for header in headers:
            name = header['name'].lower()
            value = header['value']
            
            if name == 'date':
                msg_data['date'] = value
            elif name == 'from':
                msg_data['from'] = value
            elif name == 'to':
                msg_data['to'] = value
            elif name == 'subject':
                msg_data['subject'] = value
        
        # Parse body content
        msg_data.update(_parse_message_parts(service, payload, message_id))
        
        return msg_data
    
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def _parse_message_parts(service, payload, message_id):
    """Parse email body parts recursively"""
    body_text = ''
    body_html = ''
    attachments = []
    
    def _parse_parts(parts):
        nonlocal body_text, body_html, attachments
        
        for part in parts:
            mime_type = part.get('mimeType', '')
            filename = part.get('filename', '')
            
            if part.get('parts'):
                # Recursively parse nested parts
                _parse_parts(part['parts'])
            
            elif mime_type == 'text/plain':
                # Plain text content
                data = part['body'].get('data')
                if data:
                    body_text += _decode_base64(data)
            
            elif mime_type == 'text/html':
                # HTML content
                data = part['body'].get('data')
                if data:
                    body_html += _decode_base64(data)
            
            elif filename:
                # Attachment
                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    attachment = service.users().messages().attachments().get(
                        userId='me',
                        messageId=message_id,
                        id=attachment_id
                    ).execute()
                    
                    attachments.append({
                        'filename': filename,
                        'mime_type': mime_type,
                        'size': part['body'].get('size', 0),
                        'data': attachment.get('data')
                    })
    
    # Check if message has parts
    if payload.get('parts'):
        _parse_parts(payload['parts'])
    else:
        # Single part message
        mime_type = payload.get('mimeType', '')
        data = payload.get('body', {}).get('data')
        
        if data:
            if mime_type == 'text/plain':
                body_text = _decode_base64(data)
            elif mime_type == 'text/html':
                body_html = _decode_base64(data)
    
    return {
        'body_text': body_text,
        'body_html': body_html,
        'attachments': attachments
    }

def _decode_base64(data):
    """Decode base64url encoded data"""
    try:
        # Fix padding and replace URL-safe characters
        data = data.replace('-', '+').replace('_', '/')
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        
        return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return ""

def extract_text_from_html(html_content):
    """Extract plain text from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()
```

### 3. Sending Emails
```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

def send_email(service, to_email, subject, body, attachments=None):
    """
    Send an email with optional attachments
    
    Args:
        service: Gmail API service object
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
        attachments: List of file paths to attach
    
    Returns:
        Sent message object or None if failed
    """
    try:
        if attachments:
            message = MIMEMultipart()
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            for file_path in attachments:
                _add_attachment(message, file_path)
        else:
            message = MIMEText(body, 'plain')
        
        message['to'] = to_email
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()
        
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f'Message sent successfully. Message ID: {send_message["id"]}')
        return send_message
    
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def _add_attachment(message, file_path):
    """Add file attachment to message"""
    content_type, encoding = mimetypes.guess_type(file_path)
    
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    
    main_type, sub_type = content_type.split('/', 1)
    
    with open(file_path, 'rb') as fp:
        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(fp.read())
    
    encoders.encode_base64(attachment)
    filename = os.path.basename(file_path)
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename= {filename}'
    )
    
    message.attach(attachment)

def send_html_email(service, to_email, subject, html_body, text_body=None):
    """Send HTML email with optional text fallback"""
    message = MIMEMultipart('alternative')
    message['to'] = to_email
    message['subject'] = subject
    
    # Add text version if provided
    if text_body:
        text_part = MIMEText(text_body, 'plain')
        message.attach(text_part)
    
    # Add HTML version
    html_part = MIMEText(html_body, 'html')
    message.attach(html_part)
    
    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()
    
    try:
        send_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return send_message
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
```

### 4. Email Management Operations
```python
def mark_as_read(service, message_ids):
    """Mark messages as read"""
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'removeLabelIds': ['UNREAD']
            }
        ).execute()
        
        print(f'Marked {len(message_ids)} messages as read')
    except HttpError as error:
        print(f'An error occurred: {error}')

def mark_as_unread(service, message_ids):
    """Mark messages as unread"""
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': ['UNREAD']
            }
        ).execute()
        
        print(f'Marked {len(message_ids)} messages as unread')
    except HttpError as error:
        print(f'An error occurred: {error}')

def delete_messages(service, message_ids):
    """Delete messages permanently"""
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    
    try:
        service.users().messages().batchDelete(
            userId='me',
            body={'ids': message_ids}
        ).execute()
        
        print(f'Deleted {len(message_ids)} messages')
    except HttpError as error:
        print(f'An error occurred: {error}')

def trash_messages(service, message_ids):
    """Move messages to trash"""
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    
    for message_id in message_ids:
        try:
            service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
        except HttpError as error:
            print(f'Error trashing message {message_id}: {error}')
    
    print(f'Moved {len(message_ids)} messages to trash')
```

### 5. Label Management
```python
def create_label(service, label_name):
    """Create a new label"""
    label_object = {
        'name': label_name,
        'messageListVisibility': 'show',
        'labelListVisibility': 'labelShow'
    }
    
    try:
        created_label = service.users().labels().create(
            userId='me',
            body=label_object
        ).execute()
        
        print(f'Created label: {created_label["name"]} (ID: {created_label["id"]})')
        return created_label
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def list_labels(service):
    """List all labels"""
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            print(f'{label["name"]} (ID: {label["id"]})')
        
        return labels
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def add_label_to_messages(service, message_ids, label_ids):
    """Add labels to messages"""
    if not isinstance(message_ids, list):
        message_ids = [message_ids]
    if not isinstance(label_ids, list):
        label_ids = [label_ids]
    
    try:
        service.users().messages().batchModify(
            userId='me',
            body={
                'ids': message_ids,
                'addLabelIds': label_ids
            }
        ).execute()
        
        print(f'Added labels to {len(message_ids)} messages')
    except HttpError as error:
        print(f'An error occurred: {error}')
```

## Advanced Search Queries

### Gmail Search Operators
```python
# Common search patterns
SEARCH_QUERIES = {
    # Time-based searches
    'last_week': 'newer_than:7d',
    'last_month': 'newer_than:30d',
    'older_than_week': 'older_than:7d',
    'specific_date': 'after:2024/01/01 before:2024/02/01',
    
    # Sender/recipient searches
    'from_specific': 'from:example@domain.com',
    'to_specific': 'to:example@domain.com',
    'from_domain': 'from:@domain.com',
    
    # Content searches
    'subject_contains': 'subject:"specific subject"',
    'has_attachment': 'has:attachment',
    'attachment_type': 'filename:pdf',
    'body_contains': 'newsletter trending AI',
    
    # Status searches
    'unread_only': 'is:unread',
    'important_only': 'is:important',
    'starred_only': 'is:starred',
    
    # Label searches
    'specific_label': 'label:newsletters',
    'inbox_only': 'in:inbox',
    'sent_items': 'in:sent',
    
    # Combined searches
    'complex_query': 'from:newsletter@domain.com newer_than:7d has:attachment'
}

def build_newsletter_query(domains=None, keywords=None, days_back=7):
    """Build a query to find newsletters"""
    query_parts = []
    
    # Add time constraint
    query_parts.append(f'newer_than:{days_back}d')
    
    # Add domain filters
    if domains:
        domain_filters = [f'from:@{domain}' for domain in domains]
        query_parts.append(f'({" OR ".join(domain_filters)})')
    
    # Add keyword filters
    if keywords:
        keyword_filter = " OR ".join(keywords)
        query_parts.append(f'({keyword_filter})')
    
    return " ".join(query_parts)

# Example usage
newsletter_domains = ['substack.com', 'mailchimp.com', 'newsletter.com']
ai_keywords = ['AI', 'artificial intelligence', 'machine learning', 'ML', 'GPT']
query = build_newsletter_query(newsletter_domains, ai_keywords, 7)
```

## Complete Newsletter Extraction Example

### Newsletter Processing Class
```python
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class NewsletterExtractor:
    def __init__(self, service):
        self.service = service
        
    def extract_newsletters(self, days_back: int = 7, keywords: List[str] = None) -> List[Dict]:
        """Extract newsletter content from Gmail"""
        
        # Build search query
        query_parts = [f'newer_than:{days_back}d']
        
        if keywords:
            keyword_query = " OR ".join(keywords)
            query_parts.append(f'({keyword_query})')
        
        # Common newsletter patterns
        newsletter_patterns = [
            'newsletter',
            'digest',
            'weekly update',
            'daily brief',
            'trending',
            'unsubscribe'
        ]
        
        pattern_query = " OR ".join(newsletter_patterns)
        query_parts.append(f'({pattern_query})')
        
        search_query = " ".join(query_parts)
        
        # Search for messages
        messages = search_messages(self.service, search_query, max_results=500)
        print(f"Found {len(messages)} potential newsletter messages")
        
        newsletters = []
        for message in messages:
            content = get_message_content(self.service, message['id'])
            if content and self._is_newsletter(content):
                processed = self._process_newsletter(content)
                newsletters.append(processed)
        
        return newsletters
    
    def _is_newsletter(self, content: Dict) -> bool:
        """Determine if email is a newsletter"""
        # Check for newsletter indicators
        indicators = [
            'unsubscribe',
            'newsletter',
            'digest',
            'weekly',
            'daily',
            'trending',
            'update'
        ]
        
        text_content = (content.get('body_text', '') + 
                       content.get('subject', '') + 
                       content.get('from', '')).lower()
        
        # Must contain at least 2 indicators
        found_indicators = sum(1 for indicator in indicators 
                             if indicator in text_content)
        
        # Check for typical newsletter structure
        has_multiple_links = text_content.count('http') > 3
        has_sections = any(header in text_content 
                          for header in ['news', 'articles', 'stories', 'updates'])
        
        return found_indicators >= 2 or (found_indicators >= 1 and has_multiple_links)
    
    def _process_newsletter(self, content: Dict) -> Dict:
        """Process newsletter content and extract key information"""
        text_content = content.get('body_text', '')
        html_content = content.get('body_html', '')
        
        # Use HTML content if available, fallback to text
        primary_content = html_content if html_content else text_content
        
        # Extract text from HTML if needed
        if html_content and not text_content:
            text_content = extract_text_from_html(html_content)
        
        # Extract key information
        processed = {
            'id': content['id'],
            'subject': content['subject'],
            'from': content['from'],
            'date': content['date'],
            'text_content': text_content,
            'html_content': html_content,
            'links': self._extract_links(primary_content),
            'topics': self._extract_topics(text_content),
            'summary': content['snippet']
        }
        
        return processed
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract URLs from content"""
        url_pattern = r'https?://[^\s<>"]{2,}'
        urls = re.findall(url_pattern, content)
        return list(set(urls))  # Remove duplicates
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract potential topics from newsletter text"""
        # Simple keyword extraction
        ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'ML',
            'deep learning', 'neural networks', 'GPT', 'ChatGPT',
            'automation', 'robotics', 'computer vision', 'NLP',
            'data science', 'algorithms', 'tech trends'
        ]
        
        found_topics = []
        text_lower = text.lower()
        
        for keyword in ai_keywords:
            if keyword.lower() in text_lower:
                found_topics.append(keyword)
        
        return found_topics

# Usage example
def main():
    service = gmail_authenticate()
    extractor = NewsletterExtractor(service)
    
    # Extract AI-related newsletters from last 7 days
    ai_keywords = ['AI', 'artificial intelligence', 'machine learning', 'tech']
    newsletters = extractor.extract_newsletters(days_back=7, keywords=ai_keywords)
    
    print(f"Extracted {len(newsletters)} newsletters")
    
    for newsletter in newsletters:
        print(f"\nSubject: {newsletter['subject']}")
        print(f"From: {newsletter['from']}")
        print(f"Topics: {newsletter['topics']}")
        print(f"Links: {len(newsletter['links'])}")
        print(f"Summary: {newsletter['summary'][:200]}...")

if __name__ == "__main__":
    main()
```

## Error Handling and Best Practices

### Rate Limiting and Quotas
```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Decorator to rate limit API calls"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def rate_limited_get_message(service, message_id):
    """Rate-limited version of get_message_content"""
    return get_message_content(service, message_id)
```

### Robust Error Handling
```python
import time
import random
from googleapiclient.errors import HttpError

def retry_api_call(func, max_retries=3, backoff_factor=2):
    """Retry API calls with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as error:
            if error.resp.status in [429, 500, 502, 503, 504]:
                # Retryable errors
                if attempt == max_retries - 1:
                    raise
                
                wait_time = backoff_factor ** attempt + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                # Non-retryable error
                raise

def safe_batch_process(service, message_ids, process_func, batch_size=10):
    """Safely process messages in batches"""
    results = []
    
    for i in range(0, len(message_ids), batch_size):
        batch = message_ids[i:i + batch_size]
        
        for message_id in batch:
            try:
                result = retry_api_call(
                    lambda: process_func(service, message_id)
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing message {message_id}: {e}")
                continue
        
        # Pause between batches
        time.sleep(1)
    
    return results
```

## Configuration and Security

### Environment Configuration
```python
import os
from dotenv import load_dotenv

load_dotenv()

class GmailConfig:
    CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    TOKEN_PATH = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # Rate limiting
    MAX_RESULTS_PER_QUERY = int(os.getenv('GMAIL_MAX_RESULTS', '100'))
    API_CALLS_PER_SECOND = int(os.getenv('GMAIL_API_RATE_LIMIT', '10'))
    
    # Processing
    BATCH_SIZE = int(os.getenv('GMAIL_BATCH_SIZE', '10'))
    MAX_RETRIES = int(os.getenv('GMAIL_MAX_RETRIES', '3'))

# Create .env file with:
# GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
# GMAIL_TOKEN_PATH=/path/to/token.json
# GMAIL_MAX_RESULTS=100
# GMAIL_API_RATE_LIMIT=10
# GMAIL_BATCH_SIZE=10
# GMAIL_MAX_RETRIES=3
```

### Security Best Practices
```python
# 1. Store credentials securely
# - Use environment variables for paths
# - Don't commit credentials.json or token files
# - Use proper file permissions (600)

# 2. Minimize permissions
MINIMAL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# 3. Validate inputs
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# 4. Log operations
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_operations.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def logged_operation(operation_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {operation_name}: {e}")
                raise
        return wrapper
    return decorator

@logged_operation("email extraction")
def extract_emails_logged(service, query):
    return search_messages(service, query)
```

## Testing and Development

### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch
import sys
sys.path.append('.')

class TestGmailOperations(unittest.TestCase):
    
    def setUp(self):
        self.mock_service = Mock()
    
    def test_search_messages(self):
        # Mock API response
        self.mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': '123', 'threadId': '456'}]
        }
        
        messages = search_messages(self.mock_service, "test query")
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['id'], '123')
    
    def test_message_processing(self):
        # Test message content extraction
        mock_message = {
            'id': '123',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'}
                ],
                'body': {'data': 'VGVzdCBib2R5'}  # "Test body" in base64
            }
        }
        
        self.mock_service.users().messages().get().execute.return_value = mock_message
        
        content = get_message_content(self.mock_service, '123')
        
        self.assertEqual(content['subject'], 'Test Subject')
        self.assertEqual(content['from'], 'test@example.com')

if __name__ == '__main__':
    unittest.main()
```

## Resources and References

### Official Documentation
- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [Python Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail API Guides](https://developers.google.com/gmail/api/guides)

### Code Examples
- [Google Gmail API Samples](https://github.com/googleworkspace/python-samples/tree/main/gmail)
- [Gmail API Python Library](https://github.com/googleapis/google-api-python-client)

### Search Operators
- [Gmail Search Operators](https://support.google.com/mail/answer/7190?hl=en)

### Best Practices
- [Gmail API Performance Tips](https://developers.google.com/gmail/api/guides/performance)
- [Gmail API Error Handling](https://developers.google.com/gmail/api/error-codes)

## Quota and Limits

### API Quotas (as of 2024)
- **Daily Usage**: 1 billion quota units per day
- **Per-user rate limit**: 250 quota units per user per second
- **Queries per 100 seconds**: 1,000 per 100 seconds

### Quota Consumption
- **messages.list**: 5 quota units
- **messages.get**: 5 quota units  
- **messages.send**: 100 quota units
- **messages.batchModify**: 50 quota units

### Optimization Tips
1. Use batch operations when possible
2. Request only needed fields using `fields` parameter
3. Implement proper caching for frequently accessed data
4. Use appropriate `maxResults` to avoid over-fetching
5. Implement exponential backoff for rate limiting 