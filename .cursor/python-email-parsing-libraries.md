# Python Email Parsing Libraries Documentation

## Overview
This documentation covers the essential Python libraries and tools for parsing, extracting, and processing email content. Python offers several powerful libraries for handling email operations from raw email text to complex MIME message parsing.

## Core Python Email Libraries

### 1. Built-in `email` Module

#### Overview
The `email` module is Python's standard library for handling email messages. It provides comprehensive support for parsing, creating, and manipulating email messages according to RFC standards.

#### Key Components
- **Parser classes**: For converting raw email text to message objects
- **Message classes**: For representing email structure
- **MIME handling**: For multipart messages and attachments
- **Header utilities**: For encoding/decoding headers

#### Basic Usage
```python
import email
from email.parser import Parser, BytesParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Parse email from string
parser = Parser()
message = parser.parsestr(email_string)

# Parse email from bytes
bytes_parser = BytesParser()
message = bytes_parser.parsebytes(email_bytes)

# Access message components
subject = message['Subject']
sender = message['From']
body_parts = message.get_payload()
```

#### Advanced Parsing
```python
import email
from email.parser import BytesParser
from email.policy import default

# Parse with modern policy (recommended for new code)
parser = BytesParser(policy=default)
message = parser.parsebytes(raw_email)

# Walk through message parts
for part in message.walk():
    content_type = part.get_content_type()
    
    if content_type == 'text/plain':
        text_content = part.get_content()
    elif content_type == 'text/html':
        html_content = part.get_content()
    elif part.get_content_disposition() == 'attachment':
        filename = part.get_filename()
        attachment_data = part.get_content()
```

### 2. `imaplib` - IMAP Client Library

#### Overview
Built-in library for connecting to IMAP servers and retrieving emails. Essential for downloading emails programmatically.

#### Basic Connection
```python
import imaplib
import email

# Connect to IMAP server
mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login('username@gmail.com', 'password')

# Select mailbox
mail.select('INBOX')

# Search for emails
status, messages = mail.search(None, 'ALL')
message_ids = messages[0].split()

# Fetch and parse emails
for msg_id in message_ids:
    status, data = mail.fetch(msg_id, '(RFC822)')
    raw_email = data[0][1]
    
    # Parse with email module
    msg = email.message_from_bytes(raw_email)
    
    # Extract information
    subject = msg['Subject']
    sender = msg['From']
    date = msg['Date']

# Close connection
mail.logout()
```

#### Advanced IMAP Operations
```python
import imaplib
from datetime import datetime, timedelta

def search_emails_by_criteria(mail, criteria):
    """Search emails with specific criteria"""
    # Date-based search
    since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
    search_criteria = f'(SINCE "{since_date}" {criteria})'
    
    status, messages = mail.search(None, search_criteria)
    return messages[0].split() if messages[0] else []

# Usage examples
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('user@gmail.com', 'password')
mail.select('INBOX')

# Find unread emails from last week
unread_recent = search_emails_by_criteria(mail, 'UNSEEN')

# Find emails with specific subject
subject_search = search_emails_by_criteria(mail, 'SUBJECT "newsletter"')

# Find emails from specific sender
sender_search = search_emails_by_criteria(mail, 'FROM "example@domain.com"')
```

## Third-Party Libraries

### 3. `imbox` - Python IMAP for Humans

#### Overview
A more user-friendly wrapper around Python's imaplib with cleaner syntax and additional features.

#### Installation
```bash
pip install imbox
```

#### Basic Usage
```python
from imbox import Imbox
from datetime import datetime, date

# Connect with context manager (automatic cleanup)
with Imbox('imap.gmail.com',
           username='username@gmail.com',
           password='password',
           ssl=True) as imbox:
    
    # Get all messages
    all_messages = imbox.messages()
    
    # Get unread messages
    unread_messages = imbox.messages(unread=True)
    
    # Get messages from specific sender
    sender_messages = imbox.messages(sent_from='newsletter@domain.com')
    
    # Get messages by date range
    recent_messages = imbox.messages(date__gt=date(2024, 1, 1))
    
    # Get messages with specific subject
    subject_messages = imbox.messages(subject='AI trends')
    
    # Process messages
    for uid, message in unread_messages:
        print(f"Subject: {message.subject}")
        print(f"From: {message.sent_from}")
        print(f"Date: {message.date}")
        print(f"Body: {message.body.plain}")
        
        # Handle attachments
        for attachment in message.attachments:
            attachment.download()
```

