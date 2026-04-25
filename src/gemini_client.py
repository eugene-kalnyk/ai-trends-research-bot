"""
Gemini Client Module

Handles integration with Google's Gemini AI API for trend analysis.
"""

import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import pathlib
import json
import re
import traceback

import google.generativeai as genai
from google.api_core.exceptions import InternalServerError, ResourceExhausted
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


class GeminiClient:
    """Handles Gemini API interactions for trend analysis."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Gemini client."""
        self.api_key = api_key
        self.model_name = model_name
        self.rate_limit = 2  # requests per minute for free tier
        self.last_request_time = 0
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        # Define the schema for structured trend output
        self.trend_schema = {
            "type": "object",
            "properties": {
                "trends": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "category": {"type": "string"},
                            "importance_score": {"type": "number"},
                            "summary": {"type": "string"},
                            "link": {"type": "string"},
                            "actionable_recommendation": {"type": "string"},
                            "opportunities_and_risks": {"type": "string"}
                        },
                        "required": ["title", "category", "importance_score", "summary", "link"]
                    }
                }
            },
            "required": ["trends"]
        }
        self.model = genai.GenerativeModel(model_name)
        # Load report prompt from file
        import pathlib
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
        Analyze a batch of newsletters and return the full raw Gemini JSON response.
        """
        if not newsletters:
            return {}
        
        # Process all newsletters in a single request (no batching)
        
        combined_content = self._prepare_content_for_analysis(newsletters)
        prompt = self.report_prompt_template.replace("{{NEWSLETTER_CONTENT}}", combined_content)
        prompt += "\n\nRespond ONLY with a JSON object."
        
        max_retries = 3
        backoff_factor = 2  # sleep for 2, 4, 8 seconds
        
        for attempt in range(max_retries):
            try:
                self._rate_limit_check()
                
                # Use a safer model for large content batches
                # model = genai.GenerativeModel("gemini-1.5-flash-latest")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.3,
                    }
                )
                
                # Try to get text regardless of parts presence; guard against ValueError from quick accessor
                response_text = None
                try:
                    response_text = response.text
                except Exception:
                    response_text = None
                
                if (not response_text) and hasattr(response, 'candidates') and response.candidates:
                    try:
                        first_candidate = response.candidates[0]
                        finish_reason = getattr(first_candidate, 'finish_reason', None)
                        if hasattr(first_candidate, 'content') and getattr(first_candidate.content, 'parts', None):
                            parts = first_candidate.content.parts
                            response_text = "".join(getattr(p, 'text', '') for p in parts if hasattr(p, 'text'))
                        if not response_text:
                            logger.error(
                                "Gemini candidate contains no parts/text.",
                                finish_reason=str(finish_reason)
                            )
                    except Exception:
                        response_text = None

                # If still no text, log and retry (do not abort immediately)
                if not response_text:
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                        logger.error(
                            "Gemini response was blocked",
                            reason=str(response.prompt_feedback.block_reason),
                            safety_ratings=str(response.prompt_feedback.safety_ratings)
                        )
                    else:
                        logger.error("Gemini response is empty and has no feedback.")
                    # Retry on next attempt
                    raise InternalServerError("Empty response without feedback")
                
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
                            raise InternalServerError("Failed to parse JSON from fenced block")
                    else:
                        logger.error("Failed to extract JSON from Gemini response.", response_text=response_text)
                        # Retry on next attempt
                        raise InternalServerError("Failed to extract JSON from response text")

            except (InternalServerError, ResourceExhausted) as e:
                # Check if it's a rate limit error and extract retry delay
                retry_delay = backoff_factor ** (attempt + 1)
                if "429" in str(e) and "retry_delay" in str(e):
                    # Try to extract the retry delay from the error message
                    import re
                    retry_match = re.search(r'retry_delay {\s*seconds: (\d+)', str(e))
                    if retry_match:
                        retry_delay = int(retry_match.group(1)) + 1  # Add 1 second buffer
                        logger.info(f"Using API-specified retry delay: {retry_delay} seconds")
                
                logger.warning(f"Gemini API error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Failed to get raw Gemini JSON.", error=str(e), exception=traceback.format_exc())
                    return None # Return None after all retries fail
            
            except Exception as e:
                logger.error("An unexpected error occurred during Gemini call", error=str(e), exception=traceback.format_exc())
                return None # Return None for other unexpected errors
        
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
                # Merge results (append lists, concatenate strings)
                for key in all_results:
                    if isinstance(all_results[key], list):
                        if key in batch_result and isinstance(batch_result[key], list):
                            all_results[key].extend(batch_result[key])
                    elif isinstance(all_results[key], str):
                        if key in batch_result and isinstance(batch_result[key], str):
                            if all_results[key]:
                                all_results[key] += "\n\n" + batch_result[key]
                            else:
                                all_results[key] = batch_result[key]
        
        return all_results
    
    def _prepare_content_for_analysis(self, newsletters: List[Newsletter]) -> str:
        """Prepare newsletter content for AI analysis."""
        content_sections = []
        
        for newsletter in newsletters:
            # Keep each newsletter snippet reasonably short to fit model limits
            snippet = (newsletter.content or "")[:900]
            section = f"""
            Newsletter: {newsletter.subject}
            Source: {newsletter.sender}
            Date: {newsletter.date.strftime('%Y-%m-%d')}
            Content: {snippet}...
            ---
            """
            content_sections.append(section)
        
        return "\n".join(content_sections)
    
    def _analyze_trends(self, prompt: str, newsletters: List[Newsletter]) -> List[TrendSummary]:
        """Analyze content to identify trends using prompt-based JSON output."""
        try:
            self._rate_limit_check()
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            import json
            # Parse the JSON response directly
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].text
            else:
                logger.error("No valid JSON response from Gemini.")
                return self._fallback_trend_analysis(newsletters)
            # Try to extract JSON from the response
            try:
                response_json = json.loads(response_text)
            except Exception:
                # Try to extract JSON from markdown/code block
                import re
                match = re.search(r'```json\\n(.*?)```', response_text, re.DOTALL)
                if not match:
                    match = re.search(r'```(.*?)```', response_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    response_json = json.loads(json_str)
                else:
                    logger.error("Failed to extract JSON from Gemini response.")
                    return self._fallback_trend_analysis(newsletters)
            trends_data = response_json.get("trends", [])
            trends = []
            for trend_data in trends_data:
                trend = TrendSummary(
                    title=trend_data.get('title', 'Unknown Trend'),
                    description=trend_data.get('summary', ''),
                    category=trend_data.get('category', 'General'),
                    importance_score=float(trend_data.get('importance_score', 5.0)),
                    sources=[trend_data.get('link', '')] if trend_data.get('link') else [],
                    key_points=[kp for kp in [trend_data.get('actionable_recommendation', ''), trend_data.get('opportunities_and_risks', '')] if kp]
                )
                trends.append(trend)
            return trends
        except Exception as e:
            logger.error("Failed to analyze trends", error=str(e))
            return self._fallback_trend_analysis(newsletters)
    
    def _parse_trend_response(self, response_text: str, newsletters: List[Newsletter]) -> List[TrendSummary]:
        """Parse Gemini response into TrendSummary objects."""
        try:
            import json
            
            # Extract JSON from response (handle markdown formatting)
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0]
            
            trends_data = json.loads(json_text)
            
            trends = []
            for trend_data in trends_data:
                # Extract sources from newsletters
                sources = [f"{n.sender} ({n.date.strftime('%Y-%m-%d')})" for n in newsletters]
                
                trend = TrendSummary(
                    title=trend_data.get('title', 'Unknown Trend'),
                    description=trend_data.get('description', ''),
                    category=trend_data.get('category', 'General'),
                    importance_score=float(trend_data.get('importance_score', 5.0)),
                    sources=sources,
                    key_points=trend_data.get('key_points', [])
                )
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error("Failed to parse trend response", error=str(e))
            return self._fallback_trend_analysis(newsletters)
    
    def _fallback_trend_analysis(self, newsletters: List[Newsletter]) -> List[TrendSummary]:
        """Fallback trend analysis when JSON parsing fails."""
        # Simple fallback - create basic trend summaries
        trends = []
        
        for newsletter in newsletters:
            trend = TrendSummary(
                title=f"Trend from {newsletter.subject}",
                description=newsletter.content[:200] + "...",
                category="General",
                importance_score=5.0,
                sources=[f"{newsletter.sender} ({newsletter.date.strftime('%Y-%m-%d')})"],
                key_points=["Content from newsletter analysis"]
            )
            trends.append(trend)
        
        return trends[:5]  # Limit to top 5
    
    def summarize_trends(self, trends: List[TrendSummary]) -> str:
        """
        Generate an executive summary of trends.
        
        Args:
            trends: List of TrendSummary objects
            
        Returns:
            str: Executive summary
        """
        if not trends:
            return "No trends identified."
        
        try:
            self._rate_limit_check()
            
            trends_text = "\n".join([
                f"- {trend.title}: {trend.description} (Score: {trend.importance_score})"
                for trend in trends
            ])
            
            prompt = f"""
            Based on the following AI trends, write a concise executive summary (2-3 paragraphs) 
            highlighting the most important developments:
            
            {trends_text}
            
            Focus on the highest-scoring trends and their potential impact.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error("Failed to generate trend summary", error=str(e))
            return "Unable to generate executive summary." 