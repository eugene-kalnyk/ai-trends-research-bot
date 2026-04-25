#!/usr/bin/env python3
"""
AI Trends Research Bot - Main Application

This script analyzes AI newsletters from Gmail and generates trend summaries
using Google's Gemini AI.
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
import structlog

from src.config import load_config


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup structured logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
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


def create_output_directories(config: dict) -> None:
    """Create necessary output directories."""
    Path(config['output_dir']).mkdir(parents=True, exist_ok=True)
    Path('./logs').mkdir(parents=True, exist_ok=True)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI Trends Research Bot - Analyze AI newsletters and generate trend summaries"
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=None,
        help='Number of days to look back for newsletters (overrides env var)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default=None,
        help='Directory for output files (overrides env var)'
    )
    
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=None,
        help='Logging level (overrides env var)'
    )
    
    parser.add_argument(
        '--whitelist', 
        type=str, 
        default=None,
        help='Comma-separated list of newsletter domains/senders to include'
    )
    
    parser.add_argument(
        '--blacklist', 
        type=str, 
        default=None,
        help='Comma-separated list of domains/senders to exclude'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Run without making actual API calls (for testing)'
    )
    
    return parser.parse_args()


def main():
    """Main application entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        # Load configuration
        config = load_config()
        # Override config with command line arguments
        if args.days:
            config['newsletter_lookback_days'] = args.days
        if args.output_dir:
            config['output_dir'] = args.output_dir
        if args.log_level:
            config['log_level'] = args.log_level
        if args.whitelist:
            config['newsletter_whitelist'] = args.whitelist.split(',')
        if args.blacklist:
            config['newsletter_blacklist'] = args.blacklist.split(',')
        # Setup logging
        setup_logging(config['log_level'], config['log_file'])
        logger = structlog.get_logger()
        # Create output directories
        create_output_directories(config)
        logger.info("Starting AI Trends Research Bot", 
                   lookback_days=config['newsletter_lookback_days'],
                   output_dir=config['output_dir'],
                   dry_run=args.dry_run)

        # === MAIN PIPELINE IMPLEMENTATION ===
        from src.gmail_client import GmailClient
        from src.email_processor import EmailProcessor, Newsletter
        from src.gemini_client import GeminiClient
        from src.report_generator import ReportGenerator

        # 1. Connect to Gmail
        gmail_client = GmailClient()
        if not gmail_client.authenticate():
            logger.error("Failed to authenticate with Gmail. Exiting.")
            sys.exit(1)

        # 2. Fetch newsletters from the specified time range
        raw_newsletters = gmail_client.get_newsletters_last_days(config['newsletter_lookback_days'])
        logger.info(f"Fetched {len(raw_newsletters)} potential newsletters")

        # 3. Filter and process newsletters
        email_processor = EmailProcessor(
            whitelist=config['newsletter_whitelist'],
            blacklist=config['newsletter_blacklist'],
            sender_blacklist=config['newsletter_sender_blacklist'],
            subject_blacklist=config['newsletter_subject_blacklist']
        )
        filtered_newsletters = [n for n in raw_newsletters if email_processor.is_newsletter(n)]
        logger.info(f"Filtered down to {len(filtered_newsletters)} newsletters after applying filters")

        # 4. Convert to Newsletter dataclass objects
        def to_newsletter(email_dict):
            # Defensive: handle missing fields
            from src.email_processor import Newsletter
            from email.utils import parsedate_to_datetime
            sender = email_dict.get('sender', '')
            subject = email_dict.get('subject', '')
            date = email_dict.get('date')
            if not isinstance(date, datetime):
                try:
                    date = parsedate_to_datetime(str(date))
                except Exception:
                    date = datetime.now()
            content = email_dict.get('text_content') or email_dict.get('html_content') or ''
            html_content = email_dict.get('html_content', '')
            # Extract domain for source_domain
            domain = sender
            if '@' in sender:
                if '<' in sender and '>' in sender:
                    email_part = sender.split('<')[1].split('>')[0]
                    domain = email_part.split('@')[1].lower().strip()
                else:
                    domain = sender.split('@')[1].lower().strip()
            return Newsletter(
                sender=sender,
                subject=subject,
                date=date,
                content=content,
                source_domain=domain,
                html_content=html_content,
                is_newsletter=True
            )
        newsletters = [to_newsletter(n) for n in filtered_newsletters]
        logger.info(f"Prepared {len(newsletters)} Newsletter objects for analysis")

        if not newsletters:
            logger.warning("No newsletters to analyze after filtering. Exiting.")
            sys.exit(0)

        # 5. Analyze trends using Gemini API
        gemini_client = GeminiClient(api_key=config['gemini_api_key'])
        # Get the raw Gemini JSON response (simulate by calling analyze_newsletter_batch and capturing the raw JSON)
        # Instead of analyze_newsletter_batch, we need a method to get the raw JSON. For now, let's assume analyze_newsletter_batch returns the JSON dict if we add a flag.
        # If not, you may need to refactor GeminiClient to expose the raw JSON. For now, let's call a new method: analyze_newsletter_batch_raw
        if hasattr(gemini_client, 'analyze_newsletter_batch_raw'):
            gemini_json = gemini_client.analyze_newsletter_batch_raw(newsletters)
        else:
            # fallback: use analyze_newsletter_batch and reconstruct JSON from TrendSummary (not ideal)
            trends = gemini_client.analyze_newsletter_batch(newsletters)
            # This fallback will not be as rich as the real Gemini JSON
            gemini_json = {"trends": [t.__dict__ for t in trends]}
        logger.info("Gemini analysis complete.")

        if not gemini_json:
            logger.error("Failed to get a valid response from Gemini after multiple retries. Aborting.")
            sys.exit(1)

        # 6. Generate markdown report from raw Gemini JSON
        report_generator = ReportGenerator(output_dir=config['output_dir'])
        report_path = report_generator.generate_raw_gemini_report(
            gemini_json=gemini_json,
            newsletters=newsletters,
            lookback_days=config['newsletter_lookback_days']
        )
        logger.info(f"Report generated at {report_path}")
        print(f"\n✅ AI Trends Report generated: {report_path}\n")
        logger.info("AI Trends Research Bot completed successfully")

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("An error occurred", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
