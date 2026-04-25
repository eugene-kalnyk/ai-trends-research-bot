# Project Maintenance Guide

This guide outlines how to maintain the AI Trends Research Bot project structure, ensuring consistency, security, and organization.

## 📁 Directory Structure & Purpose

### Core Directories

```
ai-trends-research-bot/
├── src/                      # 🎯 MAIN SOURCE CODE
├── config/                   # 🔒 SECURE CONFIGURATION FILES
├── utils/                    # 🛠️ UTILITY SCRIPTS & TOOLS
├── tests/                    # 🧪 TEST FILES
├── outputs/                  # 📄 GENERATED REPORTS
├── logs/                     # 📋 LOG FILES
├── .cursor/                  # 📚 DOCUMENTATION & PLANNING
└── docs/                     # 📖 USER DOCUMENTATION (future)
```

### Directory Rules

| Directory | Purpose | What Goes Here | What DOESN'T Go Here |
|-----------|---------|----------------|----------------------|
| `src/` | Core application code | Main modules, classes, business logic | Tests, utilities, config files |
| `config/` | Configuration & secrets | API keys, tokens, settings | Source code, temporary files |
| `utils/` | Development tools | Scripts for testing, debugging, setup | Production code, tests |
| `tests/` | Test suites | Unit tests, integration tests | Source code, utilities |
| `outputs/` | Generated files | Reports, exports, analysis results | Source code, config |
| `logs/` | Application logs | Runtime logs, debug files | Persistent data, config |

## 🔒 Security Guidelines

### Sensitive Files Protocol

**ALWAYS** place sensitive files in `config/`:
- ✅ `config/credentials.json` - OAuth2 credentials
- ✅ `config/token.json` - Access tokens  
- ✅ `config/api_keys.json` - API keys (if separate file)
- ✅ `config/secrets.env` - Environment-specific secrets

**NEVER** place sensitive files in:
- ❌ Root directory
- ❌ `src/` directory
- ❌ `utils/` directory

### .gitignore Maintenance

When adding new sensitive files, update `.gitignore`:
```gitignore
# Add new sensitive files here
config/new_secret_file.json
config/*.key
```

## 🆕 Adding New Files

### Source Code Files

**Location**: `src/`
**Naming**: `snake_case.py`
**Examples**:
- `src/data_analyzer.py` - New analysis module
- `src/report_templates.py` - Report generation templates
- `src/notification_service.py` - Email/Slack notifications

### Utility Scripts

**Location**: `utils/`
**Naming**: `descriptive_purpose.py`
**Examples**:
- `utils/backup_config.py` - Backup configuration files
- `utils/clean_logs.py` - Log cleanup utility
- `utils/migrate_data.py` - Data migration script

### Test Files

**Location**: `tests/`
**Naming**: `test_module_name.py`
**Examples**:
- `tests/test_gmail_client.py` - Gmail client tests
- `tests/test_email_processor.py` - Email processing tests
- `tests/test_report_generator.py` - Report generation tests

### Documentation Files

**Location**: Root or `docs/` (when created)
**Naming**: `UPPERCASE.md` for root, `lowercase.md` for docs/
**Examples**:
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history
- `docs/user_guide.md` - User documentation

## 📦 Module Organization

### Import Path Strategy

**For source code in `src/`**:
```python
# ✅ Correct - relative imports within src/
from .gmail_client import GmailClient
from .email_processor import EmailProcessor

# ✅ Correct - absolute imports from root
from src.gmail_client import GmailClient
```

**For utilities in `utils/`**:
```python
# ✅ Correct - path adjustment for accessing src/
import sys
sys.path.insert(0, '../src')
from gmail_client import GmailClient
```

**For tests in `tests/`**:
```python
# ✅ Correct - standard test imports
import sys
sys.path.insert(0, '../src')
from gmail_client import GmailClient
```

### Configuration File References

**Always use relative paths from project root**:
```python
# ✅ Correct - relative to project root
credentials_path = 'config/credentials.json'
token_path = 'config/token.json'

# ✅ Correct - for utilities in subdirectories
credentials_path = '../config/credentials.json'
```

## 🔧 Development Workflow

### Adding New Features

1. **Plan**: Update `.cursor/scratchpad.md` with feature plan
2. **Code**: Create new modules in `src/`
3. **Test**: Write tests in `tests/`
4. **Document**: Update README.md and add docstrings
5. **Configure**: Add any new settings to `environment.template`

