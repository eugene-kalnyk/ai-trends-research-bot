# Google Gemini API Documentation

## Overview
Google Gemini is a family of multimodal AI models that can process text, images, audio, and video. The latest Gemini 2.0 models offer significant improvements in speed, quality, and capabilities, making them ideal for building AI-powered applications.

## Available Models

### Gemini 2.0 Flash (Recommended)
- **Status**: Generally Available
- **Context Window**: 1 million tokens
- **Features**: Native tool use, multimodal input, text output
- **Pricing**: $0.10/M input tokens, $0.40/M output tokens
- **Use Cases**: General purpose, coding, complex instruction following

### Gemini 2.0 Flash-Lite
- **Status**: Public Preview
- **Features**: Cost-optimized for large scale text output
- **Use Cases**: High-volume text generation, cost-sensitive applications

### Gemini 2.0 Pro
- **Status**: Experimental
- **Features**: Best model for coding and complex prompts
- **Use Cases**: Advanced coding tasks, complex reasoning

### Gemini 2.0 Flash Thinking Experimental
- **Features**: Reasoning before answering
- **Use Cases**: Complex problem-solving, multi-step reasoning

## API Access Options

### 1. Google AI Studio
- Web-based interface for testing and prototyping
- Free tier available
- Direct API access
- URL: https://ai.google.dev/

### 2. Vertex AI
- Enterprise-grade platform
- Advanced features and integrations
- Better for production deployments
- URL: https://cloud.google.com/vertex-ai

### 3. OpenRouter (Third-party)
- Unified API for multiple models
- OpenAI-compatible endpoints
- URL: https://openrouter.ai/

## Installation and Setup

### Python SDK Installation

#### Option 1: Google Gen AI SDK (Recommended)
```bash
pip install google-genai
```

#### Option 2: Legacy Google Generative AI SDK
```bash
pip install google-generativeai
```

### Authentication Setup

#### For Google AI Studio
1. Get API key from [Google AI Studio](https://ai.google.dev/)
2. Set environment variable:
```bash
export GOOGLE_API_KEY="your-api-key"
```

#### For Vertex AI
1. Create Google Cloud Project
2. Enable Vertex AI API
3. Set up authentication:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI=True
```

## Basic Usage

### Using Google Gen AI SDK

#### Initialize Client
```python
import google.genai as genai

# For Google AI Studio
client = genai.Client(api_key="your-api-key")

# For Vertex AI
client = genai.Client(
    vertexai=True,
    project="your-project-id",
    location="us-central1"
)
```

#### Text Generation
```python
model_id = "gemini-2.0-flash-exp"

response = client.models.generate_content(
    model=model_id,
    contents="Explain quantum computing in simple terms"
)

print(response.text)
```

#### Multimodal Input
```python
from PIL import Image
import requests

# Load image
image = Image.open(
    requests.get(
        "https://example.com/image.jpg",
        stream=True
    ).raw
)

response = client.models.generate_content(
    model=model_id,
    contents=[
        image,
        "Describe what you see in this image"
    ]
)

print(response.text)
```

### Configuration Options

#### Generation Parameters
```python
from google.genai.types import GenerateContentConfig

config = GenerateContentConfig(
    temperature=0.7,        # Controls randomness (0.0-1.0)
    top_p=0.95,            # Nucleus sampling
    top_k=40,              # Top-k sampling
    candidate_count=1,      # Number of responses
    max_output_tokens=1024, # Maximum response length
    stop_sequences=["STOP"], # Stop generation at these sequences
    seed=42                 # For reproducible results
)

response = client.models.generate_content(
    model=model_id,
    contents="Write a short story",
    config=config
)
```

## Advanced Features

### 1. Tool Use and Function Calling
```python
from google.genai.types import Tool, FunctionDeclaration

# Define a function
def get_weather(location: str) -> str:
    # Implementation here
    return f"Weather in {location}: Sunny, 75°F"

# Define tool
weather_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_weather",
            description="Get weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        )
    ]
)

response = client.models.generate_content(
    model=model_id,
    contents="What's the weather like in New York?",
    config=GenerateContentConfig(tools=[weather_tool])
)
```

### 2. Search as a Tool
```python
from google.genai.types import Tool, GoogleSearch

google_search_tool = Tool(
    google_search=GoogleSearch()
)

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='What are the latest developments in AI?',
    config=GenerateContentConfig(
        tools=[google_search_tool]
    )
)

print(response.text)
# Access grounding metadata
print(response.candidates[0].grounding_metadata)
```

### 3. Multimodal Live API
```python
MODEL = 'models/gemini-2.0-flash-exp'
CONFIG = {'generation_config': {'response_modalities': ['AUDIO']}}

