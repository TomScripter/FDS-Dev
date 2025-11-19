# FDS-Dev Troubleshooting Guide

## Quick Diagnosis

```bash
# Run diagnostic check
fds --version
python -c "from fds_dev.i18n import TranslationEngine; print('✓ Imports OK')"
pytest tests/test_i18n_translator.py -v
```

---

## Common Issues

### 1. ImportError: cannot import name 'TranslationResult'

**Error Message**:
```
ImportError: cannot import name 'TranslationResult' from 'fds_dev.i18n'
```

**Cause**: Missing or outdated installation

**Solution**:
```bash
# Reinstall in editable mode
cd D:/Sanctum/FDS-Dev
pip install -e .

# Verify installation
python -c "from fds_dev.i18n import TranslationResult; print('✓ Fixed')"
```

---

### 2. API Authentication Errors

#### DeepL API Error (401 Unauthorized)

**Error Message**:
```
ValueError: DeepL API key not found in config or environment variables
```

**Solution**:
```bash
# Set environment variable
export FDS_DEEPL_API_KEY="your-api-key-here"

# Or in .fdsrc.yaml
translator:
  providers:
    deepl:
      api_key: "your-api-key-here"  # Not recommended (use env var)
```

**Verify**:
```bash
echo $FDS_DEEPL_API_KEY
# Should output your API key
```

#### Google Translate Error (NotImplementedError)

**Error Message**:
```
NotImplementedError: Google Cloud Translation API not yet implemented
```

**Cause**: Trying to use `google` provider (not implemented)

**Solution**:
```yaml
# Use google-free instead
translator:
  provider: 'google-free'  # ← Change this
```

---

### 3. Network & Timeout Errors

#### Connection Timeout

**Error Message**:
```
requests.exceptions.Timeout: HTTPSConnectionPool(host='api.deepl.com'): Read timed out
```

**Automatic Retry**:
FDS-Dev automatically retries 3 times with exponential backoff:
```
[Retry 1/3] API call failed: Read timed out. Retrying in 1.0s...
[Retry 2/3] API call failed: Read timed out. Retrying in 2.0s...
[Retry 3/3] API call failed: Read timed out. Retrying in 4.0s...
[!] Max retries (3) reached. Giving up.
```

**Manual Solutions**:

1. **Check internet connection**:
   ```bash
   ping api.deepl.com
   ```

2. **Increase timeout** (modify `translator.py`):
   ```python
   # Change timeout from 10s to 30s
   response = requests.post(api_url, data=payload, timeout=30)
   ```

3. **Use different provider**:
   ```yaml
   translator:
     provider: 'mymemory'  # Often more reliable
   ```

#### Rate Limiting (429 Too Many Requests)

**Error Message**:
```
requests.exceptions.HTTPError: 429 Client Error: Too Many Requests
```

**Cause**: API rate limit exceeded

**Solutions**:

1. **Wait before retrying** (automatic with exponential backoff)

2. **Add delays between translations**:
   ```python
   # Edit translator.py translate() method
   import time
   time.sleep(0.5)  # 500ms delay between requests
   ```

3. **Upgrade API plan**:
   ```bash
   # DeepL: https://www.deepl.com/pro
   # Or switch to free provider:
   fds translate --provider mymemory
   ```

---

### 4. Translation Quality Issues

#### Low Quality Score (Ω < 0.75)

**Warning Message**:
```
[✗] [Ω=0.62] (L42): 복잡한 문장 구조...
  - Issue: Semantic meaning may be lost in translation
  - Recommendation: Consider rephrasing or adding clarification
```

**Solutions**:

1. **Switch to AI mode**:
   ```bash
   fds translate README.md --mode ai
   ```

2. **Lower threshold** (if acceptable):
   ```bash
   fds translate README.md --quality-threshold 0.60
   ```

3. **Manual review and edit**:
   ```bash
   # Preview first
   fds translate README.md
   # Then manually fix low-quality translations
   ```

#### Preserved Terms Not Working

**Issue**: Technical terms like `CamelCase` are being translated

**Check**:
```python
python -c "
from fds_dev.i18n import TechnicalTermDatabase
print(TechnicalTermDatabase.should_preserve('CamelCase'))  # Should be True
"
```

**Solution**:
```python
# Add custom terms to PRESERVE_TERMS
# Edit fds_dev/i18n/translator.py

PRESERVE_TERMS = {
    # ... existing terms
    'MyCustomClass',  # Add your custom terms here
    'custom_function',
}
```

---

### 5. File Processing Errors

#### UnicodeDecodeError

**Error Message**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x89 in position 0
```

**Cause**: File encoding mismatch

**Solution**:
```python
# FDS-Dev auto-detects encoding, but you can force it
# Edit file manually with correct encoding:

