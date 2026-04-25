"""
Report Generator Module

Handles generation of markdown reports from analyzed trends.
"""

import os
from datetime import datetime
from typing import List, Dict
from pathlib import Path

import structlog

from gemini_client import TrendSummary
from email_processor import Newsletter


logger = structlog.get_logger(__name__)


class ReportGenerator:
    """Handles generation of markdown trend reports."""
    
    def __init__(self, output_dir: str = "./outputs"):
        """Initialize report generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_raw_gemini_report(self, gemini_json: dict, newsletters: List[Newsletter], lookback_days: int = 7) -> str:
        """
        Generate a markdown report directly from the raw Gemini JSON response.
        Args:
            gemini_json: The full JSON object returned by Gemini
            newsletters: List of source newsletters
            lookback_days: Number of days analyzed
        Returns:
            str: Path to generated report file
        """
        from datetime import datetime

        # --- Section: Numbered headings and nested TOC ---
        # We'll build a structure to track section and subsection numbers and titles for TOC and heading numbering
        section_titles = []  # [(section_number, section_title, [subsection_titles])]
        section_counter = 1
        toc_lines = ["# Table of Contents\n"]
        toc_anchors = {
            'executive summary': 'executive-summary',
            'major vendor announcements': 'major-vendor-announcements',
            'papers': 'papers',
            'opportunities for ai sdrs': 'opportunities-for-ai-sdrs',
            'ai engineering techniques career growth': 'ai-engineering-techniques-career-growth',
            'inspiring ai applications': 'inspiring-ai-applications',
            'mini projects to try': 'mini-projects-to-try',
            'newsletter sources and metadata': 'newsletter-sources-and-metadata',
        }
        # Pre-scan gemini_json for section and subsection titles
        for key, value in gemini_json.items():
            section_title = key.replace('_', ' ').title()
            subsections = []
            if isinstance(value, list):
                for idx, item in enumerate(value, 1):
                    if isinstance(item, dict):
                        # Use a list of potential keys to find the title
                        title_keys = ['title', 'vendor_name', 'name', 'Title', 'Vendor Name', 'Vendor']
                        sub_title = next((item.get(k) for k in title_keys if item.get(k)), f"Item {idx}")
                        subsections.append(sub_title)
            section_titles.append((section_counter, section_title, subsections))
            section_counter += 1
        # Build nested TOC
        for sec_num, sec_title, subsections in section_titles:
            anchor = toc_anchors.get(sec_title.strip().lower(), sec_title.lower().replace(' ', '-'))
            toc_lines.append(f"- [{sec_num}. {sec_title}](#{anchor})")
            if subsections:
                for idx, sub in enumerate(subsections, 1):
                    sub_anchor = f"{anchor}-{idx}"
                    toc_lines.append(f"  - [{sec_num}.{idx} {sub}](#{sub_anchor})")
        toc_lines.append("")
        # --- End TOC logic ---

        report_date = datetime.now().strftime("%B %d, %Y")
        content = f"# AI Trends Report - {report_date}\n\n"
        content += f"*Generated from {len(newsletters)} newsletters over the past {lookback_days} days*\n\n---\n"
        content += "\n".join(toc_lines) + "---\n"

        # Section/subsection numbering state
        section_counter = 1
        for key, value in gemini_json.items():
            section_title = key.replace('_', ' ').title()
            anchor = toc_anchors.get(section_title.strip().lower(), section_title.lower().replace(' ', '-'))
            # Numbered section heading
            content += f"\n<a name=\"{anchor}\"></a>\n\n## {section_counter}. {section_title}\n\n"
            # Special handling for mini projects section
            if key.lower() in ('mini_projects_to_try', 'mini projects to try') and isinstance(value, list):
                for idx, item in enumerate(value, 1):
                    project_title = item.get('title') or f"Project {idx}"
                    sub_anchor = f"{anchor}-{idx}"
                    content += f"<a name=\"{sub_anchor}\"></a>\n\n### {section_counter}.{idx} {project_title}\n\n"
                    # Description
                    description = item.get('description')
                    if description:
                        content += f"**Description:** {description}\n\n"
                    # Step-by-step outline
                    steps = item.get('steps') or item.get('outline')
                    if steps and isinstance(steps, list):
                        content += "**How to Try:**\n"
                        for step in steps:
                            content += f"- {step}\n"
                        content += "\n"
                    # Links/references
                    links = item.get('links') or item.get('references')
                    if links and isinstance(links, list):
                        if len(links) == 1:
                            content += f"**Link:** [{links[0]}]({links[0]})\n\n"
                        elif len(links) > 1:
                            content += "**Links & References:**\n"
                            for l in links:
                                content += f"- [{l}]({l})\n"
                            content += "\n"
                    content += "\n"
            # Subsection logic for lists of dicts (other sections)
            elif isinstance(value, list):
                for idx, item in enumerate(value, 1):
                    title_keys = ['title', 'vendor_name', 'name', 'Title', 'Vendor Name', 'Vendor']
                    sub_title = next((item.get(k) for k in title_keys if item.get(k)), f"Item {idx}")
                    sub_anchor = f"{anchor}-{idx}"
                    content += f"<a name=\"{sub_anchor}\"></a>\n\n### {section_counter}.{idx} {sub_title}\n\n"
                    for k, v in item.items():
                        if k.lower() in ('title', 'vendor_name', 'name', 'Title'):
                            continue
                        if k.lower() == 'summary' and v:
                            content += f"**Summary:** {v}\n\n"
                            continue
                        if k.lower() in ('bullet_points', 'bullets', 'key_points') and isinstance(v, list):
                            content += "\n**Key Points:**\n"
                            for point in v:
                                content += f"- {point}\n"
                            content += "\n"
                            continue
                        if k.lower() == 'key_features' and isinstance(v, list):
                            content += "\n**Key Features:**\n"
                            for feature in v:
                                content += f"- {feature}\n"
                            content += "\n"
                            continue
                        if k.lower() == 'relevance_for_ai_sdr' and v:
                            content += f"> **💡 Relevance for AI SDR:** {v}\n\n"
                            continue
                        if k.lower() == 'actionable_recommendation' and v:
                            content += f"> **🚀 Actionable Recommendation:** {v}\n\n"
                            continue
                        if k.lower() == 'opportunities_and_risks' and v:
                            content += f"> **Opportunities and Risks:** {v}\n\n"
                            continue
                        if (k.lower() == 'links' and isinstance(v, list)) or (k.lower() == 'link' and isinstance(v, str)):
                            links = v if isinstance(v, list) else [v]
                            if links:
                                if len(links) == 1:
                                    content += f"**Link:** [{links[0]}]({links[0]})\n\n"
                                else:
                                    content += "**Links:**\n"
                                    for l in links:
                                        content += f"- [{l}]({l})\n"
                                    content += "\n"
                            else:
                                content += "(No links provided)\n\n"
                            continue
                        if k.lower() == 'what_should_i_do' and v:
                            content += f"> **What should I do?** {v}\n\n"
                            continue
                        content += f"**{k.replace('_', ' ').capitalize()}:** {v}\n\n"
            elif key.lower() in ('newsletter_sources_and_metadata', 'newsletter sources and metadata') and isinstance(value, list):
                content += f"{gemini_json.get('date_range', '')}\n"
                for item in value:
                    name = item.get('name', '')
                    homepage = item.get('homepage', '')
                    date = item.get('date', '')
                    title = item.get('title', '')
                    content += f"- **Name**: {name}\n"
                    if homepage:
                        content += f"  - **Homepage**: {homepage}\n"
                    if date:
                        content += f"  - **Date**: {date}\n"
                    if title:
                        content += f"  - **Title**: {title}\n"
                stats = gemini_json.get('statistics', {})
                if stats:
                    for k, v in stats.items():
                        content += f"- **{k.replace('_', ' ').capitalize()}**: {v}\n"
            else:
                # Fallback for simple string sections like Executive Summary
                if isinstance(value, str):
                    content += f"{value}\n"
                elif value: # Fallback for other unexpected types
                    content += f"{str(value)}\n"

            content += "\n---\n"
            section_counter += 1
        # Add metadata at the end
        content += self._build_metadata_section([], newsletters, lookback_days)
        # Save to file with timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_trends_report_{timestamp}.md"
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Generated report: {file_path}")
        return str(file_path)
    
    def generate_report(self, trends: List[TrendSummary], 
                       newsletters: List[Newsletter],
                       executive_summary: str = "",
                       lookback_days: int = 7) -> str:
        """
        Generate a comprehensive markdown report.
        
        Args:
            trends: List of analyzed trends
            newsletters: List of source newsletters
            executive_summary: Executive summary text
            lookback_days: Number of days analyzed
            
        Returns:
            str: Path to generated report file
        """
        try:
            # Generate report content
            report_content = self._build_report_content(
                trends, newsletters, executive_summary, lookback_days
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_trends_report_{timestamp}.md"
            file_path = self.output_dir / filename
            
            # Write report
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Generated report: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error("Failed to generate report", error=str(e))
            raise
    
    def _build_report_content(self, trends: List[TrendSummary], 
                            newsletters: List[Newsletter],
                            executive_summary: str,
                            lookback_days: int) -> str:
        """Build the complete markdown report content."""
        
        # Report header
        report_date = datetime.now().strftime("%B %d, %Y")
        content = f"""# AI Trends Report - {report_date}

