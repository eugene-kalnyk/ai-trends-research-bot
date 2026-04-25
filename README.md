# AI Trends Research Bot

An automated tool that analyzes AI newsletters from Gmail and generates trend summaries using Google's Gemini AI.

## Features

- 📧 Connects to Gmail via MCP (Model Context Protocol) to read newsletters
- 🤖 Uses Google Gemini 2.5-flash API for intelligent trend analysis
- 📝 Generates structured markdown reports of AI trends
- ⏰ Configurable time range for newsletter analysis (default: 7 days)
- 🔍 Smart newsletter detection and filtering
- 📊 Organized trend summaries with source attribution
- 🎯 Suggests fun, hands-on mini projects based on the latest AI trends

## Prerequisites

- Python 3.8 or higher
- Gmail account with newsletters
- Google Gemini API key
- MCP server for Gmail access (or direct Gmail API setup)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-trends-research-bot
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp environment.template .env
   # Edit .env with your actual API keys and configuration
   ```

## Configuration

### Required Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))
- `NEWSLETTER_LOOKBACK_DAYS`: Number of days to look back for newsletters (default: 7)

### Optional Configuration

- `OUTPUT_DIR`: Directory for output files (default: ./outputs)
- `LOG_LEVEL`: Logging level (default: INFO)
- Newsletter filtering settings (whitelist/blacklist)

## Running the Bot

1. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run the main script from the project root:**
   ```bash
   python src/main.py
   ```

3. **Options:**
   - Analyze newsletters from the last 7 days (default):
     ```bash
     python src/main.py
     ```
   - Analyze newsletters from a specific time range:
     ```bash
     python src/main.py --days 7
     ```
   - Generate report with custom output directory:
     ```bash
     python src/main.py --output-dir ./custom_reports
     ```
   - Run with verbose logging:
     ```bash
     python src/main.py --log-level DEBUG
     ```
   - Filter specific newsletter sources:
     ```bash
     python src/main.py --whitelist "substack.com,medium.com"
     ```

4. **Output:**
   - The generated markdown report will appear in the `outputs/` directory by default, or in the directory you specify with `--output-dir`.

**Troubleshooting:**
If you see `ModuleNotFoundError`, make sure you are running the script from the project root and your virtual environment is activated.

## Usage

See the 'Running the Bot' section above for script execution instructions.

### Output

- The generated markdown report includes:
  - Numbered/nested table of contents
  - Executive summary with bolded highlights
  - Major vendor announcements, opportunities, and engineering techniques
  - **Mini Projects to Try**: Up to three fun, hands-on project ideas with step-by-step instructions and links, inspired by the latest AI trends
  - Newsletter sources and metadata
  - Report metadata

## Project Structure

```
ai-trends-research-bot/
├── .cursor/                    # Documentation and project planning
│   ├── scratchpad.md          # Project plan and progress tracking
│   ├── mcp-gmail-setup.md     # MCP Gmail setup guide
│   ├── google-gemini-api.md   # Gemini API documentation
│   └── ...                    # Other documentation files
├── src/                       # Source code
│   ├── __init__.py
│   ├── main.py               # Main application entry point
│   ├── gmail_client.py       # Gmail API integration
│   ├── email_processor.py    # Email parsing and processing
│   ├── gemini_client.py      # Gemini API integration
│   └── report_generator.py   # Markdown report generation (includes 'Mini Projects to Try' section)
├── utils/                     # Utility scripts
│   ├── test_filtering.py     # Newsletter filtering test
│   └── scan_newsletters.py   # Newsletter scanning utility
├── config/                    # Configuration files
│   ├── credentials.json      # Gmail API credentials
│   └── token.json            # Gmail API token (generated)
├── tests/                     # Test files
├── outputs/                   # Generated reports
├── logs/                      # Log files
├── requirements.txt           # Python dependencies
├── environment.template       # Environment configuration template
└── README.md                 # This file
```

## Setup Guides

Detailed setup guides are available in the `.cursor/` directory:

- [MCP Gmail Setup](.cursor/mcp-gmail-setup.md) - Complete MCP Gmail server setup
- [Google Gemini API](.cursor/google-gemini-api.md) - Gemini API configuration
- [Gmail API Python](.cursor/gmail-api-python.md) - Direct Gmail API integration
- [Email Parsing Libraries](.cursor/python-email-parsing-libraries.md) - Email processing utilities

## Project Organization

For contributors and maintainers:

- [**Project Maintenance Guide**](.cursor/rules/MAINTENANCE.md) - Complete guide for project organization, file structure, and maintenance best practices

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_email_processor.py
```

### Development Setup

1. Install development dependencies:
   ```bash
   pip install -e .
   ```

2. Set up pre-commit hooks (if using):
   ```bash
   pre-commit install
   ```

## Roadmap

- [x] Project structure and documentation
- [x] Mini Projects section in reports
- [ ] MCP Gmail integration
- [ ] Newsletter detection and parsing
- [ ] Gemini API integration
- [ ] Markdown report generation
- [ ] Email output functionality
- [ ] Scheduled execution
- [ ] Web dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the documentation in `.cursor/`
- Review the setup guides
- Open an issue on GitHub 