# Open with specific encoding
with open('file.py', 'r', encoding='cp949') as f:
    content = f.read()

# Save as UTF-8
with open('file.py', 'w', encoding='utf-8') as f:
    f.write(content)
```

#### SyntaxError During Parsing

**Error Message**:
```
SyntaxError: invalid syntax
```

**Cause**: Python file has syntax errors

**Solution**:
1. **Fix syntax errors first**:
   ```bash
   python file.py  # Check for syntax errors
   ```

2. **Skip file** (FDS-Dev auto-skips invalid files):
   ```
   Warning: Failed to parse file.py: invalid syntax
   # File is skipped, others continue
   ```

---

### 6. Test Failures

#### pytest Import Errors

**Error Message**:
```
ImportError: cannot import name 'CommentNode' from 'fds_dev.i18n'
```

**Solution**:
```bash
# Ensure package is installed
pip install -e .

# Verify __init__.py exports
cat fds_dev/i18n/__init__.py | grep CommentNode
# Should show: from .code_comment_parser import CommentNode
```

#### Test Assertion Failures

**Example**:
```
AssertionError: assert 'function' in '함수를 호출.'
```

**Cause**: Rule-based translation has limited vocabulary

**Not a bug**: This is expected behavior. Tests validate that:
- AI mode works (high quality)
- Rule-based mode has known limitations

**Action**: Tests are informational, not production blockers

---

## API-Specific Troubleshooting

### DeepL API Issues

#### Free Tier Limit Reached

**Error**:
```
{"message":"Quota exceeded"}
```

**Solutions**:
1. **Wait until next month** (free tier resets monthly)
2. **Upgrade to paid tier**
3. **Switch to alternative**:
   ```yaml
   translator:
     provider: 'google-free'  # No limits
   ```

#### Invalid Language Code

**Error**:
```
{"message":"Value for 'target_lang' not supported"}
```

**Cause**: DeepL uses uppercase language codes

**Fixed in code** (automatic conversion):
```python
# Automatically converts to uppercase
payload["target_lang"] = target_lang.upper()  # 'en' → 'EN'
```

### MyMemory API Issues

#### Daily Limit Exceeded

**Error**:
```
{"responseStatus":403,"responseDetails":"DAILY LIMIT REACHED"}
```

**Solutions**:
1. **Add email to config** (increases limit to 10,000 chars/day):
   ```yaml
   translator:
     providers:
       mymemory:
         email: 'your@email.com'
   ```

2. **Wait 24 hours** for reset

3. **Switch provider**:
   ```bash
   fds translate --provider deepl
   ```

#### Poor Translation Quality

**Issue**: MyMemory translations are less accurate than DeepL

**Expected**: MyMemory is free but lower quality

**Solution**: Use DeepL or AI mode for important translations

### LibreTranslate Issues

#### Connection Refused

**Error**:
```
requests.exceptions.ConnectionError: Connection refused
```

**Cause**: LibreTranslate server not running

**Solution**:
```bash
# Start LibreTranslate server
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate

# Or install locally
pip install libretranslate
libretranslate
```

**Verify**:
```bash
curl http://localhost:5000/languages
# Should return JSON array of supported languages
```

---

## Performance Issues

### Slow Translation Speed

**Issue**: Takes 30+ seconds per file

**Diagnosis**:
```bash
# Check API latency
time fds translate test.py --in-place

