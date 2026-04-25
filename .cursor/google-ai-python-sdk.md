# Google AI Python SDK Documentation

## Overview
The Google AI Python SDK (google-genai) provides unified access to Google's generative AI services including Gemini models, Vertex AI, and other Google AI services. This documentation covers installation, authentication, model interaction, and advanced features for building AI-powered applications.

## Installation and Setup

### Requirements
- Python 3.9 or higher
- Google Cloud project (for Vertex AI integration)
- API credentials (API key or service account)

### Installation
```bash
# Install the Google Gen AI SDK
pip install google-genai

# For Vertex AI integration
pip install google-cloud-aiplatform

# Additional dependencies for advanced features
pip install google-cloud-storage  # For file uploads
pip install pillow              # For image processing
```

### Authentication Setup

#### Option 1: API Key (Recommended for Development)
```python
import os
from google import genai

# Set API key as environment variable
os.environ['GEMINI_API_KEY'] = 'your-api-key-here'

# Initialize client (automatically picks up API key)
client = genai.Client()
```

#### Option 2: Service Account (Recommended for Production)
```python
import os
from google import genai

# Set service account credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account.json'

# Initialize client
client = genai.Client()
```

#### Option 3: Vertex AI Authentication
```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
PROJECT_ID = "your-project-id"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)

# Create model instance
model = GenerativeModel("gemini-2.5-flash")
```

## Core Concepts

### Models Available
- **Gemini 2.5 Flash**: Fast, efficient model for most use cases
- **Gemini 2.5 Pro**: More capable model for complex tasks
- **Gemini 2.0 Flash**: Latest generation with improved capabilities
- **Text-Bison**: Legacy text generation model

### Model Capabilities
- Text generation and completion
- Image understanding and analysis
- Video processing
- Audio processing
- Code generation and execution
- Function calling
- Multimodal interactions

## Basic Usage

### Simple Text Generation
```python
from google import genai

client = genai.Client()

# Generate content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how machine learning works in simple terms"
)

print(response.text)
```

### Multimodal Input (Text + Image)
```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload an image
image_file = client.files.upload(path="path/to/image.jpg")

# Generate content with image
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(parts=[
            types.Part.from_text("What's in this image?"),
            types.Part.from_uri(image_file.uri, mime_type=image_file.mime_type)
        ])
    ]
)

print(response.text)
```

### System Instructions
```python
from google import genai
from google.genai import types

client = genai.Client()

# Create model with system instructions
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What are the latest AI trends?",
    config=types.GenerateContentConfig(
        system_instruction="You are an AI research expert who provides concise, factual summaries of AI trends based on recent developments."
    )
)

print(response.text)
```

## Advanced Configuration

### Model Parameters
```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a creative story about AI",
    config=types.GenerateContentConfig(
        temperature=0.8,          # Creativity (0.0 to 2.0)
        top_p=0.95,              # Nucleus sampling
        top_k=40,                # Top-k sampling
        max_output_tokens=1024,   # Response length
        candidate_count=1,        # Number of responses
        stop_sequences=["END"]    # Stop generation at these sequences
    )
)

print(response.text)
```

### Safety Settings
```python
from google import genai
from google.genai import types

client = genai.Client()

# Configure safety settings
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    )
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your content here",
    config=types.GenerateContentConfig(
        safety_settings=safety_settings
    )
)
```

### Thinking Configuration
```python
from google import genai
from google.genai import types

client = genai.Client()

# Enable/disable thinking for Gemini 2.5 models
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Solve this complex problem step by step",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=1000  # Set to 0 to disable thinking
        )
    )
)

print(response.text)
```

## Chat and Conversations

### Multi-turn Chat
```python
from google import genai
from google.genai import types

client = genai.Client()

# Initialize chat
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful AI assistant."
    )
)

# Send messages
response1 = chat.send_message("Hello! I'm working on a Python project.")
print("Assistant:", response1.text)

response2 = chat.send_message("Can you help me with error handling?")
print("Assistant:", response2.text)

response3 = chat.send_message("Show me an example of try-catch blocks.")
print("Assistant:", response3.text)

# Get chat history
for message in chat.history:
    print(f"{message.role}: {message.parts[0].text}")
```

### Streaming Responses
```python
from google import genai
from google.genai import types

client = genai.Client()

# Stream content generation
stream = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a detailed explanation of neural networks"
)

print("Streaming response:")
for chunk in stream:
    if chunk.text:
        print(chunk.text, end='', flush=True)
print()  # New line at the end
```