#### Advanced Filtering
```python
from imbox import Imbox
from datetime import datetime, timedelta

with Imbox('imap.gmail.com', username='user', password='pass', ssl=True) as imbox:
    
    # Complex date filtering
    week_ago = datetime.now() - timedelta(days=7)
    recent_newsletters = imbox.messages(
        sent_from='newsletter@domain.com',
        date__gt=week_ago.date(),
        unread=True
    )
    
    # Gmail-specific extensions
    labeled_messages = imbox.messages(
        folder='all',
        label='newsletters'
    )
    
    # Raw search queries
    attachment_messages = imbox.messages(
        folder='all',
        raw='has:attachment'
    )
```

### 4. `beautifulsoup4` - HTML Parsing

#### Overview
Essential for parsing HTML content in email bodies, especially for newsletter extraction.

#### Installation
```bash
pip install beautifulsoup4 lxml
```

#### Email HTML Parsing
```python
from bs4 import BeautifulSoup
import re

def extract_newsletter_content(html_content):
    """Extract structured content from newsletter HTML"""
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Extract links
    links = []
    for link in soup.find_all('a', href=True):
        links.append({
            'text': link.get_text().strip(),
            'url': link['href']
        })
    
    # Extract headlines (common newsletter structure)
    headlines = []
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        headlines.append(heading.get_text().strip())
    
    # Extract main content areas
    content_areas = []
    for div in soup.find_all('div', class_=re.compile(r'content|article|story')):
        text = div.get_text().strip()
        if len(text) > 50:  # Filter out short snippets
            content_areas.append(text)
    
    # Get clean text
    clean_text = soup.get_text()
    
    return {
        'links': links,
        'headlines': headlines,
        'content_areas': content_areas,
        'clean_text': clean_text
    }

# Usage with email parsing
import email
from email.parser import BytesParser

parser = BytesParser()
message = parser.parsebytes(raw_email)

for part in message.walk():
    if part.get_content_type() == 'text/html':
        html_content = part.get_content()
        extracted_data = extract_newsletter_content(html_content)
        
        print("Links found:", len(extracted_data['links']))
        print("Headlines:", extracted_data['headlines'])
```

### 5. `mailparser` - Advanced Email Parsing

#### Overview
A specialized library for advanced email parsing with support for various email formats and comprehensive metadata extraction.

#### Installation
```bash
pip install mailparser
```

#### Usage
```python
import mailparser

# Parse from file
mail = mailparser.parse_from_file('/path/to/email.eml')

# Parse from string
mail = mailparser.parse_from_string(email_string)

# Parse from bytes
mail = mailparser.parse_from_bytes(email_bytes)

# Access parsed data
print(f"Subject: {mail.subject}")
print(f"From: {mail.from_}")
print(f"To: {mail.to}")
print(f"Date: {mail.date}")
print(f"Message ID: {mail.message_id}")

# Body content
print(f"Text body: {mail.text_plain}")
print(f"HTML body: {mail.text_html}")

# Attachments
for attachment in mail.attachments:
    print(f"Attachment: {attachment['filename']}")
    print(f"Content type: {attachment['content-type']}")
    print(f"Size: {len(attachment['payload'])} bytes")

# Headers
for header, value in mail.headers.items():
    print(f"{header}: {value}")

# Raw email data
print(f"Raw email: {mail.body}")
```

## Email Content Extraction Libraries

### 6. Custom Newsletter Parser

