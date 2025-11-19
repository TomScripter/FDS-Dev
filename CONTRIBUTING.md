# Contributing to FDS-Dev

Thanks for helping improve Flamehaven Doc Sanity! This guide explains how to set up
your environment, propose changes, and ship releases while keeping the project ASCII-safe
and production-ready.

## Getting Started
1. Fork the repository and `git clone https://github.com/<you>/FDS-Dev.git`.
2. Create a virtualenv (Python 3.9–3.12 are supported):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   pip install --upgrade pip
   pip install -e .
   pip install pytest pytest-cov flake8 build twine
   ```
3. Copy `.fdsrc.yaml` if you need custom linting rules for local experiments.

## Development Workflow
- Create feature branches off `main` using `feature/<short-description>` or `fix/<issue-id>`.
- Follow the existing commit style (`Add …`, `Fix …`, `Update …`) and keep commits focused.
- Keep all code, comments, and docs ASCII-only to avoid cp949 decoding issues on Windows systems.

## Quality Gates
- Lint: `flake8 fds_dev/ --count --select=E9,F63,F7,F82` and `flake8 fds_dev/ --count --exit-zero --max-complexity=10`.
- Tests: `pytest tests/ -v --cov=fds_dev --cov-report=term`.
- For focused debugging, run individual suites such as `pytest tests/test_i18n_translator.py -k cached`.

## Documentation Expectations
- Update `README.md` and `README_KR.md` when user-facing behavior changes.
- Add or extend files under `docs/` for architecture or troubleshooting topics.
- Capture large examples in `tests/data` instead of embedding multi-line blobs in code.
- Reference new environment variables in `.fdsrc.yaml` or `PYPI_SETUP.md` as needed.

## Pull Request Checklist
- [ ] Tests and flake8 pass locally.
- [ ] `CHANGELOG.md` contains an entry under the correct version heading.
- [ ] New or modified public APIs include type hints and docstrings.
- [ ] Screenshots or terminal transcripts attached for CLI/prompt changes.
- [ ] Linked issues and described behavioral impact in the PR template.

## Release Contributions
- Bump `project.version` in `pyproject.toml` and update the matching tag (`vX.Y.Z`).
- Ensure the latest entry in `CHANGELOG.md` summarizes the release.
- Run `python -m build` and `twine check dist/*` locally before tagging.
- Tag with `git tag vX.Y.Z && git push origin vX.Y.Z` to trigger the release workflow.

## Reporting Issues
Use GitHub Issues for bugs, Discussions for idea pitches, and info@flamehaven.space for private contact.
Include logs, OS details, sample documents, and the command you ran.

## Code of Conduct
Be respectful, assume positive intent, and collaborate transparently. Harassment or discrimination will not be tolerated.
