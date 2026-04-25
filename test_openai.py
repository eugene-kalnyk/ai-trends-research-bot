#!/usr/bin/env python3
"""
Test script for OpenAI client
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from openai_client import OpenAIClient
from email_processor import Newsletter
from datetime import datetime

def test_openai_client():
    """Test the OpenAI client with a simple example."""
    
    # Check if OpenAI API key is set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    print("✅ OpenAI API key found")
    
    # Create a test newsletter
    test_newsletter = Newsletter(
        sender="test@example.com",
        subject="Test AI Newsletter",
        date=datetime.now(),
        content="This is a test newsletter about AI trends and developments.",
        html_content="<p>This is a test newsletter about AI trends and developments.</p>",
        is_newsletter=True,
        source_domain="example.com"
    )
    
    # Initialize OpenAI client
    try:
        openai_client = OpenAIClient(api_key=openai_api_key)
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return False
    
    # Test analysis
    try:
        print("🔄 Testing OpenAI analysis...")
        result = openai_client.analyze_newsletter_batch_raw([test_newsletter])
        
        if result:
            print("✅ OpenAI analysis successful")
            print(f"📊 Result keys: {list(result.keys())}")
            
            # Check if key sections are present
            key_sections = ["executive_summary", "key_trends", "emerging_opportunities"]
            for section in key_sections:
                if section in result:
                    content = result[section]
                    if isinstance(content, str) and content.strip():
                        print(f"✅ {section}: {len(content)} characters")
                    elif isinstance(content, list) and content:
                        print(f"✅ {section}: {len(content)} items")
                    else:
                        print(f"⚠️  {section}: empty")
                else:
                    print(f"❌ {section}: missing")
            
            return True
        else:
            print("❌ OpenAI analysis returned None")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI analysis failed: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_client()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