## Function Calling

### Define Functions
```python
from google import genai
from google.genai import types
import json

client = genai.Client()

# Define function schema
get_weather_function = types.FunctionDeclaration(
    name="get_weather",
    description="Get current weather for a location",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "location": types.Schema(
                type=types.Type.STRING,
                description="City and state, e.g. San Francisco, CA"
            ),
            "unit": types.Schema(
                type=types.Type.STRING,
                enum=["celsius", "fahrenheit"],
                description="Temperature unit"
            )
        },
        required=["location"]
    )
)

# Create tool
weather_tool = types.Tool(function_declarations=[get_weather_function])

# Generate content with function calling
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="What's the weather like in New York?",
    config=types.GenerateContentConfig(
        tools=[weather_tool],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=types.FunctionCallingConfig.Mode.AUTO
            )
        )
    )
)

# Check if function was called
if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function called: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    
    # Execute function (implement your weather API here)
    weather_data = {"temperature": "72°F", "condition": "Sunny"}
    
    # Send function response back
    function_response = types.Content(parts=[
        types.Part.from_function_response(
            name=function_call.name,
            response=weather_data
        )
    ])
    
    final_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(parts=[types.Part.from_text("What's the weather like in New York?")]),
            response.candidates[0].content,
            function_response
        ]
    )
    
    print("Final response:", final_response.text)
```

### Advanced Function Calling with Multiple Tools
```python
from google import genai
from google.genai import types

client = genai.Client()

# Define multiple functions
functions = [
    types.FunctionDeclaration(
        name="search_emails",
        description="Search emails by query and date range",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "query": types.Schema(type=types.Type.STRING, description="Search query"),
                "days_back": types.Schema(type=types.Type.INTEGER, description="Days to search back"),
                "sender": types.Schema(type=types.Type.STRING, description="Filter by sender email")
            },
            required=["query"]
        )
    ),
    types.FunctionDeclaration(
        name="summarize_content",
        description="Summarize text content",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "text": types.Schema(type=types.Type.STRING, description="Text to summarize"),
                "max_sentences": types.Schema(type=types.Type.INTEGER, description="Maximum sentences in summary")
            },
            required=["text"]
        )
    )
]

# Create tool
email_tool = types.Tool(function_declarations=functions)

# Use in conversation
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Search for emails about AI trends from the last week and summarize them",
    config=types.GenerateContentConfig(
        tools=[email_tool]
    )
)

print(response.text)
```

## File Handling

### Upload and Process Files
```python
from google import genai
from google.genai import types

client = genai.Client()

# Upload a document
document_file = client.files.upload(
    path="path/to/document.pdf",
    mime_type="application/pdf"
)

print(f"Uploaded file: {document_file.uri}")

# Process the document
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(parts=[
            types.Part.from_text("Summarize the key points from this document"),
            types.Part.from_uri(document_file.uri, mime_type=document_file.mime_type)
        ])
    ]
)

print(response.text)

# List uploaded files
files = client.files.list()
for file in files:
    print(f"File: {file.name}, URI: {file.uri}")

# Delete file when done
client.files.delete(name=document_file.name)
```

### Batch Processing
```python
from google import genai
from google.genai import types
import asyncio

client = genai.Client()

async def process_multiple_documents(file_paths):
    """Process multiple documents in parallel"""
    
    # Upload files
    upload_tasks = []
    for path in file_paths:
        upload_tasks.append(
            client.files.upload_async(path=path, mime_type="application/pdf")
        )
    
    uploaded_files = await asyncio.gather(*upload_tasks)
    
    # Process files
    process_tasks = []
    for file in uploaded_files:
        task = client.models.generate_content_async(
            model="gemini-2.5-flash",
            contents=[
                types.Content(parts=[
                    types.Part.from_text("Extract key information from this document"),
                    types.Part.from_uri(file.uri, mime_type=file.mime_type)
                ])
            ]
        )
        process_tasks.append(task)
    
    results = await asyncio.gather(*process_tasks)
    
    # Clean up
    for file in uploaded_files:
        await client.files.delete_async(name=file.name)
    
    return [result.text for result in results]

# Usage
file_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
summaries = asyncio.run(process_multiple_documents(file_paths))

for i, summary in enumerate(summaries):
    print(f"Document {i+1} summary: {summary[:200]}...")
```

## Context Caching