# Output example:
# real    0m32.451s  ← Too slow
```

**Solutions**:

1. **Enable caching** (automatic):
   ```bash
   # First run: slow (API calls)
   fds translate src/ --recursive

   # Second run: fast (cache hits)
   fds translate src/ --recursive  # ~80% faster
   ```

2. **Use batch processing** (future feature):
   ```python
   # Translate multiple comments in one API call
   results = translator.translate_batch(comments)
   ```

3. **Parallel processing** (future feature):
   ```bash
   # Process files in parallel
   fds translate src/ --workers 4
   ```

### High Memory Usage

**Issue**: Process uses >1GB RAM

**Cause**: Large files with many comments

**Solution**:
```bash
# Process files one at a time
for file in src/*.py; do
    fds translate "$file" --in-place
done
```

---

## Configuration Issues

### .fdsrc.yaml Not Found

**Warning**:
```
Warning: .fdsrc.yaml not found, using defaults
```

**Not an error**: FDS-Dev works with defaults

**To customize**:
```bash
# Create config file
cat > .fdsrc.yaml <<EOF
translator:
  provider: 'deepl'
  mode: 'ai'
  quality_threshold: 0.75
EOF
```

### Invalid YAML Syntax

**Error**:
```
yaml.scanner.ScannerError: while scanning a simple key
```

**Cause**: YAML syntax error

**Solution**:
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.fdsrc.yaml'))"

# Common errors:
# - Tabs instead of spaces (use 2 spaces)
# - Missing quotes around strings with special chars
# - Incorrect indentation
```

---

## Debugging Tools

### Enable Verbose Logging

```bash
# Run with verbose output
fds translate README.md -v

# Or modify translator.py to add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Translation Cache

```bash
# View cache contents
cat .fds_cache.json | python -m json.tool

# Clear cache
rm .fds_cache.json
```

### Test Individual Components

```python
# Test language detection
python -c "
from fds_dev.i18n import LanguageDetector
detector = LanguageDetector()
result = detector.detect('한국어 텍스트')
print(f'Language: {result.language}, Confidence: {result.confidence}')
"

# Test translation
python -c "
from fds_dev.i18n import TranslationEngine
engine = TranslationEngine(mode='rule_based')
result = engine.translate('함수', 'ko', 'en')
print(f'Translation: {result.translated}')
"

# Test quality validation
python -c "
from fds_dev.i18n import TranslationQualityOracle
oracle = TranslationQualityOracle()
assessment = oracle.evaluate('test', 'test', 'en')
print(f'Omega: {assessment.omega_score}')
"
```

---

## Emergency Recovery

### Complete Reinstall

```bash
# Remove existing installation
pip uninstall fds-dev -y

# Clear cache
rm -rf ~/.cache/pip/wheels/fds-dev*
rm -rf build/ dist/ *.egg-info/

# Reinstall
cd D:/Sanctum/FDS-Dev
pip install -e .

# Verify
fds --version
pytest tests/ -v
```

### Restore Original Files

```bash
# If translations went wrong, restore from git
git checkout -- src/

# Or use backup (if you created one)
cp -r src.backup/ src/
```

### Contact Support

If issues persist:

1. **Check GitHub Issues**: https://github.com/flamehaven01/FDS-Dev/issues
2. **Create new issue** with:
   - Error message (full traceback)
   - FDS-Dev version (`fds --version`)
   - Python version (`python --version`)
   - Operating system
   - Steps to reproduce

---

## Known Limitations

### Current Limitations (v0.1.x)

1. **AI Mode**: Not fully implemented (uses simulation)
   - **Workaround**: Use DeepL provider for production quality

2. **Batch Translation**: Not implemented
   - **Workaround**: Caching makes repeated runs fast

3. **Progress Bars**: Not implemented
   - **Workaround**: Use verbose mode (`-v`)

4. **Parallel Processing**: Not implemented
   - **Workaround**: Run multiple `fds` processes manually

### Planned for v0.2.0

- Real AI integration (OpenAI, Anthropic, Google Gemini)
- Batch translation API support
- Progress bars with `tqdm`
- Parallel file processing with `--workers`
- Translation memory (TM) support
- Glossary/terminology management

---

## FAQ

**Q: Why does rule-based mode not translate some words?**

A: Rule-based mode has limited vocabulary (20+ Korean terms). Use AI mode or DeepL for comprehensive coverage.

**Q: Can I use FDS-Dev offline?**

A: Yes, with `--mode rule_based` or `--provider libretranslate` (self-hosted).

**Q: How do I preserve custom technical terms?**

A: Edit `fds_dev/i18n/translator.py` and add terms to `PRESERVE_TERMS` set.

**Q: What's the difference between `google` and `google-free`?**

A: `google` is official API (not implemented), `google-free` is unofficial free API (works but unstable).

**Q: Can I translate languages other than Korean?**

A: Yes! FDS-Dev supports: Korean (ko), Japanese (ja), Chinese (zh), Spanish (es), French (fr), German (de), Russian (ru).

**Q: How accurate is the quality score (Ω)?**

A: Quality scores are heuristic-based estimates. Manual review recommended for critical translations.

---

## Diagnostic Checklist

Before reporting a bug, please check:

- [ ] FDS-Dev is installed: `pip list | grep fds-dev`
- [ ] Python version ≥ 3.9: `python --version`
- [ ] Environment variables set (if using DeepL): `echo $FDS_DEEPL_API_KEY`
- [ ] Internet connection (if using online APIs): `ping api.deepl.com`
- [ ] `.fdsrc.yaml` syntax valid: `python -c "import yaml; yaml.safe_load(open('.fdsrc.yaml'))"`
- [ ] Tests passing: `pytest tests/ -v` (100/105 expected)
- [ ] No conflicting installations: `pip list | grep trans`

---

**Last Updated**: 2025-11-19
**Version**: 1.0
**Related Docs**: TRANSLATION_ALGORITHM.md, README.md
