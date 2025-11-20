"""
Advanced example: Custom linting rules and batch processing
"""

from pathlib import Path
from fds_dev.main import lint_file
from fds_dev.rules import RuleRegistry
from concurrent.futures import ThreadPoolExecutor, as_completed


# [!] Example 1: Batch Linting with Parallel Processing

def lint_directory_parallel(dir_path: Path, max_workers: int = 4):
    """Lint all Markdown files in a directory using parallel processing"""
    md_files = list(dir_path.rglob("*.md"))
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(lint_file, file): file 
            for file in md_files
        }
        
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results[file] = result
                print(f"[+] Linted {file.name}: {len(result.issues)} issues")
            except Exception as e:
                print(f"[-] Error linting {file.name}: {e}")
    
    return results


# [!] Example 2: Filter Issues by Severity

def get_critical_issues(lint_result):
    """Extract only critical and high-severity issues"""
    critical = [
        issue for issue in lint_result.issues 
        if issue.severity in ['critical', 'error']
    ]
    return critical


# [!] Example 3: Generate Markdown Report

def generate_report(results: dict, output_path: Path):
    """Generate a Markdown report of linting results"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# FDS-Dev Linting Report\n\n")
        
        total_issues = sum(len(r.issues) for r in results.values())
        f.write(f"[=] Total files: {len(results)}\n")
        f.write(f"[!] Total issues: {total_issues}\n\n")
        
        for file, result in results.items():
            if result.issues:
                f.write(f"## {file.name}\n\n")
                for issue in result.issues:
                    f.write(f"- **{issue.severity.upper()}** (line {issue.line}): {issue.message}\n")
                f.write("\n")
    
    print(f"[+] Report saved to {output_path}")


# [!] Example Usage

if __name__ == "__main__":
    # Lint documentation directory
    docs_dir = Path("docs")
    
    if docs_dir.exists():
        print("[>] Starting parallel linting...\n")
        results = lint_directory_parallel(docs_dir)
        
        # Generate report
        report_path = Path("lint_report.md")
        generate_report(results, report_path)
        
        # Show critical issues
        print("\n[!] Critical Issues:\n")
        for file, result in results.items():
            critical = get_critical_issues(result)
            if critical:
                print(f"{file.name}:")
                for issue in critical:
                    print(f"  [-] Line {issue.line}: {issue.message}")
    else:
        print("[-] docs/ directory not found")
