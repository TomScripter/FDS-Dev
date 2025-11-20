# FDS-Dev Examples

Quick examples demonstrating FDS-Dev capabilities.

## Files

- **`basic_usage.py`**: Essential patterns for getting started
  - Linting Markdown files
  - Rule-based translation
  - Code comment parsing
  - Configuration loading
  - CLI command reference

- **`advanced_usage.py`**: Production-ready patterns
  - Parallel batch processing
  - Custom severity filtering
  - Report generation
  - Multi-file workflows

## Running Examples

### Basic Usage
```bash
# From repository root
python examples/basic_usage.py
```

### Advanced Usage
```bash
python examples/advanced_usage.py
```

## Prerequisites

Install FDS-Dev in development mode:
```bash
pip install -e .
```

## Quick CLI Test

```bash
# Initialize configuration
fds init

# Lint README
fds lint README.md

# Check i18n issues
fds i18n-check fds_dev/
```

---

[>] For comprehensive documentation, see [`docs/`](../docs/)
