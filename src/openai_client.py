"""
OpenAI Client Module

Handles integration with OpenAI's GPT-4o-mini API for trend analysis.
"""

import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import pathlib
import json
import re
import traceback

import openai
from openai import OpenAI
import structlog

from email_processor import Newsletter


logger = structlog.get_logger(__name__)


@dataclass
class TrendSummary:
    """Represents an analyzed AI trend."""
    title: str
    description: str
    category: str
    importance_score: float
    sources: List[str]
    key_points: List[str]


class OpenAIClient:
    """Handles OpenAI API interactions for trend analysis."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4.1-mini"):
        """Initialize OpenAI client."""
        self.api_key = api_key
        self.model_name = model_name
        self.rate_limit = 10  # requests per minute (conservative)
        self.last_request_time = 0
        
        # Configure OpenAI
        self.client = OpenAI(api_key=api_key)
        
        # Load report prompt from file
        prompt_path = pathlib.Path("config/gemini_report_prompt.md")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.report_prompt_template = f.read()
    
    def _rate_limit_check(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 60.0 / self.rate_limit  # seconds between requests
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def analyze_newsletter_batch(self, newsletters: List[Newsletter]) -> List[TrendSummary]:
        """
        Analyze a batch of newsletters to identify trends and generate a report.
        """
        if not newsletters:
            return []
        # Combine newsletter content for analysis
        combined_content = self._prepare_content_for_analysis(newsletters)
        # Build prompt from template (but instruct for JSON output)
        prompt = self.report_prompt_template.replace("{{NEWSLETTER_CONTENT}}", combined_content)
        # Add explicit instruction for JSON output
        prompt += "\n\nRespond ONLY with a JSON object matching the provided schema."
        # Analyze trends
        trends = self._analyze_trends(prompt, newsletters)
        logger.info(f"Identified {len(trends)} trends from {len(newsletters)} newsletters")
        return trends
    
    def analyze_newsletter_batch_raw(self, newsletters: List[Newsletter]) -> dict:
        """
        Analyze a batch of newsletters and return the full raw OpenAI JSON response.
        """
        if not newsletters:
            return {}
        
        # If we have too many newsletters, batch them into smaller chunks
        max_newsletters_per_batch = 5  # Reduced from 20 to 5
        if len(newsletters) > max_newsletters_per_batch:
            logger.info(f"Batching {len(newsletters)} newsletters into chunks of {max_newsletters_per_batch}")
            return self._analyze_batched_newsletters_raw(newsletters, max_newsletters_per_batch)
        
        combined_content = self._prepare_content_for_analysis(newsletters)
        prompt = self.report_prompt_template.replace("{{NEWSLETTER_CONTENT}}", combined_content)
        prompt += "\n\nRespond ONLY with a JSON object."
        
        max_retries = 3
        backoff_factor = 2  # sleep for 2, 4, 8 seconds
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_check()
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are an AI trends analyst. Analyze the provided newsletter content and return a structured JSON response."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=8000
                )
                
                # Extract the response text
                response_text = response.choices[0].message.content
                
                if not response_text:
                    logger.error("OpenAI response is empty.")
                    raise Exception("Empty response from OpenAI")
                
                # Try to extract JSON from the response
                try:
                    response_json = json.loads(response_text)
                    return response_json # Success
                except json.JSONDecodeError:
                    match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        try:
                            response_json = json.loads(json_str)
                            return response_json # Success
                        except json.JSONDecodeError as e:
                            logger.error("Failed to parse extracted JSON", error=str(e), json_string=json_str)
                            # Retry on next attempt
                            raise Exception("Failed to parse JSON from fenced block")
                    else:
                        logger.error("Failed to extract JSON from OpenAI response.", response_text=response_text)
                        # Retry on next attempt
                        raise Exception("Failed to extract JSON from response text")

            except Exception as e:
                logger.warning(f"OpenAI API error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {backoff_factor ** (attempt + 1)}s...")
                if attempt < max_retries - 1:
                    time.sleep(backoff_factor ** (attempt + 1))
                else:
                    logger.error("Max retries reached. Failed to get raw OpenAI JSON.", error=str(e), exception=traceback.format_exc())
                    return None # Return None after all retries fail
        
        return None # Should not be reached, but as a fallback
    
    def _analyze_batched_newsletters_raw(self, newsletters: List[Newsletter], batch_size: int) -> dict:
        """
        Analyze newsletters in batches and merge the results.
        """
        all_results = {
            "executive_summary": "",
            "key_trends": [],
            "emerging_opportunities": [],
            "vendor_spotlight": [],
            "actionable_insights": [],
            "learning_resources": [],
            "inspiring_ai_applications": []
        }
        
        # Split newsletters into batches
        batches = [newsletters[i:i + batch_size] for i in range(0, len(newsletters), batch_size)]
        
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} newsletters")
            
            # Analyze this batch
            batch_result = self.analyze_newsletter_batch_raw(batch)
            
            if batch_result:
                logger.info(f"Batch {i+1} result fields", fields=list(batch_result.keys()))
                # Merge results (append lists, concatenate strings, handle dictionaries)
                for key in all_results:
                    if isinstance(all_results[key], list):
                        if key in batch_result and isinstance(batch_result[key], list):
                            all_results[key].extend(batch_result[key])
                            logger.info(f"Merged {len(batch_result[key])} items into {key}")
                    elif isinstance(all_results[key], str):
                        if key in batch_result and isinstance(batch_result[key], str):
                            if all_results[key]:
                                all_results[key] += "\n\n" + batch_result[key]
                            else:
                                all_results[key] = batch_result[key]
                            logger.info(f"Merged string into {key}, length: {len(batch_result[key])}")
                        elif key in batch_result and isinstance(batch_result[key], dict) and key == "executive_summary":
                            # Handle executive_summary as a dictionary
                            if "content" in batch_result[key]:
                                if all_results[key]:
                                    all_results[key] += "\n\n" + batch_result[key]["content"]
                                else:
                                    all_results[key] = batch_result[key]["content"]
                                logger.info(f"Merged executive_summary dict content, length: {len(batch_result[key]['content'])}")
                            else:
                                all_results[key] = str(batch_result[key])
                                logger.info(f"Merged executive_summary dict as string")
            else:
                logger.warning(f"Batch {i+1} returned None result")
        
        return all_results
    
    def _prepare_content_for_analysis(self, newsletters: List[Newsletter]) -> str:
        """Prepare newsletter content for AI analysis."""
        content_sections = []
        
        for newsletter in newsletters:
            # Reduce content size to avoid hitting API limits
            section = f"""
            Newsletter: {newsletter.subject}
            Source: {newsletter.sender}
            Date: {newsletter.date.strftime('%Y-%m-%d')}
            Content: {newsletter.content[:500]}...
            ---
            """
            content_sections.append(section)
        
        return "\n".join(content_sections)
    
    def _analyze_trends(self, prompt: str, newsletters: List[Newsletter]) -> List[TrendSummary]:
        """Analyze trends from the given prompt and newsletters."""
        try:
            raw_response = self.analyze_newsletter_batch_raw(newsletters)
            if not raw_response:
                return []
            
            # Convert raw response to TrendSummary objects
            trends = []
            if "trends" in raw_response:
                for trend_data in raw_response["trends"]:
                    trend = TrendSummary(
                        title=trend_data.get("title", ""),
                        description=trend_data.get("summary", ""),
                        category=trend_data.get("category", ""),
                        importance_score=trend_data.get("importance_score", 0.0),
                        sources=[trend_data.get("link", "")],
                        key_points=[trend_data.get("actionable_recommendation", "")]
                    )
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error("Failed to analyze trends", error=str(e), exception=traceback.format_exc())
            return []
    
    def _validate_and_structure_response(self, raw_response: dict) -> dict:
        """Validate and structure the raw response."""
        # Debug: Log the actual fields in the response
        logger.info("Raw response fields", fields=list(raw_response.keys()))
        
        # Map the actual response fields to the expected fields
        field_mapping = {
            "executive_summary": ["executive_summary", "overview"],
            "key_trends": ["key_trends", "major_vendor_announcements"],
            "emerging_opportunities": ["emerging_opportunities", "opportunities_for_ai_sdrs"],
            "vendor_spotlight": ["vendor_spotlight", "major_vendor_announcements"],
            "actionable_insights": ["actionable_insights", "opportunities_for_ai_sdrs"],
            "learning_resources": ["learning_resources", "ai_engineering_techniques_career_growth", "mini_projects_to_try"],
            "inspiring_ai_applications": ["inspiring_ai_applications"]
        }
        
        structured_response = {}
        for expected_field, possible_fields in field_mapping.items():
            # Try to find the field in the response
            value = None
            for field in possible_fields:
                if field in raw_response:
                    value = raw_response[field]
                    logger.info(f"Found field '{field}' for '{expected_field}'")
                    break
            
            if value is None:
                value = "No data available for this section."
                logger.warning(f"No field found for '{expected_field}'")
            elif isinstance(value, str) and not value.strip():
                value = "No data available for this section."
                logger.warning(f"Empty string found for '{expected_field}'")
            elif isinstance(value, dict) and expected_field == "executive_summary":
                # Handle executive_summary as a dictionary
                if "content" in value:
                    value = value["content"]
                else:
                    value = str(value)
                logger.info(f"Extracted content from executive_summary dict")
            
            structured_response[expected_field] = value
        
        return structured_response
