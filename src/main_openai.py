#!/usr/bin/env python3
"""
AI Trends Research Bot - OpenAI Version

This script fetches newsletters from Gmail, analyzes them using OpenAI's GPT-4o-mini,
and generates a comprehensive AI trends report.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import structlog

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from gmail_client import GmailClient
from openai_client import OpenAIClient
from email_processor import EmailProcessor
from report_generator import ReportGenerator
from config import load_config


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def main():
    """Main function to run the AI Trends Research Bot."""
    parser = argparse.ArgumentParser(description="AI Trends Research Bot - OpenAI Version")
    parser.add_argument(
        "--days", 
        type=int, 
        default=7, 
        help="Number of days to look back for newsletters (default: 7)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./outputs", 
        help="Output directory for reports (default: ./outputs)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Run without making API calls (for testing)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Validate OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    logger.info(
        "Starting AI Trends Research Bot - OpenAI Version",
        lookback_days=args.days,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )
    
    try:
        # Initialize Gmail client
        gmail_client = GmailClient(
            credentials_path=config["gmail_credentials_path"],
            token_path=config["gmail_token_path"]
        )
        
        # Authenticate Gmail client
        if not gmail_client.authenticate():
            logger.error("Failed to authenticate Gmail client")
            sys.exit(1)
        
        # Initialize OpenAI client
        openai_client = OpenAIClient(api_key=openai_api_key)
        
        # Initialize email processor
        email_processor = EmailProcessor(
            blacklist=config["newsletter_blacklist"],
            sender_blacklist=config["newsletter_sender_blacklist"],
            subject_blacklist=config["newsletter_subject_blacklist"]
        )
        
        # Initialize report generator
        report_generator = ReportGenerator(output_dir=args.output_dir)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        # Fetch newsletters from Gmail
        newsletters = gmail_client.get_newsletters_last_days(days=args.days)
        
        logger.info("Fetched newsletters", count=len(newsletters))
        
        if not newsletters:
            logger.warning("No newsletters found for the specified date range")
            return
        
        # Process and filter newsletters
        newsletter_objects = email_processor.process_newsletters(newsletters)
        logger.info("Processed newsletters", 
                   original_count=len(newsletters),
                   processed_count=len(newsletter_objects))
        
        if not newsletter_objects:
            logger.warning("No newsletters remained after processing")
            return
        logger.info("Prepared Newsletter objects", count=len(newsletter_objects))
        
        if args.dry_run:
            logger.info("Dry run mode - skipping AI analysis")
            return
        
        # Analyze newsletters using OpenAI
        logger.info("Starting OpenAI analysis...")
        raw_analysis = openai_client.analyze_newsletter_batch_raw(newsletter_objects)
        
        if not raw_analysis:
            logger.error("Failed to get analysis from OpenAI")
            sys.exit(1)
        
        logger.info("OpenAI analysis complete.")
        
        # Validate and structure the response
        structured_analysis = openai_client._validate_and_structure_response(raw_analysis)
        
        # Generate report
        report_path = report_generator.generate_raw_gemini_report(
            gemini_json=structured_analysis,
            newsletters=newsletter_objects,
            lookback_days=args.days
        )
        
        logger.info("Report generated", path=report_path)
        print(f"\n✅ AI Trends Report generated: {report_path}")
        
    except Exception as e:
        logger.error("An error occurred during execution", error=str(e), exception=str(e))
        sys.exit(1)
    
    logger.info("AI Trends Research Bot - OpenAI Version completed successfully")


if __name__ == "__main__":
    main()