async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
    message = 'Tell me about the latest AI trends'
    await session.send(message, end_of_turn=True)
    
    async for response in session:
        model_turn = response.server_content.model_turn
        for part in model_turn.parts:
            print("Response:", part.text)
```

## Error Handling

### Common Error Patterns
```python
try:
    response = client.models.generate_content(
        model=model_id,
        contents="Your prompt here"
    )
    print(response.text)
    
except Exception as e:
    if "QUOTA_EXCEEDED" in str(e):
        print("Rate limit exceeded. Please wait and try again.")
    elif "INVALID_ARGUMENT" in str(e):
        print("Invalid input provided.")
    else:
        print(f"Error: {e}")
```

### Rate Limiting
```python
import time
from typing import Generator

def retry_with_backoff(func, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = backoff_factor ** attempt
            time.sleep(wait_time)
```

## Best Practices

### 1. Prompt Engineering
```python
# Use clear, specific prompts
prompt = """
Task: Analyze the sentiment of the following text
Text: "I love this product! It works perfectly."
Format: Return only "positive", "negative", or "neutral"
"""

# Use examples for better results
prompt = """
Classify the sentiment of these reviews:

Example 1: "Great product!" → positive
Example 2: "Terrible quality" → negative
Example 3: "It's okay" → neutral

Review: "I love this product! It works perfectly."
Sentiment:
"""
```

### 2. Efficient Token Usage
```python
# Use shorter prompts when possible
# Cache responses for repeated queries
# Use appropriate model for task complexity

# For simple tasks, use Flash-Lite
# For complex reasoning, use Pro
# For general use, use Flash
```

### 3. Cost Optimization
```python
# Monitor token usage
def estimate_cost(input_tokens, output_tokens, model="gemini-2.0-flash"):
    rates = {
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
        "gemini-2.0-flash-lite": {"input": 0.05, "output": 0.20}
    }
    
    rate = rates.get(model, rates["gemini-2.0-flash"])
    cost = (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1000000
    return cost
```

## Code Examples

### Newsletter Analysis Script
```python
import google.genai as genai
from typing import List, Dict

class NewsletterAnalyzer:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"
    
    def analyze_newsletter(self, content: str) -> Dict:
        prompt = f"""
        Analyze this newsletter content and extract:
        1. Main topics and themes
        2. Key trends mentioned
        3. Important developments
        4. Sentiment (positive/negative/neutral)
        
        Newsletter content:
        {content}
        
        Return analysis in JSON format.
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=genai.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1000
            )
        )
        
        return response.text
    
    def summarize_trends(self, newsletters: List[str]) -> str:
        combined_analysis = []
        for newsletter in newsletters:
            analysis = self.analyze_newsletter(newsletter)
            combined_analysis.append(analysis)
        
        summary_prompt = f"""
        Based on these newsletter analyses, provide a comprehensive summary 
        of the latest AI trends:
        
        {' '.join(combined_analysis)}
        
        Focus on:
        1. Emerging technologies
        2. Industry developments
        3. Key players and companies
        4. Future predictions
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=summary_prompt,
            config=genai.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=2000
            )
        )
        
        return response.text

# Usage
analyzer = NewsletterAnalyzer("your-api-key")
trends_summary = analyzer.summarize_trends(newsletter_contents)
```

## Resources and Documentation

### Official Documentation
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google Gen AI SDK Guide](https://ai.google.dev/docs/gemini-api/quickstart)
- [Vertex AI Gemini API](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini)

### Code Examples and Notebooks
- [Gemini Cookbook](https://github.com/google-gemini/cookbook)
- [Vertex AI Generative AI Samples](https://github.com/GoogleCloudPlatform/generative-ai)
- [Google AI Studio Examples](https://ai.google.dev/examples)

### Pricing Information
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)

## Troubleshooting

### Common Issues
1. **API Key Issues**
   - Verify API key is valid and has proper permissions
   - Check if key is properly set in environment variables

2. **Rate Limiting**
   - Implement exponential backoff
   - Monitor usage and upgrade plan if needed

3. **Token Limits**
   - Check context window limits
   - Implement content chunking for large inputs

4. **Model Availability**
   - Some models may have regional restrictions
   - Experimental models may have limited availability

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for requests
import httpx
httpx._config.DEFAULT_TIMEOUT = 60.0
```

## Migration Guide

### From Legacy SDK to Gen AI SDK
```python
# Old way (google-generativeai)
import google.generativeai as genai
genai.configure(api_key="your-api-key")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello")

# New way (google-genai)
import google.genai as genai
client = genai.Client(api_key="your-api-key")
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Hello"
)
```

### Performance Improvements
- Gemini 2.0 Flash: 50% faster time-to-first-token
- Better multimodal understanding
- Improved coding capabilities
- Enhanced function calling 