# AI Trends Research Bot - Project Plan

## Background and Motivation
Building a script that automatically summarizes the latest AI trends by:
1. Connecting to Gmail via MCP to read newsletters from the last 7 days
2. Using Gemini 2.5-flash API to analyze and summarize the content
3. Generating a markdown summary of key AI trends and developments
4. Future iterations will include email output and scheduled runs

## High-Level Architecture
```
Gmail (MCP) → Newsletter Extraction → Gemini API → Markdown Summary
```

## Project Tasks

### Phase 1: Environment Setup and MCP Configuration
**Task 1.1: Project Structure Setup**
- Create basic Python project structure with requirements.txt
- Set up .env file template for API keys
- Create basic README with setup instructions
- **Success Criteria**: Clean project structure, .env template exists, requirements.txt has basic dependencies

**Task 1.2: MCP Gmail Integration Setup**
- Install and configure MCP for Gmail access
- Test connection and basic email reading functionality
- Document the setup process for future reference
- **Success Criteria**: Can successfully read emails from Gmail via MCP

### Phase 2: Newsletter Detection and Extraction
**Task 2.1: Newsletter Identification**
- Implement logic to identify newsletters (vs regular emails)
- Create filters for common newsletter patterns
- Add configurable time range (default: 7 days)
- **Success Criteria**: Can filter and identify newsletter emails from specified time period

**Task 2.2: Content Extraction**
- Extract relevant text content from newsletter emails
- Handle HTML email parsing
- Clean and preprocess text for AI analysis
- **Success Criteria**: Clean text extraction from newsletter emails

### Phase 3: Gemini Integration
**Task 3.1: Gemini API Setup**
- Configure Gemini 2.5-flash API client
- Create prompt templates for AI trend analysis
- Implement error handling and rate limiting
- **Success Criteria**: Can successfully call Gemini API and get responses

**Task 3.2: Trend Analysis Implementation**
- Design prompts for trend identification and summarization
- Implement batch processing of newsletter content
- Create structured output format for trends
- **Success Criteria**: Generates meaningful AI trend summaries from newsletter content

### Phase 4: Output Generation
**Task 4.1: Markdown Report Generation**
- Create structured markdown template for trends report
- Implement date-based organization
- Add metadata (sources, analysis date, etc.)
- **Success Criteria**: Generates well-formatted markdown reports

**Task 4.2: Main Script Integration**
- Create main execution script tying all components together
- Add command-line argument parsing for configuration
- Implement logging and error handling
- **Success Criteria**: Single script that runs end-to-end process

### Phase 5: Testing and Refinement
**Task 5.1: Unit Testing**
- Write tests for core functions
- Test email parsing and content extraction
- Test API integration with mock data
- **Success Criteria**: All core functions have tests and pass

**Task 5.2: Integration Testing**
- Test full pipeline with real data
- Validate output quality and format
- Performance testing and optimization
- **Success Criteria**: End-to-end pipeline works reliably

## Technical Considerations
- **MCP Setup**: Need to configure Gmail API credentials and MCP server
- **Rate Limiting**: Implement proper rate limiting for both Gmail API and Gemini API
- **Error Handling**: Robust error handling for API failures and network issues
- **Data Privacy**: Ensure sensitive email content is handled securely
- **Configurability**: Make time ranges, output formats, and API settings configurable

## Success Criteria for MVP
1. Script can connect to Gmail via MCP
2. Identifies and extracts newsletter content from last 7 days
3. Generates AI-powered trend summary using Gemini 2.5-flash
4. Outputs structured markdown report
5. Configurable time range and basic error handling

## Future Enhancements (Post-MVP)
- Email output functionality
- Scheduled execution (cron job or similar)
- Advanced newsletter filtering (by sender, keywords)
- Trend categorization and topic clustering
- Web dashboard for viewing trends
- Historical trend analysis

## Current Status / Progress Tracking
- **Current Phase**: MVP Complete – End-to-End Pipeline Working
- **Next Task**: Plan and prioritize future enhancements (see below)
- **Completed Tasks**: 
  - ✅ Task 1.1 - Project Structure Setup
  - ✅ Task 1.2 - Gmail API Integration Setup
  - ✅ Task 2.1 - Newsletter Identification
  - ✅ Task 2.2 - Content Extraction
  - ✅ Task 3.1 - Gemini API Setup
  - ✅ Task 3.2 - Trend Analysis Implementation
  - ✅ Task 4.1 - Markdown Report Generation
  - ✅ Task 4.2 - Main Script Integration
  - ✅ Task 5.1 - Unit Testing (core functions)
  - ✅ Task 5.2 - Integration Testing (end-to-end, real data)
- **Blocked/Issues**: None currently

## Executor's Feedback or Assistance Requests
- All MVP phases completed! The pipeline connects to Gmail, extracts and filters newsletters, analyzes with Gemini, and generates a clean, actionable markdown report.
- Prompt and report structure refined for clarity and audience fit; redundant sections (e.g., Newsletter Sources) removed as requested.
- End-to-end test successful: output is high quality and meets requirements.
- Ready for user review or to begin work on future enhancements (email output, scheduling, advanced filtering, dashboard, etc.)

## Lessons Learned
- **Prompt Engineering**: Clear, explicit instructions in the prompt are critical for controlling Gemini's output structure and content.
- **Pipeline Debugging**: Always verify that the full, raw model output is passed through the pipeline before post-processing or rendering.
- **Report Customization**: Programmatic sections (like newsletter sources) should be added only if they add value; otherwise, keep the report focused and concise.
- **Iterative Testing**: Frequent end-to-end tests help catch integration issues early and ensure the final output matches user expectations. 