### Creating and Using Cached Context
```python
from google import genai
from google.genai import types

client = genai.Client()

# Create a cache for frequently used context
large_document = "Your large document content here..."

cached_content = client.caches.create(
    model="gemini-2.5-flash-001",  # Must use versioned model
    contents=[
        types.Content(parts=[types.Part.from_text(large_document)])
    ],
    ttl="3600s"  # Cache for 1 hour
)

print(f"Cache created: {cached_content.name}")

# Use cached context
response = client.models.generate_content(
    model="gemini-2.5-flash-001",
    contents="What are the main themes in this document?",
    config=types.GenerateContentConfig(
        cached_content=cached_content.name
    )
)

print(response.text)

# List caches
caches = client.caches.list()
for cache in caches:
    print(f"Cache: {cache.name}, Expires: {cache.expire_time}")

# Delete cache
client.caches.delete(name=cached_content.name)
```

## Token Management

### Count Tokens
```python
from google import genai
from google.genai import types

client = genai.Client()

# Count tokens in content
content = "This is a sample text for token counting"

token_count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=content
)

print(f"Input tokens: {token_count.total_tokens}")

# Count tokens for multimodal content
image_file = client.files.upload(path="image.jpg")

multimodal_count = client.models.count_tokens(
    model="gemini-2.5-flash",
    contents=[
        types.Content(parts=[
            types.Part.from_text("Describe this image"),
            types.Part.from_uri(image_file.uri, mime_type=image_file.mime_type)
        ])
    ]
)

print(f"Multimodal tokens: {multimodal_count.total_tokens}")
```

### Compute Tokens (Billing Information)
```python
from google import genai

client = genai.Client()

# Get compute token usage for billing
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate a detailed report on AI trends"
)

if hasattr(response, 'usage_metadata'):
    usage = response.usage_metadata
    print(f"Prompt tokens: {usage.prompt_token_count}")
    print(f"Completion tokens: {usage.candidates_token_count}")
    print(f"Total tokens: {usage.total_token_count}")
```

## Embeddings

### Text Embeddings
```python
from google import genai
from google.genai import types

client = genai.Client()

# Generate text embeddings
text = "Artificial intelligence is transforming industries"

embedding_response = client.models.embed_content(
    model="text-embedding-004",
    content=text,
    task_type=types.TaskType.RETRIEVAL_DOCUMENT,
    title="AI Industry Impact"
)

embedding_vector = embedding_response.embedding.values
print(f"Embedding dimension: {len(embedding_vector)}")
print(f"First 5 values: {embedding_vector[:5]}")

# Batch embeddings
texts = [
    "Machine learning algorithms",
    "Neural network architectures", 
    "Natural language processing",
    "Computer vision applications"
]

batch_response = client.models.embed_content(
    model="text-embedding-004",
    content=texts,
    task_type=types.TaskType.RETRIEVAL_DOCUMENT
)

for i, embedding in enumerate(batch_response.embedding):
    print(f"Text {i+1} embedding dimension: {len(embedding.values)}")
```

### Similarity Search
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_texts(query_text, candidate_texts, client):
    """Find most similar texts using embeddings"""
    
    # Get query embedding
    query_response = client.models.embed_content(
        model="text-embedding-004",
        content=query_text,
        task_type=types.TaskType.RETRIEVAL_QUERY
    )
    query_embedding = np.array(query_response.embedding.values).reshape(1, -1)
    
    # Get candidate embeddings
    candidate_response = client.models.embed_content(
        model="text-embedding-004",
        content=candidate_texts,
        task_type=types.TaskType.RETRIEVAL_DOCUMENT
    )
    
    candidate_embeddings = np.array([
        emb.values for emb in candidate_response.embedding
    ])
    
    # Calculate similarities
    similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
    
    # Sort by similarity
    results = []
    for i, similarity in enumerate(similarities):
        results.append({
            'text': candidate_texts[i],
            'similarity': similarity
        })
    
    return sorted(results, key=lambda x: x['similarity'], reverse=True)

# Usage
client = genai.Client()
query = "machine learning applications"
candidates = [
    "Deep learning for image recognition",
    "Natural language processing with transformers",
    "Reinforcement learning in robotics",
    "Classical statistics and data analysis"
]

similar_texts = find_similar_texts(query, candidates, client)
for result in similar_texts:
    print(f"Similarity: {result['similarity']:.3f} - {result['text']}")
```

## Error Handling and Best Practices

### Robust Error Handling
```python
from google import genai
from google.genai import types
import time
import random

