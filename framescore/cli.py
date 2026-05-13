"""CLI entry point with argparse for FrameScore."""

import argparse
import os
import sys

from . import __version__
from .analyzer import Analyzer
from .dep_analyzer import DependencyAnalyzer
from .git_integration import GitIntegration
from .reporter import Reporter
from .rules import create_default_registry
from .scanner import ProjectScanner
from .scorer import Scorer
from .utils import Colors, format_duration


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="framescore",
        description="FrameScore - Lightweight frontend framework code health intelligent scoring engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  framescore scan ./my-project\n"
            "  framescore scan ./my-project --format json\n"
            "  framescore scan ./my-project --framework react --severity error\n"
            "  framescore scan ./my-project --output report.md\n"
            "  framescore history ./my-project\n"
            "  framescore rules\n"
        ),
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"FrameScore v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a project and output health score",
    )
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory)",
    )
    scan_parser.add_argument(
        "--format", "-f",
        choices=["table", "json", "markdown"],
        default="table",
        help="Output format (default: table)",
    )
    scan_parser.add_argument(
        "--framework",
        choices=["react", "vue", "svelte", "angular", "auto"],
        default="auto",
        help="Framework selection (default: auto-detect)",
    )
    scan_parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip dependency analysis",
    )
    scan_parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git integration",
    )
    scan_parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        default="info",
        help="Minimum severity level (default: info)",
    )
    scan_parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save report to file",
    )
    scan_parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )
    scan_parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar",
    )

    # history command
    history_parser = subparsers.add_parser(
        "history",
        help="Show score history from git",
    )
    history_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory",
    )

    # rules command
    rules_parser = subparsers.add_parser(
        "rules",
        help="List all available rules",
    )
    rules_parser.add_argument(
        "--framework",
        choices=["react", "vue", "svelte", "angular", "general", "all"],
        default="all",
        help="Filter rules by framework (default: all)",
    )
    rules_parser.add_argument(
        "--category",
        choices=["security", "performance", "correctness", "best-practice", "accessibility"],
        help="Filter rules by category",
    )

    return parser


def cmd_scan(args: argparse.Namespace) -> int:
    """Execute the scan command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    import time

    start_time = time.time()
    project_path = os.path.abspath(args.path)

    # Validate path
    if not os.path.isdir(project_path):
        print(Colors.red(f"Error: '{args.path}' is not a valid directory."))
        return 1

    # Print banner (skip for JSON format to keep output clean)
    if args.format != "json":
        print()
        print(Colors.cyan(Colors.bold("  ╔══════════════════════════════════════╗")))
        print(Colors.cyan(Colors.bold("  ║         FrameScore v1.0.0           ║")))
        print(Colors.cyan(Colors.bold("  ║   Code Health Scoring Engine        ║")))
        print(Colors.cyan(Colors.bold("  ╚══════════════════════════════════════╝")))
        print()

    # Initialize scanner
    framework_override = args.framework if args.framework != "auto" else None
    scanner = ProjectScanner(project_path, framework_override=framework_override)

    # Scan project
    if args.format != "json":
        print(Colors.bold("  Scanning project..."))
    project_info = scanner.scan()

    if project_info.total_files == 0:
        if args.format != "json":
            print(Colors.yellow("  Warning: No source files found in the project."))
            print(Colors.dim("  Supported extensions: .js, .jsx, .ts, .tsx, .vue, .svelte"))
        return 1

    if args.format != "json":
        print(f"  Framework:  {Colors.green(project_info.framework.value)}")
        print(f"  Files:      {project_info.total_files} ({project_info.total_lines} lines)")

    # Dependency analysis
    dep_result = None
    if not args.no_deps:
        dep_analyzer = DependencyAnalyzer(project_path)
        dep_result = dep_analyzer.analyze()
        if args.format != "json":
            if dep_result.total_deps > 0:
                print(f"  Deps:       {dep_result.total_deps} ({dep_result.prod_deps} prod, {dep_result.dev_deps} dev)")
                if dep_result.missing_lock:
                    print(Colors.yellow("  Warning:    No lock file found"))
                if dep_result.has_non_semver:
                    print(Colors.yellow("  Warning:    Non-semver versions detected"))

    # Git integration
    git_info = None
    if not args.no_git:
        git = GitIntegration(project_path)
        if git.is_git_repo():
            git_info = git.get_git_info()
            if args.format != "json":
                print(f"  Branch:     {git_info.current_branch}")
                print(f"  Commits:    {git_info.total_commits}")

    if args.format != "json":
        print()

    # Initialize analyzer
    registry = create_default_registry()
    analyzer = Analyzer(
        registry=registry,
        project_info=project_info,
        max_workers=args.workers,
        show_progress=not args.no_progress and args.format != "json",
    )

    # Run analysis
    result = analyzer.analyze(min_severity=args.severity)

    # Calculate score
    scorer = Scorer()
    health = scorer.calculate(result)

    # Generate report
    reporter = Reporter(result, health)
    reporter.output(format_type=args.format, output_file=args.output)

    # Save to git history
    if not args.no_git and git_info and git_info.is_git_repo:
        try:
            git.save_score_to_history(
                score=health.overall_score,
                grade=health.grade,
                issues_count=health.total_issues,
            )
        except Exception:
            pass  # Silently fail if history save fails

    # Print summary line (skip for JSON format)
    elapsed = time.time() - start_time
    if args.format != "json":
        print(
            f"  Completed in {format_duration(elapsed)} | "
            f"{health.total_issues} issues found | "
            f"Score: {health.overall_score:.1f}/100 ({health.grade})"
        )
        print()

    # Exit with error code if there are errors
    return 1 if health.error_count > 0 else 0


def cmd_history(args: argparse.Namespace) -> int:
    """Execute the history command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    project_path = os.path.abspath(args.path)

    if not os.path.isdir(project_path):
        print(Colors.red(f"Error: '{args.path}' is not a valid directory."))
        return 1

    git = GitIntegration(project_path)
    if not git.is_git_repo():
        print(Colors.red("Error: Not a git repository."))
        return 1

    # Get git info
    git_info = git.get_git_info()
    print()
    print(Colors.bold(Colors.cyan("  FrameScore - Score History")))
    print()
    print(f"  Branch: {git_info.current_branch}")
    print(f"  Total commits: {git_info.total_commits}")
    print()

    # Get score history
    history = git.get_score_history()

    if not history:
        print(Colors.yellow("  No score history found."))
        print(Colors.dim("  Run 'framescore scan' to start tracking scores."))
        print()
        return 0

    # Display history
    print(f"  {'Date':<22} {'Commit':<10} {'Score':>8} {'Grade':>6} {'Issues':>8}")
    print(f"  {'-' * 58}")

    for entry in history:
        score_color = _score_color(entry.score)
        grade_color = _grade_color(entry.grade)
        print(
            f"  {entry.date:<22} "
            f"{entry.commit_hash:<10} "
            f"{score_color(f'{entry.score:>7.1f}')} "
            f"{grade_color(f'{entry.grade:>6}')} "
            f"{entry.issues_count:>8}"
        )

    # Show trend
    if len(history) >= 2:
        latest = history[-1].score
        previous = history[-2].score
        change = latest - previous
        if change > 0:
            trend = Colors.green(f"+{change:.1f}")
        elif change < 0:
            trend = Colors.red(f"{change:.1f}")
        else:
            trend = Colors.dim("0.0")
        print()
        print(f"  Trend: {trend} (vs previous scan)")

    print()
    return 0


