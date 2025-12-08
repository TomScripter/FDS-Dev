"""FDS-Dev module."""

import click
import os
import glob
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from pathlib import Path

from fds_dev.config import load_config
from fds_dev.runner import LintRunner
from fds_dev.parser import MarkdownParser
from fds_dev.language import LanguageDetector
from fds_dev.translator import TranslationEngine
from fds_dev.output import OutputFormatter


def resolve_cache_path(target_path: str) -> Path:
    path_obj = Path(target_path)
    if path_obj.is_dir():
        return path_obj / '.fds_cache.json'
    parent = path_obj.parent if path_obj.parent.as_posix() else Path('.')
    return parent / '.fds_cache.json'


def load_cache(cache_path: Path):
    if cache_path.exists():
        with cache_path.open('r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_cache(cache, cache_path: Path):
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('w') as f:
        json.dump(cache, f, indent=2)

@click.group()
def cli():
    """
    FDS-Dev: A blazingly fast, structure-aware linter for your documentation,
    supercharged with AI-powered translation.
    """
    pass

def run_lint_on_file(runner, cache, file_path):
    """Helper function to be called by the process pool."""
    return runner.run(file_path, cache)

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def lint(path):
    """Checks documentation for structural issues."""

    # 1. Load cache and initialize components
    config = load_config(path)
    cache_path = resolve_cache_path(path)
    cache = load_cache(cache_path)
    runner = LintRunner(config)
    formatter = OutputFormatter()

    files_to_lint = []
    if os.path.isdir(path):
        # Find all markdown files recursively
        files_to_lint.extend(glob.glob(os.path.join(path, '**', '*.md'), recursive=True))
        files_to_lint.extend(glob.glob(os.path.join(path, '**', '*.markdown'), recursive=True))
    else:
        files_to_lint.append(path)

    click.echo(f"Found {len(files_to_lint)} file(s) to lint...")

    # 2. Run linting in parallel
    results = []
    with ProcessPoolExecutor() as executor:
        # Use functools.partial to create a function with runner and cache arguments pre-filled
        lint_func = partial(run_lint_on_file, runner, cache)

        future_to_file = {executor.submit(lint_func, file): file for file in files_to_lint}

        with click.progressbar(as_completed(future_to_file), length=len(files_to_lint), label="Linting files") as bar:
            for future in bar:
                file_path, file_hash, errors = future.result()
                results.append((file_path, errors))

                # 3. Update cache with new results
                if file_hash:
                    cache[file_path] = {
                        'hash': file_hash,
                        'errors': [e.__dict__ for e in errors]
                    }

    # 4. Save the updated cache
    save_cache(cache, cache_path)

    # 5. Display results
    formatter.display_lint_results(results)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', help="Output file path for the translated document.")
@click.option('--in-place', is_flag=True, help="Translate the file in-place (overwrites the original).")
def translate(path, output, in_place):
    """Translates docs and code comments to English."""
    click.echo(f"Translating {path}...")

    parser = MarkdownParser()
    detector = LanguageDetector()
    config = load_config(path)
    engine = TranslationEngine(config)
    formatter = OutputFormatter()

    try:
        doc = parser.parse(path)
        source_lang_config = config.get('language', {}).get('source', 'auto')
        target_lang_config = config.get('language', {}).get('target', 'en')

        source_lang = source_lang_config
        if source_lang == 'auto':
            detection = detector.detect(doc.content)
            source_lang = detection.language
            click.echo(f"Detected language: {source_lang.upper()} (confidence {detection.confidence:.2f})")

        if source_lang == target_lang_config:
            click.secho("Source and target languages are the same. Nothing to translate.", fg="yellow")
            return

        translated_content = engine.translate(doc.content, source_lang, target_lang_config)

        if in_place:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            formatter.display_save_message(path, in_place=True)
        elif output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            formatter.display_save_message(output, in_place=False)
        else:
            formatter.display_translation_preview(path, translated_content)

    except FileNotFoundError:
        click.secho(f"Error: File not found at {path}", fg="red")
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")


if __name__ == '__main__':
    cli()