### Adding New Utilities

1. **Create**: New script in `utils/`
2. **Import**: Use correct path adjustments for `src/` imports
3. **Document**: Add usage instructions in script header
4. **Test**: Create test utility if needed

### Configuration Changes

1. **Template**: Update `environment.template` first
2. **Code**: Update default values in source code
3. **Documentation**: Update README.md configuration section
4. **Security**: Ensure sensitive values are not hardcoded

## 📝 File Naming Conventions

### Python Files
- **Source**: `snake_case.py` (e.g., `gmail_client.py`)
- **Tests**: `test_module_name.py` (e.g., `test_gmail_client.py`)
- **Utils**: `descriptive_action.py` (e.g., `clean_old_logs.py`)

### Configuration Files
- **Templates**: `name.template` (e.g., `environment.template`)
- **Secrets**: `descriptive_name.json` (e.g., `credentials.json`)
- **Settings**: `app_settings.json`, `logging_config.yaml`

### Documentation Files
- **Root level**: `UPPERCASE.md` (e.g., `README.md`, `CHANGELOG.md`)
- **Docs folder**: `lowercase.md` (e.g., `user_guide.md`)

## 🧹 Maintenance Tasks

### Regular Cleanup

**Monthly**:
```bash
# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean old outputs
find outputs/ -name "*.md" -mtime +90 -delete

# Update dependencies
pip list --outdated
```

**Before Major Updates**:
```bash
# Backup configuration
cp -r config/ config_backup_$(date +%Y%m%d)/

# Update requirements
pip freeze > requirements.txt

# Run full test suite
python -m pytest tests/ -v
```

### Code Quality Checks

**Before Commits**:
```bash
# Check imports work correctly
python -c "from src.main import main; print('✅ Imports OK')"

# Validate configuration
python utils/test_filtering.py

# Check for security issues
grep -r "api_key\|password\|secret" src/ --exclude-dir=__pycache__
```

## 🚨 Common Pitfalls to Avoid

### ❌ Don't Do This
```python
# Hard-coded paths
credentials_path = "/Users/username/project/config/credentials.json"

# Secrets in source code
GEMINI_API_KEY = "actual_api_key_here"

# Imports from wrong locations
from utils.gmail_client import GmailClient  # utils shouldn't contain source code
```

### ✅ Do This Instead
```python
# Relative paths
credentials_path = "config/credentials.json"

# Environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Correct imports
from src.gmail_client import GmailClient
```

### Directory Mistakes to Avoid
- Putting source code in `utils/`
- Putting configuration in `src/`
- Putting tests in `src/`
- Putting temporary files in `config/`

## 📋 Checklist for New Contributors

Before adding new files:
- [ ] Read this maintenance guide
- [ ] Understand the directory structure
- [ ] Check where similar files are located
- [ ] Follow naming conventions
- [ ] Update relevant documentation
- [ ] Test imports work correctly
- [ ] Verify no sensitive data in source code
- [ ] Update requirements.txt if needed

## 🔄 Version Control Best Practices

### What to Commit
- ✅ Source code (`src/`)
- ✅ Tests (`tests/`)
- ✅ Utilities (`utils/`)
- ✅ Documentation (`*.md`)
- ✅ Configuration templates (`environment.template`)
- ✅ Requirements (`requirements.txt`)

### What NOT to Commit
- ❌ Sensitive files (`config/credentials.json`, `config/token.json`)
- ❌ Environment files (`.env`)
- ❌ Generated outputs (`outputs/`)
- ❌ Log files (`logs/`)
- ❌ Virtual environment (`venv/`, `.venv/`)

## 📖 Documentation Standards

### Code Documentation
- Use docstrings for all functions and classes
- Include type hints where appropriate
- Add inline comments for complex logic

### File Headers
```python
#!/usr/bin/env python3
"""
Module Name: Brief Description

Detailed description of what this module does.
Used by: List main users/callers
Dependencies: List key dependencies
"""
```

### README Updates
When adding new features:
- Update installation instructions if needed
- Add new configuration options
- Update usage examples
- Add new file descriptions to project structure

---

## 🎯 Summary

This project follows a **security-first, organized approach**:

1. **Sensitive files** → `config/`
2. **Source code** → `src/`
3. **Development tools** → `utils/`
4. **Test files** → `tests/`
5. **Generated content** → `outputs/`, `logs/`

Following these guidelines ensures the project remains secure, maintainable, and easy to understand for all contributors. 