#### Advanced Newsletter Extraction
```python
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

class NewsletterParser:
    def __init__(self):
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'ML',
            'deep learning', 'neural networks', 'GPT', 'ChatGPT',
            'automation', 'robotics', 'computer vision', 'NLP'
        ]
        
    def parse_newsletter(self, email_content):
        """Parse newsletter content and extract key information"""
        
        # Determine content type
        if isinstance(email_content, bytes):
            email_content = email_content.decode('utf-8', errors='ignore')
        
        # Check if content is HTML
        if '<html' in email_content.lower() or '<body' in email_content.lower():
            return self._parse_html_newsletter(email_content)
        else:
            return self._parse_text_newsletter(email_content)
    
    def _parse_html_newsletter(self, html_content):
        """Parse HTML newsletter content"""
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Clean up
        for element in soup(['script', 'style', 'meta', 'head']):
            element.decompose()
        
        # Extract sections
        sections = []
        
        # Look for article/story containers
        article_selectors = [
            'article', '.article', '.story', '.content-block',
            '.newsletter-item', '.post', '.entry'
        ]
        
        for selector in article_selectors:
            for element in soup.select(selector):
                section_data = self._extract_section_data(element)
                if section_data:
                    sections.append(section_data)
        
        # If no specific sections found, parse by headings
        if not sections:
            sections = self._parse_by_headings(soup)
        
        # Extract metadata
        links = self._extract_links(soup)
        ai_content = self._find_ai_content(soup.get_text())
        
        return {
            'type': 'html',
            'sections': sections,
            'links': links,
            'ai_related': ai_content,
            'total_links': len(links),
            'clean_text': soup.get_text()
        }
    
    def _parse_text_newsletter(self, text_content):
        """Parse plain text newsletter content"""
        lines = text_content.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers (various patterns)
            if self._is_section_header(line):
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'title': line,
                    'content': [],
                    'links': []
                }
            elif current_section:
                current_section['content'].append(line)
                
                # Extract URLs from line
                urls = re.findall(r'https?://[^\s<>"]+', line)
                current_section['links'].extend(urls)
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        # Process sections
        for section in sections:
            section['content'] = '\n'.join(section['content'])
        
        # Find AI-related content
        ai_content = self._find_ai_content(text_content)
        
        return {
            'type': 'text',
            'sections': sections,
            'ai_related': ai_content,
            'clean_text': text_content
        }
    
    def _extract_section_data(self, element):
        """Extract data from a section element"""
        # Find title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
        title = title_elem.get_text().strip() if title_elem else ''
        
        # Extract links
        links = []
        for link in element.find_all('a', href=True):
            links.append({
                'text': link.get_text().strip(),
                'url': link['href']
            })
        
        # Get content text
        content = element.get_text().strip()
        
        # Only return section if it has substantial content
        if len(content) > 50:
            return {
                'title': title,
                'content': content,
                'links': links
            }
        
        return None
    
    def _parse_by_headings(self, soup):
        """Parse content by heading structure"""
        sections = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            section_content = []
            
            # Collect content until next heading
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4']:
                    break
                section_content.append(sibling.get_text().strip())
            
            if section_content:
                content_text = '\n'.join(filter(None, section_content))
                
                sections.append({
                    'title': heading.get_text().strip(),
                    'content': content_text,
                    'links': self._extract_links_from_text(content_text)
                })
        
        return sections
    
    def _extract_links(self, soup):
        """Extract all links from soup"""
        links = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            text = link.get_text().strip()
            
            # Filter out unwanted links
            if not self._is_valid_link(url):
                continue
                
            links.append({
                'text': text,
                'url': url,
                'domain': urlparse(url).netloc
            })
        
        return links
    
    def _extract_links_from_text(self, text):
        """Extract URLs from plain text"""
        urls = re.findall(r'https?://[^\s<>"]+', text)
        return [{'url': url, 'domain': urlparse(url).netloc} for url in urls]
    
    def _is_valid_link(self, url):
        """Check if link is valid for newsletter analysis"""
        unwanted_domains = [
            'unsubscribe', 'mailto:', 'tel:', 'facebook.com',
            'twitter.com', 'linkedin.com', 'instagram.com'
        ]
        
        return not any(domain in url.lower() for domain in unwanted_domains)
    
    def _is_section_header(self, line):
        """Detect if line is a section header"""
        # Common patterns for newsletter section headers
        patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # ALL CAPS headers
            r'^\d+\.\s*[A-Z]',       # Numbered headers
            r'^[▶►▸]\s*',            # Bullet point headers
            r'^[-=]{3,}',            # Separator lines
            r'^\*\*.*\*\*$',         # Bold markdown
        ]
        
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _find_ai_content(self, text):
        """Find AI-related content in text"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.ai_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # Find AI-related sentences
        sentences = re.split(r'[.!?]+', text)
        ai_sentences = []
        
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in self.ai_keywords):
                ai_sentences.append(sentence.strip())
        
        return {
            'keywords': list(set(found_keywords)),
            'relevant_sentences': ai_sentences[:5],  # Limit to 5 most relevant
            'keyword_count': len(found_keywords)
        }

# Usage example
parser = NewsletterParser()

# Parse newsletter from email message
import email
message = email.message_from_string(email_string)

for part in message.walk():
    if part.get_content_type() in ['text/html', 'text/plain']:
        content = part.get_payload(decode=True)
        parsed_newsletter = parser.parse_newsletter(content)
        
        print(f"Newsletter type: {parsed_newsletter['type']}")
        print(f"Sections found: {len(parsed_newsletter['sections'])}")
        print(f"AI keywords: {parsed_newsletter['ai_related']['keywords']}")
        print(f"Total links: {parsed_newsletter.get('total_links', 0)}")
```

