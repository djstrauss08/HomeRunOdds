# 🔒 Security Setup Guide - API Key Configuration

Complete security guide for safely configuring and managing your The Odds API key with the MLB Home Run Props system.

## 🚨 Critical Security Principles

### Never Hardcode API Keys

❌ **NEVER DO THIS:**
```python
# WRONG - Never hardcode API keys
API_KEY = "fb3783a6282bef18eb049a90d1b1248d"
```

✅ **ALWAYS DO THIS:**
```python
# CORRECT - Use environment variables
API_KEY = os.getenv('THE_ODDS_API_KEY')
```

## 🛠️ Local Development Setup

### Option 1: Environment Variables (Recommended)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export THE_ODDS_API_KEY="your-api-key-here"

# Reload your shell
source ~/.zshrc  # or ~/.bashrc
```

### Option 2: .env File (Alternative)

1. Create a `.env` file in your project root:
```bash
THE_ODDS_API_KEY=your-api-key-here
```

2. Add `.env` to your `.gitignore`:
```bash
echo ".env" >> .gitignore
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

4. Load in your Python script:
```python
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('THE_ODDS_API_KEY')
```

### Verification

Test that your API key is properly configured:

```bash
# Check environment variable
echo $THE_ODDS_API_KEY

# Test with the system
python3 -c "import os; print('✅ API key configured' if os.getenv('THE_ODDS_API_KEY') else '❌ API key not found')"
```

## 🔐 GitHub Actions Security

### Setting Up Secrets

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click **Settings** tab
   - Click **Secrets and variables** → **Actions**

2. **Add Your API Key Secret**
   - Click **New repository secret**
   - Name: `THE_ODDS_API_KEY`
   - Value: Your actual API key (e.g., `fb3783a6282bef18eb049a90d1b1248d`)
   - Click **Add secret**

3. **Verify Secret Configuration**
   - Secret should appear in the list as `THE_ODDS_API_KEY`
   - Value will show as `***` (hidden for security)

### Using Secrets in Workflows

The GitHub Actions workflow is already configured to use your secret:

```yaml
- name: Update home run props feed
  env:
    THE_ODDS_API_KEY: ${{ secrets.THE_ODDS_API_KEY }}
  run: |
    python3 update_public_feed.py
```

## 🔍 Security Validation

### Code Review Checklist

Before committing code, verify:

- [ ] No API keys in source code
- [ ] No API keys in configuration files
- [ ] No API keys in documentation or examples
- [ ] All API access uses environment variables
- [ ] `.env` files are in `.gitignore`
- [ ] Examples use placeholder values

### Repository Scan

Search your repository for potential security issues:

```bash
# Search for potential API key patterns
grep -r "THE_ODDS_API_KEY.*=" . --exclude-dir=.git
grep -r "[a-f0-9]{32}" . --exclude-dir=.git --exclude="*.md"

# Should only show environment variable usage, not actual keys
```

## 🔄 API Key Management

### Key Rotation

Periodically rotate your API key for security:

1. **Generate New Key**
   - Login to [The Odds API](https://the-odds-api.com/account/)
   - Generate a new API key
   - Keep the old key active temporarily

2. **Update Local Environment**
   ```bash
   export THE_ODDS_API_KEY="new-api-key-here"
   ```

3. **Update GitHub Secret**
   - Go to repository Settings → Secrets
   - Click **THE_ODDS_API_KEY**
   - Click **Update secret**
   - Enter new API key value

4. **Test New Key**
   ```bash
   python3 homerun_summary.py
   ```

5. **Deactivate Old Key**
   - Once confirmed working, deactivate old key in The Odds API dashboard

### Multiple Environment Keys

For different environments, use descriptive secret names:

```yaml
# GitHub Secrets
ODDS_API_KEY_PROD
ODDS_API_KEY_DEV
ODDS_API_KEY_TEST
```

## 🚨 Incident Response

### If API Key is Compromised

**Immediate Actions:**

1. **Deactivate Compromised Key**
   - Login to The Odds API dashboard
   - Deactivate the compromised key immediately

2. **Generate New Key**
   - Create a new API key
   - Update all systems with new key

3. **Review Usage**
   - Check API usage logs for suspicious activity
   - Monitor for unusual consumption patterns

4. **Update Documentation**
   - Ensure all team members are aware
   - Update any deployment procedures

### Prevention Measures

- **Regular Audits**: Review code for hardcoded secrets monthly
- **Automated Scanning**: Use tools like GitLeaks or TruffleHog
- **Access Logging**: Monitor API usage patterns
- **Team Training**: Educate team members on security best practices

## 🔧 Advanced Security Features

### IP Restrictions (If Available)

Some API providers allow IP restrictions:

1. Check if The Odds API supports IP allowlists
2. Add GitHub Actions IP ranges if available
3. Add your development environment IPs

### Usage Monitoring

Set up alerts for unusual activity:

```python
# Example monitoring script
import os
import requests

def check_api_usage():
    """Monitor API usage and alert on unusual patterns"""
    # Implementation depends on The Odds API dashboard/monitoring features
    pass
```

### Backup Authentication

Consider setting up backup authentication methods:

- Secondary API key for emergencies
- Different account for production vs development
- Contact information for API provider support

## 📋 Security Checklist

### Before First Deployment

- [ ] API key stored in GitHub Secrets
- [ ] No hardcoded keys in source code
- [ ] Local environment uses environment variables
- [ ] `.env` files excluded from version control
- [ ] Team members trained on security practices

### Regular Security Maintenance

- [ ] Monthly code audit for secrets
- [ ] quarterly API key rotation
- [ ] Monitor API usage patterns
- [ ] Review GitHub Actions logs
- [ ] Update security documentation

### Emergency Preparedness

- [ ] API key rotation procedure documented
- [ ] Emergency contact information available
- [ ] Backup API key ready
- [ ] Incident response plan defined

## 🔗 Security Resources

### Tools

- **GitLeaks**: Scan for secrets in Git repositories
- **TruffleHog**: Search for high entropy strings and secrets
- **GitHub Secret Scanning**: Automatic detection of known secret patterns

### Documentation

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Environment Variables Best Practices](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

## 💡 Security Tips

1. **Use Unique Keys**: Different API keys for different projects
2. **Monitor Usage**: Regular checks of API consumption
3. **Least Privilege**: Only grant necessary permissions
4. **Regular Rotation**: Change keys periodically
5. **Team Education**: Keep everyone informed about security practices

## 🚨 Common Security Mistakes

### Mistake 1: Committing .env Files
```bash
# Add to .gitignore
.env
.env.local
.env.*.local
```

### Mistake 2: Logging API Keys
```python
# BAD
print(f"Using API key: {API_KEY}")

# GOOD
print("✅ API key loaded successfully" if API_KEY else "❌ API key not found")
```

### Mistake 3: Sharing Keys in Documentation
```markdown
<!-- BAD -->
Set your API key: THE_ODDS_API_KEY=abc123...

<!-- GOOD -->
Set your API key: THE_ODDS_API_KEY=your-api-key-here
```

Your API key security is now properly configured! 🔒 Remember: security is an ongoing process, not a one-time setup. 