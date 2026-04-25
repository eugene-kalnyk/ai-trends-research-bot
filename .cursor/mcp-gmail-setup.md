# MCP Gmail Server Setup Documentation

## Overview
Model Context Protocol (MCP) provides a standardized way to connect AI assistants to external systems. For Gmail integration, there are several MCP servers available that enable email management through natural language.

## Available MCP Gmail Servers

### 1. systemprompt-mcp-google (Recommended)
- **Provider**: Ejb503
- **Language**: TypeScript
- **Features**: Gmail, Google Calendar, Google Drive integration
- **Stats**: 10 stars, 3 forks
- **Package**: `systemprompt-mcp-google`

### 2. systemprompt-mcp-gmail
- **Provider**: Ejb503
- **Language**: TypeScript
- **Features**: Gmail-specific operations with voice support
- **Stats**: 8 stars, 1.1K downloads
- **Package**: `systemprompt-mcp-gmail`

### 3. Custom Gmail MCP Server
- **Provider**: Various community implementations
- **Language**: Python/TypeScript
- **Features**: Basic Gmail operations

## Prerequisites

### 1. Google Cloud Project Setup
1. Create a new Google Cloud project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the required APIs:
   - Gmail API (read, send, compose, modify, labels)
   - Google Calendar API (optional, for calendar features)
   - Google Drive API (optional, for drive features)

### 2. OAuth2 Credentials Configuration
1. Go to "APIs & Services" > "Credentials"
2. Create an OAuth 2.0 Client ID
3. Set application type to "Desktop App"
4. Set authorized redirect URIs (include `http://localhost:3333/oauth2callback`)
5. Download the credentials JSON file and save as `credentials/google-credentials.json`

### 3. API Key Requirements
- Systemprompt API key (free) from [systemprompt.io/console](https://systemprompt.io/console)
- Required to run the systemprompt MCP servers

## Installation and Setup

### Method 1: Using systemprompt-mcp-google (Recommended)

#### Step 1: Install Package
```bash
npm install systemprompt-mcp-google
```

#### Step 2: Create Credentials Directory
```bash
mkdir -p credentials
```

#### Step 3: Run Authentication
```bash
npm run auth-google
```

This will:
- Open browser for Google OAuth authentication
- Start local server on port 3333 for OAuth callback
- Generate and save tokens to `credentials/google-token.json`
- Close automatically once authentication is complete

#### Step 4: Configure MCP Client

For **Claude Desktop**, add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "google": {
      "command": "SYSTEMPROMPT_API_KEY=your_api_key npx systemprompt-mcp-google",
      "type": "stdio"
    }
  }
}
```

For **Cursor**, add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["systemprompt-mcp-google"],
      "env": {
        "SYSTEMPROMPT_API_KEY": "your_api_key"
      }
    }
  }
}
```

### Method 2: Using systemprompt-mcp-gmail (Voice-Enabled)

#### Prerequisites
- Base64 encoded Google credentials
- Base64 encoded Google token
- Systemprompt API key

#### Environment Setup
```bash
export GOOGLE_CREDENTIALS="your-base64-encoded-credentials"
export GOOGLE_TOKEN="your-base64-encoded-token"
export API_KEY="your-systemprompt-api-key"
```

#### Running the Server
```bash
npx systemprompt-mcp-gmail
```

### Method 3: Docker Setup

#### Authentication
```bash
docker run -i --rm \
  --mount type=bind,source=/path/to/gcp-oauth.keys.json,target=/gcp-oauth.keys.json \
  -v mcp-gdrive:/gdrive-server \
  -e GDRIVE_OAUTH_PATH=/gcp-oauth.keys.json \
  -e "GDRIVE_CREDENTIALS_PATH=/gdrive-server/credentials.json" \
  -p 3000:3000 \
  mcp/gdrive auth
```

#### Server Configuration
```json
{
  "mcpServers": {
    "gdrive": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "mcp-gdrive:/gdrive-server",
        "-e", "GDRIVE_CREDENTIALS_PATH=/gdrive-server/credentials.json",
        "mcp/gdrive"
      ]
    }
  }
}
```

## Available Operations

### Gmail Operations
- **Search Emails**: Find emails using keywords, sender names, or date ranges
- **Read Emails**: View email content, attachments, and threading information
- **Send Emails**: Compose and send new emails with AI assistance
- **Delete Emails**: Remove unwanted messages from inbox
- **Manage Drafts**: Create, edit, and manage email drafts
- **Handle Attachments**: Process email attachments
- **Manage Labels**: Organize emails with labels

### Example Commands
```javascript
// Send email
{
  "command": "gmail.sendEmail",
  "parameters": {
    "to": "recipient@example.com",
    "subject": "Hello from MCP",
    "body": "This email was sent via MCP!"
  }
}

// List messages
{
  "command": "gmail.listMessages",
  "parameters": {
    "maxResults": 10
  }
}
```

## Security Considerations

### OAuth2 Security
- Secure OAuth2 authentication flow
- Automatic token refresh
- Scoped access for different services
- Environment-based configuration

### Required Permissions
- Gmail: read, send, compose, modify, and manage labels
- Calendar: read events and calendars (if enabled)
- Drive: read-only access (if enabled)

## Troubleshooting

### Common Issues
1. **Authentication Errors**
   - Verify OAuth2 credentials are correctly configured
   - Check that redirect URIs are properly set
   - Ensure APIs are enabled in Google Cloud Console

2. **Token Expiration**
   - Tokens refresh automatically
   - If issues persist, re-run authentication process

3. **Permission Errors**
   - Verify required scopes are granted
   - Check that test users are added to OAuth consent screen

### Debug Mode
```bash
DEBUG=mcp:* npm run dev
```

## Advanced Features

### Sampling and Notifications
- Configure AI response processing and filtering
- Real-time updates on email operations
- Requires advanced MCP client support

### Multimodal Support
- Voice-controlled email interactions
- Real-time voice synthesis
- Integration with multimodal-mcp-client

## Resources
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Systemprompt Console](https://systemprompt.io/console)

## Testing
```bash
# Run all tests
npm test

# Watch mode for development
npm run test:watch

# Generate coverage report
npm run test:coverage
``` 