## Utility Functions and Helpers

### 7. Email Processing Utilities

```python
import re
import base64
import quopri
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime

class EmailUtils:
    @staticmethod
    def decode_email_header(header_value):
        """Decode email header that might be encoded"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        decoded_header = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        decoded_header += part.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        decoded_header += part.decode('utf-8', errors='ignore')
                else:
                    decoded_header += part.decode('utf-8', errors='ignore')
            else:
                decoded_header += part
        
        return decoded_header.strip()
    
    @staticmethod
    def extract_email_address(address_string):
        """Extract clean email address from address string"""
        if not address_string:
            return "", ""
        
        name, email_addr = parseaddr(address_string)
        
        # Decode name if needed
        name = EmailUtils.decode_email_header(name)
        
        return name.strip('"'), email_addr.strip()
    
    @staticmethod
    def clean_email_body(body_content):
        """Clean email body content"""
        if not body_content:
            return ""
        
        # Remove excessive whitespace
        body_content = re.sub(r'\n\s*\n', '\n\n', body_content)
        body_content = re.sub(r' +', ' ', body_content)
        
        # Remove common email artifacts
        body_content = re.sub(r'=\n', '', body_content)  # Quoted-printable line breaks
        body_content = re.sub(r'=3D', '=', body_content)  # Quoted-printable equals
        
        return body_content.strip()
    
    @staticmethod
    def extract_urls_from_text(text):
        """Extract URLs from text content"""
        url_pattern = r'https?://[^\s<>"\']+(?:[^\s<>"\'.,:;!?)])'
        urls = re.findall(url_pattern, text)
        
        # Clean URLs
        cleaned_urls = []
        for url in urls:
            # Remove trailing punctuation
            url = re.sub(r'[.,:;!?)\]]+$', '', url)
            if url:
                cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Remove duplicates
    
    @staticmethod
    def is_newsletter_email(message):
        """Determine if email is likely a newsletter"""
        indicators = [
            'unsubscribe', 'newsletter', 'digest', 'weekly', 'daily',
            'update', 'news', 'bulletin', 'magazine', 'journal'
        ]
        
        # Check subject
        subject = EmailUtils.decode_email_header(message.get('Subject', ''))
        subject_lower = subject.lower()
        
        # Check sender
        sender = EmailUtils.decode_email_header(message.get('From', ''))
        sender_lower = sender.lower()
        
        # Check for indicators in subject or sender
        for indicator in indicators:
            if indicator in subject_lower or indicator in sender_lower:
                return True
        
        # Check for list headers
        list_headers = ['List-Unsubscribe', 'List-Id', 'List-Post']
        for header in list_headers:
            if message.get(header):
                return True
        
        # Check body for unsubscribe links (basic check)
        try:
            body = str(message.get_payload())
            if 'unsubscribe' in body.lower():
                return True
        except:
            pass
        
        return False
    
    @staticmethod
    def extract_date_from_message(message):
        """Extract and parse date from email message"""
        date_header = message.get('Date')
        if not date_header:
            return None
        
        try:
            return parsedate_to_datetime(date_header)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def decode_attachment(part):
        """Decode email attachment"""
        payload = part.get_payload(decode=True)
        
        if payload:
            return {
                'filename': part.get_filename(),
                'content_type': part.get_content_type(),
                'size': len(payload),
                'content': payload
            }
        
        return None

# Usage examples
utils = EmailUtils()

# Process email message
for header_name in ['Subject', 'From', 'To']:
    header_value = message.get(header_name)
    if header_value:
        decoded_value = utils.decode_email_header(header_value)
        print(f"{header_name}: {decoded_value}")

# Extract sender info
sender_name, sender_email = utils.extract_email_address(message.get('From'))
print(f"Sender: {sender_name} <{sender_email}>")

# Check if newsletter
if utils.is_newsletter_email(message):
    print("This appears to be a newsletter")

# Extract date
email_date = utils.extract_date_from_message(message)
if email_date:
    print(f"Date: {email_date}")
```

