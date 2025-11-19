# Changelog
All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [0.0.1] - 2025-11-19
### Added
- Initial `fds` CLI with the `lint` and `translate` commands, parallel lint execution, and persistent cache management via `.fds_cache.json`.
- Translation pipeline that detects the source language, enforces `.fdsrc.yaml` rules, and fans out to DeepL, LibreTranslate, MyMemory, or the google-free backend with consistent result objects.
- Language-aware Markdown parser, comment-preserving code parser, and translation quality tensor exported from `fds_dev.i18n`.
- Configuration bootstrap (`.fdsrc.yaml`) plus opinionated rule presets for structure-aware linting.
- Documentation set: `docs/ARCHITECTURE.md`, `docs/TRANSLATION_ALGORITHM.md`, `docs/TROUBLESHOOTING.md`, and the bilingual README pair.

### Fixed
- Corrected the `TranslationResult` import path and provided a guarded `GoogleTranslator` placeholder so unknown providers raise friendly errors instead of crashing.
- Added exponential backoff retries to all HTTP translators to smooth over transient API failures.
- Hardened output formatting and cache serialization so linting large documentation trees is deterministic.

### Testing
- Added 92 dedicated tests across `tests/test_i18n_language_detector.py`, `tests/test_i18n_translator.py`, `tests/test_i18n_metacognition.py`, and `tests/test_i18n_code_parser.py`, yielding 95% coverage with 100/105 tests green.
- Captured regression data and fixtures for language detection, translation quality scoring, and lint runner behaviors.

### Documentation
- Rebuilt `README.md` with deployment badges, a feature tour, translation provider matrix, and support channels.
- Authored Korean documentation (`README_KR.md`) to demonstrate the translation workflow.

### Infrastructure
- Set up `.github/workflows/ci.yml` for multi-version lint + pytest runs and `.github/workflows/release.yml` for trusted-publisher PyPI deployments and GitHub Releases.
- Added `PYPI_SETUP.md` to document how to provision tokens, environments, and release tags.
