# Quick Reference Guide

## 📁 Where to Put Files

| File Type | Location | Example |
|-----------|----------|---------|
| 🎯 Main code | `src/` | `src/new_analyzer.py` |
| 🔒 Secrets | `config/` | `config/new_api_key.json` |
| 🛠️ Dev tools | `utils/` | `utils/cleanup_script.py` |
| 🧪 Tests | `tests/` | `tests/test_new_feature.py` |
| 📄 Reports | `outputs/` | Auto-generated |
| 📋 Logs | `logs/` | Auto-generated |

## 🔧 Common Commands

### Testing
```bash
# Test filtering
python utils/test_filtering.py

# Run main application
python src/main.py --days 7

# Run tests
python -m pytest tests/ -v
```

### Imports
```python
# In src/ files
from .gmail_client import GmailClient

# In utils/ files
import sys
sys.path.insert(0, '../src')
from gmail_client import GmailClient
```

### Configuration
```python
# Always use relative paths
credentials_path = 'config/credentials.json'
token_path = 'config/token.json'

# For utils/ scripts
credentials_path = '../config/credentials.json'
```

## 🚨 Security Checklist

- [ ] Sensitive files in `config/` directory
- [ ] No hardcoded API keys in source code
- [ ] Use environment variables for secrets
- [ ] Update `.gitignore` for new sensitive files

## 📝 Before Committing

```bash
# Check imports work
python -c "from src.main import main; print('✅ OK')"

# Test configuration
python utils/test_filtering.py

# Check for secrets in code
grep -r "api_key\|password\|secret" src/
```

## 🔄 Adding New Features

1. Plan in `.cursor/scratchpad.md`
2. Code in `src/`
3. Test in `tests/`
4. Document in `README.md`
5. Configure in `environment.template`

---

See [MAINTENANCE.md](../MAINTENANCE.md) for detailed guidelines. 