## Performance and Best Practices

### 8. Efficient Email Processing

```python
import concurrent.futures
from typing import List, Dict, Callable
import time

class EmailBatchProcessor:
    def __init__(self, max_workers=5, rate_limit=10):
        self.max_workers = max_workers
        self.rate_limit = rate_limit  # emails per second
        self.last_process_time = 0
    
    def process_emails_batch(self, 
                           email_messages: List, 
                           process_func: Callable,
                           chunk_size: int = 50) -> List[Dict]:
        """Process emails in batches with rate limiting"""
        
        results = []
        
        # Process in chunks to manage memory
        for i in range(0, len(email_messages), chunk_size):
            chunk = email_messages[i:i + chunk_size]
            
            # Rate limiting
            self._enforce_rate_limit()
            
            # Parallel processing within chunk
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_email = {
                    executor.submit(process_func, email): email 
                    for email in chunk
                }
                
                for future in concurrent.futures.as_completed(future_to_email):
                    email = future_to_email[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as exc:
                        print(f'Email processing generated an exception: {exc}')
                        results.append(None)
            
            print(f"Processed {len(results)} emails so far...")
        
        return results
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between batches"""
        current_time = time.time()
        time_diff = current_time - self.last_process_time
        min_interval = 1.0 / self.rate_limit
        
        if time_diff < min_interval:
            time.sleep(min_interval - time_diff)
        
        self.last_process_time = time.time()

# Memory-efficient email processing
def process_large_mailbox(mailbox_messages, processor_func):
    """Process large numbers of emails efficiently"""
    
    batch_processor = EmailBatchProcessor(max_workers=3, rate_limit=5)
    
    def safe_process_email(email_data):
        try:
            return processor_func(email_data)
        except Exception as e:
            print(f"Error processing email: {e}")
            return None
    
    # Process in batches
    results = batch_processor.process_emails_batch(
        mailbox_messages,
        safe_process_email,
        chunk_size=25
    )
    
    # Filter out failed results
    valid_results = [r for r in results if r is not None]
    
    return valid_results
```

## Error Handling and Logging

### 9. Robust Email Processing