*Generated from {len(newsletters)} newsletters over the past {lookback_days} days*

---

## Executive Summary

{executive_summary or "No executive summary available."}

---

## Key Trends

"""
        
        # Add trends by category
        trends_by_category = self._group_trends_by_category(trends)
        
        for category, category_trends in trends_by_category.items():
            content += f"### {category}\n\n"
            
            for trend in category_trends:
                content += self._format_trend(trend)
                content += "\n"
        
        # Add newsletter sources
        content += self._build_sources_section(newsletters)
        
        # Add metadata
        content += self._build_metadata_section(trends, newsletters, lookback_days)
        
        return content
    
    def _group_trends_by_category(self, trends: List[TrendSummary]) -> Dict[str, List[TrendSummary]]:
        """Group trends by category and sort by importance."""
        grouped = {}
        
        for trend in trends:
            category = trend.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(trend)
        
        # Sort each category by importance score
        for category in grouped:
            grouped[category].sort(key=lambda x: x.importance_score, reverse=True)
        
        # Sort categories by highest importance score
        sorted_categories = sorted(grouped.items(), 
                                 key=lambda x: max(t.importance_score for t in x[1]), 
                                 reverse=True)
        
        return dict(sorted_categories)
    
    def _format_trend(self, trend: TrendSummary) -> str:
        """Format a single trend for markdown."""
        content = f"""#### {trend.title}
