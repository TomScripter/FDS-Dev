# Security Checklist for FDS-Dev

## Pre-Commit (Developer)

- [ ] No hardcoded API keys, tokens, or passwords in code
- [ ] Environment variables used for sensitive config
- [ ] `.env` files added to `.gitignore`
- [ ] Run `pre-commit run --all-files` before committing
- [ ] No large binary files committed

## Code Review (Reviewer)

- [ ] Check for accidental secret exposure
- [ ] Validate input sanitization for user-provided data
- [ ] Verify external API calls use HTTPS
- [ ] Confirm error messages don't leak sensitive info
- [ ] Test edge cases and error handling

## CI/CD Pipeline

- [ ] All tests pass
- [ ] Linters (ruff, flake8) pass
- [ ] Coverage meets threshold (>=70%)
- [ ] No security vulnerabilities in dependencies (Dependabot)
- [ ] Secrets stored in GitHub Secrets (not in code)

## Release Preparation

- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Security fixes documented (if any)
- [ ] Tag follows `vX.Y.Z` pattern
- [ ] GitHub Release notes include security warnings

## Repository Settings (Maintainer)

### Branch Protection (main)
- [ ] Require pull request reviews (min 1)
- [ ] Require status checks to pass
- [ ] Require branches to be up to date
- [ ] Require signed commits (recommended)
- [ ] Include administrators in restrictions

### Security Features
- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] Secret scanning enabled
- [ ] Code scanning (CodeQL) enabled
- [ ] Private vulnerability reporting enabled

### Secrets Management
- [ ] `PYPI_API_TOKEN` stored in Secrets
- [ ] No plain-text secrets in repository
- [ ] Environment-specific secrets use Environments

## Incident Response

### If Secret Leaked
1. **IMMEDIATELY** rotate compromised credential
2. Check git history: `git log -S "secret_string"`
3. Remove from history if found:
   ```bash
   # Option 1: git-filter-repo (recommended)
   git filter-repo --path-match 'file_with_secret' --invert-paths

   # Option 2: BFG Repo-Cleaner
   bfg --delete-files file_with_secret
   ```
4. Force push (DANGEROUS - coordinate with team):
   ```bash
   git push --force-with-lease
   ```
5. Notify all collaborators
6. Create security advisory if public exposure

### If Vulnerability Reported
1. Acknowledge within 72 hours
2. Triage severity (Critical/High/Medium/Low)
3. Create private security advisory
4. Develop and test fix
5. Release patch version
6. Publish advisory after fix deployed

## Compliance (for Enterprise Users)

- [ ] Data residency requirements met
- [ ] GDPR compliance (if handling EU data)
- [ ] HIPAA compliance (if handling health data)
- [ ] SOC 2 audit trail (if applicable)
- [ ] License compatibility verified

## Regular Maintenance

### Weekly
- [ ] Review Dependabot PRs
- [ ] Check security advisory dashboard

### Monthly
- [ ] Audit GitHub Actions logs
- [ ] Review access permissions
- [ ] Update security documentation

### Quarterly
- [ ] Full dependency audit
- [ ] Security policy review
- [ ] Incident response drill (simulated)

---

**Last Updated**: 2025-11-20
**Checklist Version**: 1.0
