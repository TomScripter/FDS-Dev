# Translation Algorithm Documentation

## Overview

FDS-Dev uses a sophisticated multi-stage translation pipeline that combines rule-based translation, AI-powered translation (optional), and meta-cognitive quality validation to translate code comments and documentation from any language to English.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FDS-Dev Translation Pipeline                          │
└─────────────────────────────────────────────────────────────────────────┘

    INPUT: Python/Markdown Files with Non-English Comments
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: Language Detection                                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ LanguageDetector.detect()                                         │  │
│  │  • Script Detection (Hangul, Kanji, Hiragana, Latin)             │  │
│  │  • Language Markers (particles, common words)                     │  │
│  │  • Confidence Scoring (0.0-1.0)                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: LanguageDetectionResult(language='ko', confidence=0.95)         │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: Code Parsing & Comment Extraction                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ CodeCommentParser.parse_file()                                    │  │
│  │  • AST-based Python parsing                                       │  │
│  │  • Extract inline comments (#)                                    │  │
│  │  • Extract docstrings (""")                                       │  │
│  │  • Extract Markdown paragraphs                                    │  │
│  │  • Preserve line numbers & context                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: ParsedCodeFile(comments=[], docstrings=[])                      │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: Technical Term Extraction                                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ TranslationEngine._extract_preservable_terms()                    │  │
│  │  • Detect CamelCase (MyClass)                                     │  │
│  │  • Detect snake_case (my_function)                                │  │
│  │  • Detect UPPER_CASE (CONSTANT_VALUE)                             │  │
│  │  • Check against TechnicalTermDatabase                            │  │
│  │  • Preserve: function, class, API, HTTP, JSON, etc.               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: preserved_terms=['CamelCase', 'function', 'API']                │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: Translation Execution                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ TranslationEngine.translate() - Multi-Backend                     │  │
│  │                                                                     │  │
│  │  MODE 1: Rule-Based                                                │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │ • Apply STANDARD_TRANSLATIONS (함수→function)                 │ │  │
│  │  │ • Transform sentence endings (입니다→.)                       │ │  │
│  │  │ • Preserve technical terms                                    │ │  │
│  │  │ • Confidence: 0.6                                             │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  MODE 2: AI-Powered (OpenAI/Anthropic/DeepL)                       │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │ • Construct LLM prompt with context                          │ │  │
│  │  │ • Specify preserved terms                                     │ │  │
│  │  │ • Call API with retry logic (3 attempts)                     │ │  │
│  │  │ • Exponential backoff: 1s → 2s → 4s                         │ │  │
│  │  │ • Confidence: 0.95                                            │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  MODE 3: Hybrid                                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │ • Try AI first, fallback to rule-based on failure            │ │  │
│  │  │ • Best of both worlds                                         │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: TranslationResult(translated="call the function", conf=0.95)   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 5: Meta-Cognitive Quality Validation                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ TranslationQualityOracle.evaluate()                               │  │
│  │                                                                     │  │
│  │  5-Dimensional Quality Tensor:                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │ 1. Semantic Fidelity (30%)                                   │ │  │
│  │  │    • Length ratio check                                       │ │  │
│  │  │    • Keyword overlap analysis                                 │ │  │
│  │  │    • Structural similarity (punctuation)                      │ │  │
│  │  │                                                               │ │  │
│  │  │ 2. Technical Accuracy (25%)                                  │ │  │
│  │  │    • Preserved terms verification                             │ │  │
│  │  │    • CamelCase/snake_case integrity                          │ │  │
│  │  │    • Error pattern detection                                  │ │  │
│  │  │                                                               │ │  │
│  │  │ 3. Fluency (20%)                                             │ │  │
│  │  │    • Sentence structure check                                 │ │  │
│  │  │    • Capitalization validation                                │ │  │
│  │  │    • Common English pattern matching                          │ │  │
│  │  │                                                               │ │  │
│  │  │ 4. Consistency (15%)                                         │ │  │
│  │  │    • Term translation consistency                             │ │  │
│  │  │    • Cross-file terminology uniformity                        │ │  │
│  │  │                                                               │ │  │
│  │  │ 5. Context Awareness (10%)                                   │ │  │
│  │  │    • Appropriate for code comments                            │ │  │
│  │  │    • Conciseness check                                        │ │  │
│  │  │    • Professional tone validation                             │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                     │  │
│  │  Ω Score Calculation:                                              │  │
│  │    Ω = 0.30×Semantic + 0.25×Technical + 0.20×Fluency +            │  │
│  │        0.15×Consistency + 0.10×Context                             │  │
│  │                                                                     │  │
│  │  Quality Gate: Ω ≥ 0.75 (default threshold)                        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: QualityAssessment(omega=0.87, should_retranslate=False)        │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 6: File Reconstruction                                            │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ CodeCommentParser.reconstruct_file()                              │  │
│  │  • Replace inline comments with translations                      │  │
│  │  • Replace docstrings with translations                           │  │
│  │  • Preserve code structure & formatting                           │  │
│  │  • Maintain original line numbers                                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  Output: Translated file with preserved code structure                   │
└─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
    OUTPUT: Python/Markdown Files with English Comments
```

---

## Step-by-Step Workflow

### Example: Translating Korean Comment to English

**Input**:
```python
def process_data():
    # 데이터를 처리합니다
    return result
```

#### Step 1: Language Detection

```python
detector = LanguageDetector()
result = detector.detect("데이터를 처리합니다")

# Output:
# LanguageDetectionResult(
#     language='ko',
#     confidence=0.95,
#     script='hangul',
#     samples=['데이터를 처리합니다']
# )
```

**How it works**:
1. Character range detection: `\uAC00-\uD7AF` → Hangul detected
2. Language marker check: "합니다" found → Korean confirmed
3. Confidence calculation: Script (1.0) + Markers (0.9) / 2 = 0.95

#### Step 2: Code Parsing

```python
parser = CodeCommentParser()
parsed = parser.parse_file("example.py")

# Output:
# ParsedCodeFile(
#     comments=[
#         CommentNode(
#             node_type='inline_comment',
#             content='데이터를 처리합니다',
#             line_number=2,
#             column_offset=4,
#             context='def process_data():\n    # 데이터를 처리합니다'
#         )
#     ]
# )
```

**How it works**:
1. AST parsing of Python file
2. Extract comments using regex: `r"#\s*(.+)$"`
3. Skip comments inside strings (quote counting)
4. Capture surrounding context (±2 lines)

#### Step 3: Technical Term Extraction

```python
engine = TranslationEngine(mode='rule_based')
terms = engine._extract_preservable_terms("데이터를 처리합니다")

# Output: []
# (No CamelCase/snake_case/UPPER_CASE terms in this example)
```

**How it works**:
1. Regex patterns:
   - CamelCase: `r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b"`
   - snake_case: `r"\b[a-z]+_[a-z_]+\b"`
   - UPPER_CASE: `r"\b[A-Z][A-Z_]+\b"`
2. Check against `TechnicalTermDatabase.PRESERVE_TERMS`
3. Return unique list of terms to preserve

#### Step 4: Translation (Rule-Based)

```python
result = engine.translate(
    text="데이터를 처리합니다",
    source_lang='ko',
    target_lang='en'
)

# Internal steps:
# 1. Apply STANDARD_TRANSLATIONS
#    "데이터" → not in dictionary (keep as-is)
#
# 2. Transform sentence endings
#    "합니다" → "." (regex: r"합니다\.?$")
#
# 3. Output: "데이터를 처리."
```

**Standard Translations (Korean)**:
```python
STANDARD_TRANSLATIONS['ko'] = {
    '함수': 'function',
    '클래스': 'class',
    '메서드': 'method',
    '변수': 'variable',
    '매개변수': 'parameter',
    '반환': 'return',
    # ... 20+ more terms
}
```

#### Step 4b: Translation (AI-Powered)

```python
# With AI mode (requires API key)
engine = TranslationEngine(mode='ai', api_key='sk-...')
result = engine.translate(
    text="데이터를 처리합니다",
    source_lang='ko',
    target_lang='en'
)

# Internal steps:
# 1. Construct prompt:
#    "Translate from ko to en. Preserve: []
#     Rules: Professional developer English, concise
#     Text: 데이터를 처리합니다"
#
# 2. Call API (with retry logic):
#    - Attempt 1: Immediate
#    - Attempt 2: After 1s delay (if failed)
#    - Attempt 3: After 2s delay (if failed)
#
# 3. Output: "Process the data."
```

**Retry Logic**:
```python
@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def translate(self, text, source_lang, target_lang):
    response = requests.post(api_url, data=payload, timeout=10)
    response.raise_for_status()
    return response.json()['translations'][0]['text']
```

#### Step 5: Quality Validation

```python
oracle = TranslationQualityOracle(strict_threshold=0.75)
assessment = oracle.evaluate(
    original="데이터를 처리합니다",
    translated="Process the data.",
    source_lang='ko',
    preserved_terms=[]
)

# Detailed calculation:
```

**5D Quality Tensor Calculation**:

1. **Semantic Fidelity (Weight: 30%)**:
   ```python
   # Length ratio
   len_ratio = min(11, 19) / max(11, 19) = 0.58

   # Keyword overlap (words longer than 3 chars)
   original_keywords = {'데이터를'}  # 1 word
   translated_keywords = {'Process', 'data'}  # 2 words
   overlap = 0 / 1 = 0.0  # Different languages, no overlap expected

   # Punctuation similarity
   orig_punct = set()  # No punctuation
   trans_punct = {'.'}  # One period
   punct_sim = 0 / 1 = 0.0

   # Final score
   semantic_fidelity = 0.58*0.4 + 0.0*0.4 + 0.0*0.2 = 0.23
   ```

2. **Technical Accuracy (Weight: 25%)**:
   ```python
   # No preserved terms to check
   # Default for no terms: 0.9
   technical_accuracy = 0.9
   ```

3. **Fluency (Weight: 20%)**:
   ```python
   fluency = 1.0  # Perfect English sentence

   # Checks:
   # - Capitalized: ✓ "Process"
   # - Ends with period: ✓
   # - Reasonable length (4 words): ✓
   # - Common English patterns: ✓ "the"
   # - No repeated words: ✓
   ```

4. **Consistency (Weight: 15%)**:
   ```python
   consistency = 0.8  # Default assumption (first translation)
   ```

5. **Context Awareness (Weight: 10%)**:
   ```python
   context_awareness = 0.8  # Base score

   # Checks:
   # - Concise (4 words < 30): ✓ (+0)
   # - Professional tone: ✓ (+0)
   # - No casual language: ✓ (+0)
   # - Technical terms present: ✗ (no penalty for comments)
   ```

**Ω Score Calculation**:
```python
Ω = 0.23×0.30 + 0.9×0.25 + 1.0×0.20 + 0.8×0.15 + 0.8×0.10
  = 0.069 + 0.225 + 0.200 + 0.120 + 0.080
  = 0.694

# Result: FAIL (Ω < 0.75 threshold)
# Recommendation: Retranslate with AI mode or adjust threshold
```

**Quality Gate Decision**:
```python
if assessment.omega_score >= 0.75:
    # Accept translation
    node.translated = result.translated
else:
    # Reject or retranslate
    if mode == 'hybrid':
        # Try AI translation
        result = engine._ai_translate(...)
    else:
        # Keep original or mark for review
        print(f"Warning: Low quality (Ω={assessment.omega_score:.2f})")
```

#### Step 6: File Reconstruction

```python
# Apply translation to file
parsed.comments[0].translated = "Process the data."

# Reconstruct file
reconstructed = parser.reconstruct_file(parsed)

# Output:
# def process_data():
#     # Process the data.
#     return result
```

**Reconstruction Algorithm**:
```python
def reconstruct_file(parsed_file):
    lines = parsed_file.original_lines.copy()

    # Replace inline comments
    for comment in parsed_file.comments:
        if comment.translated:
            line_idx = comment.line_number - 1
            original_line = lines[line_idx]

            # Find comment position
            comment_match = re.search(r"#\s*.+$", original_line)
            before_comment = original_line[:comment_match.start()]

            # Replace with translation
            lines[line_idx] = f"{before_comment}# {comment.translated}\n"

    return "".join(lines)
```

---

## Translation Backends

### 1. Google Translate (Free) - `google-free`

**Provider**: Unofficial py-googletrans library
**API Key**: Not required
**Cost**: Free
**Stability**: Unstable (may break without notice)

**Configuration**:
```yaml
# .fdsrc.yaml
translator:
  provider: 'google-free'
```

**Pros**:
- No API key needed
- Fast responses
- Good quality for general text

**Cons**:
- Unofficial API (may stop working)
- Rate limiting unpredictable
- No official support

### 2. DeepL - `deepl`

**Provider**: DeepL Official API
**API Key**: Required
**Cost**: Limited free tier, paid plans available
**Stability**: Very high

**Configuration**:
```yaml
# .fdsrc.yaml
translator:
  provider: 'deepl'
  providers:
    deepl:
      api_key: null  # Use FDS_DEEPL_API_KEY env var
      free_api: true  # Set false for paid tier
```

```bash
# Set API key via environment variable
export FDS_DEEPL_API_KEY="your-api-key-here"
```

**Pros**:
- Highest quality translations
- Excellent for technical content
- Official API with SLA
- Preserves formatting well

**Cons**:
- Requires API key
- Paid service (after free tier)

**Retry Configuration**:
```python
# Automatic retry with exponential backoff
@retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
def translate(self, text, source_lang, target_lang):
    # Retry schedule:
    # Attempt 1: Immediate
    # Attempt 2: After 1.0s
    # Attempt 3: After 2.0s (cumulative: 3s)
    # Attempt 4: After 4.0s (cumulative: 7s)
```

### 3. MyMemory - `mymemory`

**Provider**: MyMemory Translation API
**API Key**: Optional (higher limits with email)
**Cost**: Free
**Stability**: Medium

**Configuration**:
```yaml
translator:
  provider: 'mymemory'
  providers:
    mymemory:
      email: 'your@email.com'  # Optional, for higher limits
```

**Pros**:
- Free
- No API key required
- Reasonable quality

**Cons**:
- Rate limits (5000 chars/day without email)
- Lower quality than DeepL
- Occasional downtime

### 4. LibreTranslate - `libretranslate`

**Provider**: Self-hosted open source
**API Key**: Not required
**Cost**: Free (self-hosted)
**Stability**: User-managed

**Configuration**:
```yaml
translator:
  provider: 'libretranslate'
  providers:
    libretranslate:
      url: 'http://localhost:5000/translate'  # Your instance
```

**Setup**:
```bash
# Docker deployment
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate

# Test
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"Hello","source":"en","target":"ko","format":"text"}'
```

**Pros**:
- Fully open source
- Complete control
- No API limits
- Offline capable

**Cons**:
- Requires self-hosting
- Quality depends on model
- Resource intensive

---

## Performance Characteristics

### Latency Breakdown

**Per-Comment Translation**:
```
┌──────────────────────────────────────────────────────┐
│ Stage                          │ Time      │ %      │
├────────────────────────────────┼───────────┼────────┤
│ 1. Language Detection          │   ~50μs   │  <1%   │
│ 2. Code Parsing (AST)          │   ~5ms    │  2%    │
│ 3. Term Extraction             │   ~100μs  │  <1%   │
│ 4. Translation (API call)      │ 200-500ms │ 95%    │
│ 5. Quality Validation          │   ~50μs   │  <1%   │
│ 6. File Reconstruction         │   ~1ms    │  <1%   │
├────────────────────────────────┼───────────┼────────┤
│ TOTAL                          │ ~210-510ms│ 100%   │
└──────────────────────────────────────────────────────┘
```

**Bottleneck**: API call latency (95% of total time)

### Throughput Estimates

**Small File** (10 comments):
- Sequential: ~2-5 seconds
- With caching: ~0.5-1 seconds (80% cache hit)

**Medium File** (50 comments):
- Sequential: ~10-25 seconds
- With batch API: ~5-10 seconds (if supported)

**Large File** (200 comments):
- Sequential: ~40-100 seconds
- Recommended: Use batch processing or parallel workers

### Optimization Strategies

1. **Translation Caching**:
   ```python
   # Cache key: sha256(source_lang:target_lang:text)
   cache_key = f"{source_lang}:{target_lang}:{text[:100]}"

   if cache_key in self.translation_cache:
       return self.translation_cache[cache_key]
   ```

2. **Batch Processing** (Future):
   ```python
   # Translate multiple comments in single API call
   results = translator.translate_batch(
       texts=['comment1', 'comment2', 'comment3'],
       source_lang='ko',
       target_lang='en'
   )
   ```

3. **Parallel Workers** (Future):
   ```python
   # Process files concurrently
   with ProcessPoolExecutor(max_workers=4) as executor:
       futures = [executor.submit(translate_file, f) for f in files]
       results = [f.result() for f in as_completed(futures)]
   ```

---

## Error Handling & Retry Logic

### Retry Strategy

**Exponential Backoff**:
```
Attempt 1: Immediate          (delay: 0s)
Attempt 2: After 1.0s delay   (total: 1s)
Attempt 3: After 2.0s delay   (total: 3s)
Attempt 4: After 4.0s delay   (total: 7s)
MAX RETRIES: 3
```

**Retryable Errors**:
- `requests.exceptions.RequestException`
- `requests.exceptions.Timeout`
- `requests.exceptions.ConnectionError`

**Non-Retryable Errors**:
- `ValueError` (invalid configuration)
- `NotImplementedError` (unsupported provider)
- API authentication errors (401, 403)

### Error Recovery Flow

```
┌──────────────────────────────────────────────────────┐
│ Translation Attempt                                  │
└──────────────────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ API Call       │
         └────────┬───────┘
                  │
         ┌────────▼────────────┐
         │ Success?            │
         └─────┬───────┬───────┘
           Yes │       │ No
               │       │
               │       ▼
               │  ┌─────────────────────┐
               │  │ Retryable Error?    │
               │  └───┬──────────┬──────┘
               │   Yes│          │No
               │      │          │
               │      ▼          ▼
               │  ┌────────┐  ┌──────────────────┐
               │  │ Retry  │  │ Raise Exception  │
               │  │ Count  │  │ (User notified)  │
               │  │ < 3?   │  └──────────────────┘
               │  └─┬────┬─┘
               │    │ Yes│No
               │    │    │
               │    │    ▼
               │    │  ┌──────────────────┐
               │    │  │ Raise Exception  │
               │    │  │ (Max retries)    │
               │    │  └──────────────────┘
               │    │
               │    ▼
               │  ┌──────────────┐
               │  │ Wait delay   │
               │  │ (exponential)│
               │  └──────┬───────┘
               │         │
               │         └───────┐
               │                 │
               ▼                 ▼
         ┌───────────────────────────┐
         │ Return TranslationResult  │
         └───────────────────────────┘
```

### Fallback Mechanisms

**Hybrid Mode**:
```python
if mode == 'hybrid':
    try:
        # Try AI translation first
        result = self._ai_translate(...)
    except Exception as e:
        # Fallback to rule-based
        result = self._rule_based_translate(...)
```

**Graceful Degradation**:
```python
# If all translation attempts fail
if result.translated == text:
    # Keep original text
    result.confidence = 0.1
    result.metadata['note'] = 'Translation failed, kept original'
```

---

## Quality Scoring Formula

### Detailed Ω Score Calculation

**Formula**:
```
Ω = w₁·S + w₂·T + w₃·F + w₄·C + w₅·A

Where:
  S = Semantic Fidelity     (w₁ = 0.30)
  T = Technical Accuracy    (w₂ = 0.25)
  F = Fluency              (w₃ = 0.20)
  C = Consistency          (w₄ = 0.15)
  A = Context Awareness    (w₅ = 0.10)

Score Range: 0.0 ≤ Ω ≤ 1.0
```

### Component Formulas

#### 1. Semantic Fidelity (S)

Measures if meaning is preserved:

```python
S = 0.4·length_ratio + 0.4·keyword_overlap + 0.2·punctuation_similarity

# Length Ratio
length_ratio = min(len(original), len(translated)) / max(len(original), len(translated))

# Keyword Overlap (words > 3 chars)
original_keywords = {w for w in original.split() if len(w) > 3}
translated_keywords = {w for w in translated.split() if len(w) > 3}
keyword_overlap = len(original_keywords ∩ translated_keywords) / len(original_keywords)

# Punctuation Similarity
original_punct = {c for c in original if c in ".,!?;:"}
translated_punct = {c for c in translated if c in ".,!?;:"}
punct_similarity = len(original_punct ∩ translated_punct) / max(1, len(original_punct ∪ translated_punct))
```

**Example**:
```python
# Original: "함수를 호출합니다" (11 chars)
# Translated: "call the function." (19 chars)

length_ratio = 11/19 = 0.58
keyword_overlap = 0.0  # Different languages
punct_similarity = 0.0  # Original has no punctuation

S = 0.4×0.58 + 0.4×0.0 + 0.2×0.0 = 0.23
```

#### 2. Technical Accuracy (T)

Measures if technical terms are preserved:

```python
if preserved_terms is empty:
    T = 0.9  # Default high score (nothing to preserve)
else:
    # Count how many preserved terms appear in translation
    found = sum(1 for term in preserved_terms if term in translated)
    T = found / len(preserved_terms)

    # Penalty for common errors
    if CamelCase broken into words:
        T -= 0.1
    if snake_case broken:
        T -= 0.1
```

**Example**:
```python
# Preserved terms: ['CamelCase', 'snake_case']
# Translated: "Use CamelCase and snake_case here"

found = 2  # Both terms present
T = 2/2 = 1.0
```

#### 3. Fluency (F)

Measures if translation is natural English:

```python
F = 1.0  # Start with perfect score

# Penalties
if len(words) == 1:
    F -= 0.5  # Single word rarely fluent
elif len(words) < 3:
    F -= 0.3  # Very short
elif len(words) > 50:
    F -= 0.1  # Too long

if not capitalized:
    F -= 0.1
if not ends_with_punctuation:
    F -= 0.05
if has_repeated_words:
    F -= 0.1

# Bonuses
if contains_common_english_patterns:  # "the", "is", "are", etc.
    F += 0.1

F = max(0.0, min(1.0, F))  # Clamp to [0, 1]
```

**Example**:
```python
# Translated: "call the function."

len(words) = 3  # No penalty
capitalized = False  # -0.1
ends_with_period = True  # No penalty
repeated_words = False  # No penalty
contains("the") = True  # +0.1

F = 1.0 - 0.1 + 0.1 = 1.0
```

#### 4. Consistency (C)

Measures terminology consistency across translations:

```python
# Default for first translation
C = 0.8

# After multiple translations
consistency_score = consistent_terms / total_terms

# Example:
# If "함수" translated as "function" in 10 places
# but "method" in 2 places:
# consistency_score = 10/12 = 0.83
```

#### 5. Context Awareness (A)

Measures appropriateness for context (code comment):

```python
A = 0.8  # Base score

# Penalties
if len(words) > 30:
    A -= 0.2  # Too long for comment
if contains_casual_language:  # "lol", "btw", etc.
    A -= 0.3

# Bonuses
if contains_technical_terms:
    A += 0.1

A = max(0.0, min(1.0, A))
```

### Quality Thresholds

```
Ω ≥ 0.90  →  EXCELLENT   (Production ready)
0.75 ≤ Ω < 0.90  →  GOOD        (Acceptable)
0.60 ≤ Ω < 0.75  →  FAIR        (Review recommended)
Ω < 0.60  →  POOR       (Retranslate required)
```

**Default Threshold**: 0.75 (configurable via `--quality-threshold`)

---

## Configuration Reference

### .fdsrc.yaml Format

```yaml
# FDS-Dev Configuration File

# Language settings
language:
  source: 'auto'  # Auto-detect or specify: ko, ja, zh, en
  target: 'en'    # Target language (default: English)

# Translation engine
translator:
  provider: 'google-free'  # Options: google-free, deepl, mymemory, libretranslate
  mode: 'ai'              # Options: rule_based, ai, hybrid
  quality_threshold: 0.75 # Minimum Ω score to accept translation

  # Provider-specific settings
  providers:
    deepl:
      api_key: null      # Use FDS_DEEPL_API_KEY env var
      free_api: true     # false for paid tier

    mymemory:
      email: null        # Optional, for higher limits

    libretranslate:
      url: 'http://localhost:5000/translate'

    google-free:
      service_urls: null # Optional custom service URLs

# File processing
files:
  recursive: true        # Process subdirectories
  patterns:
    - '*.py'
    - '*.md'
    - '*.markdown'
  exclude:
    - '**/__pycache__/**'
    - '**/.git/**'
    - '**/node_modules/**'
```

### Environment Variables

```bash
# DeepL API key
export FDS_DEEPL_API_KEY="your-deepl-api-key"

# OpenAI API key (for future AI mode)
export OPENAI_API_KEY="sk-..."

# Anthropic API key (for future AI mode)
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## CLI Usage Examples

### Basic Translation

```bash
# Translate single file
fds translate README.ko.md --output README.md

# Translate in-place
fds translate src/main.py --in-place

# Translate directory recursively
fds translate src/ --recursive --in-place
```

### Advanced Options

```bash
# Specify source language
fds translate README.md --source-lang ko --target-lang en

# Set translation mode
fds translate README.md --mode ai

# Set quality threshold
fds translate README.md --quality-threshold 0.85

# Preview without saving
fds translate src/ --recursive
# (Without --in-place, shows preview only)
```

### Integration with CI/CD

```yaml
# .github/workflows/translate.yml
name: Auto-translate Documentation

on:
  push:
    paths:
      - '**.ko.md'
      - '**.ja.md'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install FDS-Dev
        run: pip install fds-dev

      - name: Translate Korean docs
        env:
          FDS_DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
        run: |
          fds translate docs/*.ko.md --mode ai --in-place

      - name: Commit translations
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/*.md
          git commit -m "docs: Auto-translate Korean documentation"
          git push
```

---

## Best Practices

### 1. Choose the Right Translation Mode

**Rule-Based** (`--mode rule_based`):
- ✓ Fast, free, offline-capable
- ✓ Good for simple technical comments
- ✗ Limited vocabulary coverage
- ✗ Lower quality for complex sentences

**AI-Powered** (`--mode ai`):
- ✓ Highest quality translations
- ✓ Handles complex sentences
- ✓ Context-aware
- ✗ Requires API key & internet
- ✗ Costs money (after free tier)

**Hybrid** (`--mode hybrid`):
- ✓ Best of both worlds
- ✓ Fallback on API failure
- ✗ Slightly more complex setup

**Recommendation**: Use `hybrid` mode for production

### 2. Set Appropriate Quality Thresholds

```bash
# For technical documentation (strict)
fds translate docs/ --quality-threshold 0.85

# For informal comments (lenient)
fds translate scripts/ --quality-threshold 0.65

# For production code (balanced)
fds translate src/ --quality-threshold 0.75  # Default
```

### 3. Use Caching for Large Projects

FDS-Dev automatically caches translations in `.fds_cache.json`:

```json
{
  "ko:en:함수를 호출합니다": {
    "translated": "call the function.",
    "confidence": 0.95,
    "timestamp": "2025-11-19T10:30:00Z"
  }
}
```

**Benefits**:
- Avoids redundant API calls
- Maintains consistency
- Speeds up re-runs

**Note**: Cache is invalidated when source text changes

### 4. Review Low-Quality Translations

```bash
# Preview mode to review before applying
fds translate src/ --recursive

# Look for warnings:
# [✗] [Ω=0.62] (L42): 복잡한 문장 구조...
#   - Issue: Semantic meaning may be lost in translation
#   - Recommendation: Consider rephrasing or adding clarification
```

Then manually fix or adjust threshold.

---

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed error solutions.

Quick fixes:

1. **Import Error**: Ensure FDS-Dev is installed: `pip install -e .`
2. **API Error**: Check API key in environment variables
3. **Low Quality**: Try `--mode ai` or adjust `--quality-threshold`
4. **Timeout**: Check network connection, API may be slow

---

**Last Updated**: 2025-11-19
**Version**: 1.0
**Related Docs**: TROUBLESHOOTING.md, QUALITY_SCORING.md