```python
import logging
from functools import wraps
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_email_operation(operation_name: str):
    """Decorator for logging email operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {operation_name}: {str(e)}")
                raise
        return wrapper
    return decorator

class EmailProcessingError(Exception):
    """Custom exception for email processing errors"""
    pass

@log_email_operation("email parsing")
def safe_parse_email(raw_email: bytes) -> Optional[object]:
    """Safely parse email with comprehensive error handling"""
    
    try:
        # Try with BytesParser first
        from email.parser import BytesParser
        from email.policy import default
        
        parser = BytesParser(policy=default)
        message = parser.parsebytes(raw_email)
        
        return message
        
    except Exception as e:
        logger.warning(f"BytesParser failed: {e}, trying fallback methods")
        
        try:
            # Fallback to basic parser
            import email
            message = email.message_from_bytes(raw_email)
            return message
            
        except Exception as e2:
            logger.error(f"All parsing methods failed: {e2}")
            
            try:
                # Last resort: try to decode and parse as string
                email_string = raw_email.decode('utf-8', errors='ignore')
                message = email.message_from_string(email_string)
                return message
                
            except Exception as e3:
                logger.error(f"Final parsing attempt failed: {e3}")
                raise EmailProcessingError(f"Could not parse email: {e3}")

@log_email_operation("content extraction")
def safe_extract_content(message) -> Dict:
    """Safely extract content from email message"""
    
    content = {
        'subject': '',
        'from': '',
        'to': '',
        'date': '',
        'body_text': '',
        'body_html': '',
        'attachments': [],
        'errors': []
    }
    
    try:
        # Extract headers safely
        content['subject'] = EmailUtils.decode_email_header(message.get('Subject', ''))
        content['from'] = EmailUtils.decode_email_header(message.get('From', ''))
        content['to'] = EmailUtils.decode_email_header(message.get('To', ''))
        content['date'] = message.get('Date', '')
        
    except Exception as e:
        content['errors'].append(f"Header extraction error: {e}")
        logger.warning(f"Header extraction failed: {e}")
    
    try:
        # Extract body content
        if message.is_multipart():
            for part in message.walk():
                try:
                    content_type = part.get_content_type()
                    
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True)
                        if body:
                            content['body_text'] = body.decode('utf-8', errors='ignore')
                    
                    elif content_type == 'text/html':
                        body = part.get_payload(decode=True)
                        if body:
                            content['body_html'] = body.decode('utf-8', errors='ignore')
                    
                    elif part.get_filename():
                        # Handle attachment
                        attachment = EmailUtils.decode_attachment(part)
                        if attachment:
                            content['attachments'].append(attachment)
                
                except Exception as e:
                    content['errors'].append(f"Part processing error: {e}")
                    logger.warning(f"Error processing email part: {e}")
        else:
            # Single part message
            try:
                payload = message.get_payload(decode=True)
                if payload:
                    decoded_payload = payload.decode('utf-8', errors='ignore')
                    if message.get_content_type() == 'text/html':
                        content['body_html'] = decoded_payload
                    else:
                        content['body_text'] = decoded_payload
            except Exception as e:
                content['errors'].append(f"Single part processing error: {e}")
                logger.warning(f"Error processing single part message: {e}")
    
    except Exception as e:
        content['errors'].append(f"Body extraction error: {e}")
        logger.error(f"Body extraction failed: {e}")
    
    return content
```

## Integration Examples

### 10. Complete Newsletter Processing Pipeline