**Importance Score:** {trend.importance_score}/10

{trend.description}

"""
        
        if trend.key_points:
            content += "**Key Points:**\n"
            for point in trend.key_points:
                content += f"- {point}\n"
            content += "\n"
        
        if trend.sources:
            content += "**Sources:**\n"
            for source in trend.sources:
                content += f"- {source}\n"
            content += "\n"
        
        return content
    
    def _build_sources_section(self, newsletters: List[Newsletter]) -> str:
        """Build the sources section of the report."""
        content = """---

## Newsletter Sources

The following newsletters were analyzed for this report:

"""
        
        # Group by source domain
        sources_by_domain = {}
        for newsletter in newsletters:
            domain = newsletter.source_domain
            if domain not in sources_by_domain:
                sources_by_domain[domain] = []
            sources_by_domain[domain].append(newsletter)
        
        for domain, domain_newsletters in sources_by_domain.items():
            content += f"### {domain}\n\n"
            
            for newsletter in domain_newsletters:
                date_str = newsletter.date.strftime("%Y-%m-%d")
                content += f"- **{newsletter.subject}** ({date_str})\n"
                content += f"  - From: {newsletter.sender}\n"
            
            content += "\n"
        
        return content
    
    def _build_metadata_section(self, trends: List[TrendSummary], 
                               newsletters: List[Newsletter],
                               lookback_days: int) -> str:
        """Build the metadata section."""
        content = """---

## Report Metadata

"""
        
        # Analysis statistics
        content += f"- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"- **Lookback Period:** {lookback_days} days\n"
        content += f"- **Newsletters Analyzed:** {len(newsletters)}\n"
        content += f"- **Trends Identified:** {len(trends)}\n"
        
        if trends:
            avg_importance = sum(t.importance_score for t in trends) / len(trends)
            content += f"- **Average Importance Score:** {avg_importance:.2f}/10\n"
            
            categories = set(t.category for t in trends)
            content += f"- **Categories Covered:** {', '.join(sorted(categories))}\n"
        
        content += "\n"
        
        # Date range
        if newsletters:
            earliest_date = min(n.date for n in newsletters)
            latest_date = max(n.date for n in newsletters)
            content += f"- **Content Date Range:** {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}\n"
        
        content += "\n---\n\n"
        content += "*Report generated by AI Trends Research Bot*\n"
        
        return content
    
    def generate_summary_report(self, trends: List[TrendSummary], 
                               newsletters: List[Newsletter]) -> str:
        """
        Generate a brief summary report.
        
        Args:
            trends: List of analyzed trends
            newsletters: List of source newsletters
            
        Returns:
            str: Path to generated summary report
        """
        try:
            # Generate summary content
            content = self._build_summary_content(trends, newsletters)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_trends_summary_{timestamp}.md"
            file_path = self.output_dir / filename
            
            # Write summary
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Generated summary report: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error("Failed to generate summary report", error=str(e))
            raise
    
    def _build_summary_content(self, trends: List[TrendSummary], 
                              newsletters: List[Newsletter]) -> str:
        """Build summary report content."""
        
        report_date = datetime.now().strftime("%B %d, %Y")
        content = f"""# AI Trends Summary - {report_date}

## Top Trends

"""
        
        # Sort trends by importance and take top 5
        top_trends = sorted(trends, key=lambda x: x.importance_score, reverse=True)[:5]
        
        for i, trend in enumerate(top_trends, 1):
            content += f"### {i}. {trend.title}\n"
            content += f"**Score:** {trend.importance_score}/10\n\n"
            content += f"{trend.description}\n\n"
        
        content += f"---\n\n"
        content += f"*Analyzed {len(newsletters)} newsletters*\n"
        
        return content 