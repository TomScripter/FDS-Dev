# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.2   | :white_check_mark: |
| < 0.0.2 | :x:                |

## Reporting a Vulnerability

**DO NOT** open a public issue for security vulnerabilities.

### Report via GitHub Security Advisory
1. Go to [Security Advisories](https://github.com/flamehaven01/FDS-Dev/security/advisories)
2. Click "Report a vulnerability"
3. Provide detailed description, impact, and reproduction steps

### Alternative Contact
- Email: `flamehaven01@users.noreply.github.com`
- Subject: `[SECURITY] FDS-Dev Vulnerability Report`

### Expected Response Time
- **Acknowledgment**: Within 72 hours
- **Initial Assessment**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

## Security Best Practices

### For Users
1. **Never commit API keys** to `.fdsrc.yaml`
   ```yaml
   translation:
     provider: deepl
     api_key: null  # Use FDS_DEEPL_API_KEY environment variable
   ```

2. **Use environment variables**
   ```bash
   export FDS_DEEPL_API_KEY="your-key-here"
   ```

3. **Keep FDS-Dev updated**
   ```bash
   pip install --upgrade fds-dev
   ```

### For Contributors
1. **Run security scans** before submitting PRs
2. **Never hardcode secrets** in code or tests
3. **Review dependencies** for known vulnerabilities
4. **Use `.env` files** (add to `.gitignore`)

## Automated Security

### Dependabot
- Enabled for security updates
- Auto-creates PRs for vulnerable dependencies
- Weekly scan schedule

### Secret Scanning (GitHub)
- Automatically detects committed secrets
- Blocks pushes containing common token patterns
- Configure in Repository Settings → Code security

## Vulnerability Disclosure

After a vulnerability is fixed:
1. Security advisory published
2. CVE assigned (if applicable)
3. Release notes include security fixes
4. Users notified via GitHub Releases

## Acknowledgments

We appreciate responsible disclosure. Contributors who report valid vulnerabilities will be:
- Credited in CHANGELOG.md (with permission)
- Listed in security advisory (optional)

---

**Last Updated**: 2025-11-20
**Policy Version**: 1.0