def cmd_rules(args: argparse.Namespace) -> int:
    """Execute the rules command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    registry = create_default_registry()
    all_rules = registry.get_all()

    # Filter by framework
    if args.framework != "all":
        from .rules.base import Framework
        fw_map = {
            "react": Framework.REACT,
            "vue": Framework.VUE,
            "svelte": Framework.SVELTE,
            "angular": Framework.ANGULAR,
            "general": Framework.GENERAL,
        }
        target_fw = fw_map.get(args.framework)
        if target_fw:
            all_rules = [r for r in all_rules if r.framework == target_fw]

    # Filter by category
    if args.category:
        from .rules.base import Category
        cat_map = {
            "security": Category.SECURITY,
            "performance": Category.PERFORMANCE,
            "correctness": Category.CORRECTNESS,
            "best-practice": Category.BEST_PRACTICE,
            "accessibility": Category.ACCESSIBILITY,
        }
        target_cat = cat_map.get(args.category)
        if target_cat:
            all_rules = [r for r in all_rules if r.category == target_cat]

    # Display rules
    print()
    print(Colors.bold(Colors.cyan("  FrameScore - Available Rules")))
    print()
    print(f"  Total: {len(all_rules)} rules")
    print()

    # Group by framework
    from .rules.base import Framework
    frameworks = [Framework.REACT, Framework.VUE, Framework.SVELTE, Framework.ANGULAR, Framework.GENERAL]
    fw_labels = {
        Framework.REACT: "React",
        Framework.VUE: "Vue",
        Framework.SVELTE: "Svelte",
        Framework.ANGULAR: "Angular",
        Framework.GENERAL: "General",
    }

    for fw in frameworks:
        fw_rules = [r for r in all_rules if r.framework == fw]
        if not fw_rules:
            continue

        print(Colors.bold(f"  [{fw_labels[fw]}] ({len(fw_rules)} rules)"))
        print()

        for rule in fw_rules:
            sev_color = _severity_color(rule.severity.value)
            cat_display = Colors.dim(f"[{rule.category.value}]")
            print(
                f"    {rule.rule_id}  "
                f"{sev_color(rule.severity.value.upper()):<8} "
                f"{cat_display}  "
                f"{rule.name}"
            )
        print()

    # Summary
    summary = registry.summary()
    print(Colors.dim(f"  Total rules: {summary['total']}"))
    print()

    return 0


def _score_color(score: float) -> str:
    """Get color function for a score value.

    Args:
        score: Numeric score.

    Returns:
        Color function.
    """
    if score >= 90:
        return Colors.green
    if score >= 75:
        return Colors.yellow
    return Colors.red


def _grade_color(grade: str) -> str:
    """Get color function for a grade.

    Args:
        grade: Grade string.

    Returns:
        Color function.
    """
    if grade in ("A+", "A"):
        return Colors.green
    if grade in ("B+", "B"):
        return Colors.cyan
    if grade in ("C+", "C"):
        return Colors.yellow
    return Colors.red


def _severity_color(severity: str) -> str:
    """Get color function for a severity level.

    Args:
        severity: Severity string.

    Returns:
        Color function.
    """
    colors = {
        "error": Colors.red,
        "warning": Colors.yellow,
        "info": Colors.cyan,
    }
    return colors.get(severity, Colors.WHITE)


def main(argv: list = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "history":
        return cmd_history(args)
    elif args.command == "rules":
        return cmd_rules(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