```python
import os
from datetime import datetime, timedelta
from typing import List, Dict
import json

class NewsletterProcessor:
    def __init__(self, config: Dict):
        self.config = config
        self.parser = NewsletterParser()
        self.utils = EmailUtils()
        self.processed_count = 0
        
    def process_gmail_newsletters(self, days_back: int = 7) -> List[Dict]:
        """Complete pipeline for processing Gmail newsletters"""
        
        logger.info(f"Starting newsletter processing for last {days_back} days")
        
        # Step 1: Connect to Gmail and fetch emails
        from imbox import Imbox
        
        newsletters = []
        
        try:
            with Imbox(self.config['imap_server'],
                      username=self.config['email'],
                      password=self.config['password'],
                      ssl=True) as imbox:
                
                # Calculate date range
                since_date = datetime.now() - timedelta(days=days_back)
                
                # Search for potential newsletters
                search_queries = [
                    {'sent_from': domain, 'date__gt': since_date.date()}
                    for domain in self.config.get('newsletter_domains', [])
                ]
                
                # Add keyword-based search
                for keyword in self.config.get('keywords', []):
                    search_queries.append({
                        'subject': keyword,
                        'date__gt': since_date.date()
                    })
                
                # Fetch messages
                all_messages = []
                for query in search_queries:
                    messages = list(imbox.messages(**query))
                    all_messages.extend(messages)
                
                # Remove duplicates by message ID
                unique_messages = {}
                for uid, message in all_messages:
                    msg_id = getattr(message, 'message_id', uid)
                    if msg_id not in unique_messages:
                        unique_messages[msg_id] = (uid, message)
                
                logger.info(f"Found {len(unique_messages)} unique messages")
                
                # Step 2: Process each message
                for uid, message in unique_messages.values():
                    try:
                        processed_newsletter = self._process_single_newsletter(message)
                        if processed_newsletter:
                            newsletters.append(processed_newsletter)
                            self.processed_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing message {uid}: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Error connecting to Gmail: {e}")
            raise
        
        logger.info(f"Successfully processed {len(newsletters)} newsletters")
        return newsletters
    
    def _process_single_newsletter(self, message) -> Optional[Dict]:
        """Process a single newsletter message"""
        
        # Check if it's actually a newsletter
        if not self.utils.is_newsletter_email(message):
            return None
        
        # Extract basic metadata
        newsletter_data = {
            'subject': self.utils.decode_email_header(message.subject),
            'sender_name': '',
            'sender_email': '',
            'date': message.date,
            'content': {},
            'ai_insights': {},
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # Parse sender
        sender_name, sender_email = self.utils.extract_email_address(str(message.sent_from))
        newsletter_data['sender_name'] = sender_name
        newsletter_data['sender_email'] = sender_email
        
        # Process content
        if hasattr(message.body, 'html') and message.body.html:
            newsletter_data['content'] = self.parser.parse_newsletter(message.body.html)
        elif hasattr(message.body, 'plain') and message.body.plain:
            newsletter_data['content'] = self.parser.parse_newsletter(message.body.plain)
        else:
            logger.warning(f"No body content found for message: {newsletter_data['subject']}")
            return None
        
        # Extract AI-related insights
        newsletter_data['ai_insights'] = newsletter_data['content'].get('ai_related', {})
        
        # Add summary metrics
        newsletter_data['metrics'] = {
            'total_sections': len(newsletter_data['content'].get('sections', [])),
            'total_links': newsletter_data['content'].get('total_links', 0),
            'ai_keyword_count': newsletter_data['ai_insights'].get('keyword_count', 0),
            'has_ai_content': newsletter_data['ai_insights'].get('keyword_count', 0) > 0
        }
        
        return newsletter_data
    
    def save_results(self, newsletters: List[Dict], output_file: str):
        """Save processed newsletters to file"""
        
        output_data = {
            'processing_date': datetime.now().isoformat(),
            'total_newsletters': len(newsletters),
            'newsletters': newsletters,
            'summary': self._generate_summary(newsletters)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_file}")
    
    def _generate_summary(self, newsletters: List[Dict]) -> Dict:
        """Generate summary statistics"""
        
        if not newsletters:
            return {}
        
        # Count senders
        senders = {}
        ai_newsletters = 0
        total_links = 0
        
        for newsletter in newsletters:
            sender = newsletter.get('sender_email', 'Unknown')
            senders[sender] = senders.get(sender, 0) + 1
            
            if newsletter.get('metrics', {}).get('has_ai_content', False):
                ai_newsletters += 1
            
            total_links += newsletter.get('metrics', {}).get('total_links', 0)
        
        return {
            'total_newsletters': len(newsletters),
            'unique_senders': len(senders),
            'top_senders': sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5],
            'ai_related_newsletters': ai_newsletters,
            'ai_percentage': (ai_newsletters / len(newsletters)) * 100,
            'total_links_extracted': total_links,
            'average_links_per_newsletter': total_links / len(newsletters) if newsletters else 0
        }

# Configuration and usage
config = {
    'imap_server': 'imap.gmail.com',
    'email': 'your_email@gmail.com',
    'password': 'your_app_password',
    'newsletter_domains': [
        'substack.com', 'mailchimp.com', 'constantcontact.com'
    ],
    'keywords': [
        'AI', 'artificial intelligence', 'machine learning', 'newsletter'
    ]
}

# Run the processor
processor = NewsletterProcessor(config)
newsletters = processor.process_gmail_newsletters(days_back=7)
processor.save_results(newsletters, 'ai_newsletters.json')

print(f"Processed {len(newsletters)} newsletters")
```

## Resources and Documentation

### Official Documentation
- [Python email module](https://docs.python.org/3/library/email.html)
- [imaplib documentation](https://docs.python.org/3/library/imaplib.html)
- [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### Third-Party Libraries
- [imbox on GitHub](https://github.com/martinrusev/imbox)
- [mailparser documentation](https://pypi.org/project/mailparser/)

### Email Standards
- [RFC 5322 - Email Message Format](https://tools.ietf.org/html/rfc5322)
- [RFC 2047 - MIME Header Encoding](https://tools.ietf.org/html/rfc2047)
- [RFC 2045 - MIME Part One](https://tools.ietf.org/html/rfc2045)

### Best Practices
- Always use context managers for IMAP connections
- Implement proper error handling and logging
- Use rate limiting to avoid server restrictions
- Cache parsed results when possible
- Consider memory usage for large email processing
- Test with various email formats and encodings 