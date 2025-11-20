"""
Basic usage example for FDS-Dev

This demonstrates the quickest way to start using FDS-Dev
for documentation linting and translation.
"""

# [!] Example 1: Basic Linting
# Run FDS on a single Markdown file

from fds_dev.main import lint_file
from pathlib import Path

# Lint a README file
result = lint_file(Path("README.md"))
print(f"[+] Linting result: {len(result.issues)} issues found")

for issue in result.issues[:3]:  # Show first 3 issues
    print(f"  [-] {issue.severity}: {issue.message} (line {issue.line})")


# [!] Example 2: Translation (Rule-based)
# Translate non-English comments to English

from fds_dev.i18n.translation import TranslationEngine

engine = TranslationEngine(mode='rule_based')
korean_text = "이것은 한국어 주석입니다"
english_text = engine.translate(korean_text, source_lang='ko', target_lang='en')
print(f"\n[+] Translation: {korean_text} -> {english_text}")


# [!] Example 3: Code Comment Parsing
# Extract and analyze comments from source code

from fds_dev.i18n.code_comment_parser import CodeCommentParser

parser = CodeCommentParser()
python_code = '''
def hello():
    # 이 함수는 인사를 출력합니다
    print("Hello, world!")
'''

comments = parser.parse_string(python_code)
for comment in comments:
    print(f"\n[+] Found comment at line {comment['line']}: {comment['text']}")
    if comment.get('needs_translation'):
        print(f"  [!] Needs translation from {comment['detected_lang']}")


# [!] Example 4: Using Configuration File
# Load settings from .fdsrc.yaml

import yaml
from pathlib import Path

config_path = Path(".fdsrc.yaml")
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
    print(f"\n[+] Loaded config: {config.get('linter', {}).get('level', 'standard')}")


# [!] Example 5: CLI Usage (recommended for most users)
# Run these commands in your terminal:

print("""
\n[>] Quickstart CLI Commands:

1. Lint your documentation:
   $ fds lint README.md

2. Lint with strict mode:
   $ fds lint --strict docs/

3. Check for translation needs:
   $ fds i18n-check src/

4. Initialize config file:
   $ fds init

5. Show version:
   $ fds --version

[>] For more examples, see: https://github.com/flamehaven01/FDS-Dev/tree/main/docs
""")