class GeminiAPIHandler:
    def __init__(self, api_key=None):
        self.client = genai.Client(api_key=api_key)
        self.max_retries = 3
        self.base_delay = 1
    
    def generate_content_with_retry(self, model, contents, config=None):
        """Generate content with exponential backoff retry"""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
                return response
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Handle specific errors
                if "quota" in str(e).lower():
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Quota exceeded, retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                elif "rate" in str(e).lower():
                    delay = self.base_delay * (2 ** attempt)
                    print(f"Rate limit hit, retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    print(f"Unexpected error: {e}")
                    raise e
    
    def safe_generate(self, prompt, model="gemini-2.5-flash"):
        """Safely generate content with error handling"""
        
        try:
            response = self.generate_content_with_retry(
                model=model,
                contents=prompt
            )
            
            # Check for safety issues
            if response.candidates[0].finish_reason == types.FinishReason.SAFETY:
                return "Content was blocked due to safety filters"
            
            return response.text
            
        except Exception as e:
            return f"Error generating content: {str(e)}"

# Usage
handler = GeminiAPIHandler()

# Safe content generation
result = handler.safe_generate("Explain quantum computing")
print(result)
```

### Rate Limiting and Batch Processing
```python
import asyncio
import time
from typing import List, Dict

class BatchProcessor:
    def __init__(self, client, requests_per_minute=60):
        self.client = client
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
    
    async def rate_limited_request(self, model, contents, config=None):
        """Make rate-limited request"""
        
        # Ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        
        response = await self.client.models.generate_content_async(
            model=model,
            contents=contents,
            config=config
        )
        
        self.last_request_time = time.time()
        return response
    
    async def process_batch(self, requests: List[Dict]) -> List[str]:
        """Process a batch of requests with rate limiting"""
        
        results = []
        
        for i, request in enumerate(requests):
            try:
                print(f"Processing request {i+1}/{len(requests)}")
                
                response = await self.rate_limited_request(
                    model=request.get('model', 'gemini-2.5-flash'),
                    contents=request['contents'],
                    config=request.get('config')
                )
                
                results.append(response.text)
                
            except Exception as e:
                print(f"Error processing request {i+1}: {e}")
                results.append(f"Error: {str(e)}")
        
        return results

# Usage
async def main():
    client = genai.Client()
    processor = BatchProcessor(client, requests_per_minute=30)
    
    requests = [
        {'contents': 'Explain machine learning'},
        {'contents': 'What is artificial intelligence?'},
        {'contents': 'How do neural networks work?'}
    ]
    
    results = await processor.process_batch(requests)
    
    for i, result in enumerate(results):
        print(f"Result {i+1}: {result[:100]}...")

# Run batch processing
asyncio.run(main())
```

## Newsletter Processing Application

### Complete Newsletter Analysis System
```python
from google import genai
from google.genai import types
import json
import re
from datetime import datetime
from typing import List, Dict

class NewsletterAnalyzer:
    def __init__(self, api_key=None):
        self.client = genai.Client(api_key=api_key)
        self.ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'ML',
            'deep learning', 'neural networks', 'GPT', 'ChatGPT',
            'automation', 'robotics', 'computer vision', 'NLP'
        ]
    
    def extract_newsletter_structure(self, content: str) -> Dict:
        """Extract structure from newsletter content"""
        
        prompt = f"""
        Analyze this newsletter content and extract the following information in JSON format:
        
        1. Main topics/sections
        2. Key headlines or titles
        3. Important URLs or links mentioned
        4. Company/organization names mentioned
        5. Product names or announcements
        6. Any AI-related content specifically
        
        Newsletter content:
        {content[:4000]}  # Limit content to avoid token limits
        
        Return only valid JSON with these fields:
        - topics: list of main topics
        - headlines: list of key headlines
        - urls: list of URLs found
        - companies: list of company names
        - products: list of product names
        - ai_content: list of AI-related mentions
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,  # Low temperature for consistent output
                response_mime_type="application/json"
            )
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return self._fallback_extraction(content)
    
    def _fallback_extraction(self, content: str) -> Dict:
        """Fallback extraction using regex patterns"""
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s<>"]+', content)
        
        # Find AI keywords
        ai_mentions = []
        for keyword in self.ai_keywords:
            if keyword.lower() in content.lower():
                ai_mentions.append(keyword)
        
        return {
            'topics': ['Content analysis available'],
            'headlines': ['Manual extraction needed'],
            'urls': urls[:10],  # Limit to first 10 URLs
            'companies': [],
            'products': [],
            'ai_content': ai_mentions
        }
    
    def generate_summary(self, newsletters: List[Dict]) -> str:
        """Generate a comprehensive summary of multiple newsletters"""
        
        # Prepare content for summarization
        newsletter_summaries = []
        
        for newsletter in newsletters:
            summary = f"""
            Newsletter: {newsletter.get('subject', 'Unknown')}
            From: {newsletter.get('sender', 'Unknown')}
            AI Topics: {', '.join(newsletter.get('analysis', {}).get('ai_content', []))}
            Key Headlines: {', '.join(newsletter.get('analysis', {}).get('headlines', [])[:3])}
            """
            newsletter_summaries.append(summary)
        
        combined_content = '\n---\n'.join(newsletter_summaries)
        
        prompt = f"""
        Based on the following newsletter summaries, create a comprehensive report about current AI trends:
        
        {combined_content}
        
        Please provide:
        1. **Key AI Trends**: Top 5 emerging trends mentioned across newsletters
        2. **Important Companies**: Companies frequently mentioned in AI context
        3. **Product Announcements**: New AI products or features announced
        4. **Industry Impact**: How these trends might impact different industries
        5. **Recommendations**: Actionable insights for staying current with AI developments
        
        Format the response in markdown with clear sections.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048
            )
        )
        
        return response.text
    
    def analyze_newsletter(self, newsletter_data: Dict) -> Dict:
        """Analyze a single newsletter"""
        
        content = newsletter_data.get('content', '')
        
        # Extract structure
        analysis = self.extract_newsletter_structure(content)
        
        # Calculate relevance score
        ai_score = len(analysis.get('ai_content', []))
        relevance_score = min(ai_score * 10, 100)  # Cap at 100
        
        return {
            'newsletter_id': newsletter_data.get('id'),
            'subject': newsletter_data.get('subject'),
            'sender': newsletter_data.get('sender'),
            'analysis': analysis,
            'ai_relevance_score': relevance_score,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def process_newsletter_batch(self, newsletters: List[Dict]) -> Dict:
        """Process multiple newsletters and generate insights"""
        
        analyzed_newsletters = []
        
        for newsletter in newsletters:
            try:
                analysis = self.analyze_newsletter(newsletter)
                analyzed_newsletters.append(analysis)
                print(f"Analyzed: {analysis['subject'][:50]}...")
                
            except Exception as e:
                print(f"Error analyzing newsletter: {e}")
                continue
        
        # Generate comprehensive summary
        summary = self.generate_summary(analyzed_newsletters)
        
        # Calculate statistics
        total_newsletters = len(analyzed_newsletters)
        ai_relevant = [n for n in analyzed_newsletters if n['ai_relevance_score'] > 20]
        avg_relevance = sum(n['ai_relevance_score'] for n in analyzed_newsletters) / total_newsletters if total_newsletters > 0 else 0
        
        return {
            'summary': summary,
            'newsletters': analyzed_newsletters,
            'statistics': {
                'total_processed': total_newsletters,
                'ai_relevant_count': len(ai_relevant),
                'average_relevance_score': round(avg_relevance, 2),
                'top_ai_newsletters': sorted(
                    analyzed_newsletters, 
                    key=lambda x: x['ai_relevance_score'], 
                    reverse=True
                )[:5]
            },
            'generated_at': datetime.now().isoformat()
        }

# Usage example
def main():
    # Initialize analyzer
    analyzer = NewsletterAnalyzer()
    
    # Sample newsletter data (would come from email processing)
    sample_newsletters = [
        {
            'id': '1',
            'subject': 'AI Weekly: Latest in Machine Learning',
            'sender': 'ai-newsletter@example.com',
            'content': 'This week in AI: OpenAI releases GPT-4 updates, Google announces new AI features...'
        },
        {
            'id': '2', 
            'subject': 'Tech Trends Digest',
            'sender': 'tech@digest.com',
            'content': 'Deep learning breakthroughs, autonomous vehicles progress, neural network optimization...'
        }
    ]
    
    # Process newsletters
    results = analyzer.process_newsletter_batch(sample_newsletters)
    
    # Save results
    with open('ai_trends_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("AI Trends Summary:")
    print("=" * 50)
    print(results['summary'])
    
    print("\nStatistics:")
    print(f"Total newsletters: {results['statistics']['total_processed']}")
    print(f"AI relevant: {results['statistics']['ai_relevant_count']}")
    print(f"Average relevance: {results['statistics']['average_relevance_score']}")

if __name__ == "__main__":
    main()
```

## Production Deployment

### Environment Configuration
```python
import os
from google import genai
from google.genai import types

class ProductionGeminiClient:
    def __init__(self):
        # Load configuration from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.region = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
        
        # Initialize client
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # Default configuration
        self.default_config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=1024,
            top_p=0.95,
            top_k=40
        )
    
    def health_check(self) -> bool:
        """Check if the service is healthy"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Hello",
                config=types.GenerateContentConfig(max_output_tokens=10)
            )
            return len(response.text) > 0
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            models = self.client.models.list()
            return [model.name for model in models]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

# Create production client
def create_production_client():
    """Factory function for production client"""
    return ProductionGeminiClient()
```

### Monitoring and Logging
```python
import logging
import time
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gemini_api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def monitor_api_calls(func):
    """Decorator to monitor API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(f"API call {func.__name__} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API call {func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

class MonitoredGeminiClient:
    def __init__(self):
        self.client = genai.Client()
    
    @monitor_api_calls
    def generate_content(self, model, contents, config=None):
        """Generate content with monitoring"""
        return self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    
    @monitor_api_calls
    def generate_content_stream(self, model, contents, config=None):
        """Generate streaming content with monitoring"""
        return self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config
        )
```

## Resources and References

### Official Documentation
- [Google AI Platform Documentation](https://ai.google.dev/)
- [Gemini API Reference](https://ai.google.dev/api)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

### Model Information
- [Gemini Model Overview](https://ai.google.dev/models/gemini)
- [Model Pricing](https://ai.google.dev/pricing)
- [Rate Limits and Quotas](https://ai.google.dev/docs/rate_limits)

### Best Practices
- [Prompt Engineering Guide](https://ai.google.dev/docs/prompt_intro)
- [Safety and Responsible AI](https://ai.google.dev/docs/safety_setting_gemini)
- [Function Calling Best Practices](https://ai.google.dev/docs/function_calling)

### Code Examples
- [Google AI Cookbook](https://github.com/google-gemini/cookbook)
- [Generative AI Samples](https://github.com/GoogleCloudPlatform/generative-ai)

### Support and Community
- [Google AI Forum](https://discuss.ai.google.dev/)
- [Stack Overflow (google-gemini tag)](https://stackoverflow.com/questions/tagged/google-gemini)
- [GitHub Issues](https://github.com/google/generative-ai-python/issues)

## Troubleshooting

### Common Issues

#### Authentication Errors
```python
# Check API key
import os
print("API Key set:", bool(os.getenv('GEMINI_API_KEY')))

# Test authentication
try:
    client = genai.Client()
    models = client.models.list()
    print("Authentication successful")
except Exception as e:
    print(f"Authentication failed: {e}")
```

#### Rate Limiting
```python
# Handle rate limits gracefully
import time
import random

def with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "rate" in str(e).lower() and attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            raise e
```

#### Memory Management
```python
# For large batch processing
import gc

def process_large_batch(items, batch_size=10):
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
        
        # Clean up memory
        gc.collect()
    
    return results
```

### Performance Optimization

#### Async Processing
```python
import asyncio
from typing import List

async def process_concurrent_requests(requests: List[str], max_concurrent=5):
    """Process multiple requests concurrently with rate limiting"""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single(request):
        async with semaphore:
            response = await client.models.generate_content_async(
                model="gemini-2.5-flash",
                contents=request
            )
            return response.text
    
    tasks = [process_single(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

#### Caching Strategies
```python
from functools import lru_cache
import hashlib

class CachedGeminiClient:
    def __init__(self):
        self.client = genai.Client()
        self._cache = {}
    
    def _get_cache_key(self, model, contents, config):
        """Generate cache key for request"""
        content_str = str(contents) + str(config)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def generate_content_cached(self, model, contents, config=None, use_cache=True):
        """Generate content with caching"""
        
        if not use_cache:
            return self.client.models.generate_content(
                model=model, contents=contents, config=config
            )
        
        cache_key = self._get_cache_key(model, contents, config)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        response = self.client.models.generate_content(
            model=model, contents=contents, config=config
        )
        
        self._cache[cache_key] = response
        return response
```

This comprehensive documentation covers the Google AI Python SDK from basic setup to advanced production deployment, providing practical examples for building AI-powered applications with Gemini models. 