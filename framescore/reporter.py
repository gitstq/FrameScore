"""Output formatting - table, JSON, and markdown report generation."""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

from .analyzer import AnalysisResult
from .rules.base import Category, Issue, Severity
from .scorer import HealthScore
from .utils import (
    Colors,
    format_duration,
    grade_to_color,
    severity_to_color,
)


class Reporter:
    """Formats and outputs analysis results in various formats.

    Supports table (terminal), JSON, and Markdown output formats.
    """

    def __init__(self, result: AnalysisResult, score: HealthScore):
        """Initialize the reporter.

        Args:
            result: Analysis result with issues.
            score: Calculated health score.
        """
        self.result = result
        self.score = score

    def format_table(self) -> str:
        """Format the report as a rich ASCII table for terminal output.

        Returns:
            Formatted string with ANSI color codes.
        """
        lines = []
        lines.append("")
        lines.append(self._separator("=", 70))
        lines.append(Colors.bold(Colors.cyan("  FrameScore - Code Health Report")))
        lines.append(self._separator("=", 70))
        lines.append("")

        # Project info
        if self.result.project_info:
            pi = self.result.project_info
            lines.append(f"  {Colors.bold('Project:')}     {pi.root_path}")
            lines.append(f"  {Colors.bold('Framework:')}   {pi.framework.value}")
            lines.append(f"  {Colors.bold('Files:')}       {pi.total_files} files, {pi.total_lines} lines")
            lines.append(f"  {Colors.bold('Analyzed:')}    {self.result.files_analyzed} files")
            lines.append(f"  {Colors.bold('Rules:')}       {self.result.rules_run} rules applied")
            lines.append(f"  {Colors.bold('Time:')}        {format_duration(self.result.analysis_time)}")
        lines.append("")

        # Score display
        lines.append(self._separator("-", 70))
        score_color = grade_to_color(self.score.grade)
        lines.append(
            f"  {Colors.bold('Health Score:')} "
            f"{Colors.wrap(Colors.bold(f'{self.score.overall_score:.1f}/100'), score_color)} "
            f"  Grade: {Colors.wrap(Colors.bold(f'  {self.score.grade}  '), score_color)}"
        )
        lines.append(self._separator("-", 70))
        lines.append("")

        # Issue summary
        error_color = severity_to_color("error")
        warning_color = severity_to_color("warning")
        info_color = severity_to_color("info")

        lines.append(
            f"  {Colors.bold('Issues:')}       "
            f"{Colors.wrap(f'{self.score.error_count} errors', error_color)}  "
            f"{Colors.wrap(f'{self.score.warning_count} warnings', warning_color)}  "
            f"{Colors.wrap(f'{self.score.info_count} info', info_color)}"
        )
        lines.append(
            f"  {Colors.bold('Deductions:')}   {self.score.deductions:.1f} points"
        )
        lines.append("")

        # Category breakdown
        lines.append(self._separator("-", 70))
        lines.append(Colors.bold("  Category Breakdown"))
        lines.append(self._separator("-", 70))

        cat_header = f"  {'Category':<20} {'Score':>8} {'Issues':>8} {'Deduct':>8}"
        lines.append(f"  {Colors.dim(cat_header)}")
        lines.append(f"  {'-' * 46}")

        for cat_name, cat_score in self.score.category_scores.items():
            cat_color = self._category_color(cat_name, cat_score.score)
            cat_display = cat_color(f"{cat_name:<20}")
            score_display = cat_color(f"{cat_score.score:>7.1f}")
            issues_display = str(cat_score.issues_count)
            deduct_display = f"-{cat_score.deductions:.1f}"
            lines.append(
                f"  {cat_display} {score_display} {issues_display:>8} {deduct_display:>8}"
            )

        lines.append("")

        # Module breakdown (if available)
        if self.score.module_scores:
            lines.append(self._separator("-", 70))
            lines.append(Colors.bold("  Module Breakdown"))
            lines.append(self._separator("-", 70))

            mod_header = f"  {'Module':<30} {'Score':>8} {'Issues':>8}"
            lines.append(f"  {Colors.dim(mod_header)}")
            lines.append(f"  {'-' * 48}")

            for mod_name, mod_score in sorted(
                self.score.module_scores.items(), key=lambda x: x[1].score
            ):
                mod_color = grade_to_color(
                    self._score_to_grade(mod_score.score)
                )
                mod_display = Colors.wrap(f"{mod_name:<30}", mod_color)
                score_display = Colors.wrap(f"{mod_score.score:>7.1f}", mod_color)
                lines.append(
                    f"  {mod_display} {score_display} {mod_score.issues_count:>8}"
                )

            lines.append("")

        # Top issues
        top_issues = self.result.get_top_issues(10)
        if top_issues:
            lines.append(self._separator("-", 70))
            lines.append(Colors.bold("  Top Issues"))
            lines.append(self._separator("-", 70))

            for i, issue in enumerate(top_issues, 1):
                sev_color = severity_to_color(issue.severity.value)
                sev_display = Colors.wrap(f"[{issue.severity.value.upper()}]", sev_color)
                rule_display = Colors.dim(f"{issue.rule_id}")
                file_display = Colors.dim(issue.file_path)
                line_display = Colors.dim(f":{issue.line}")

                lines.append(
                    f"  {i:>2}. {sev_display} {rule_display} "
                    f"{file_display}{line_display}"
                )
                lines.append(f"      {issue.message}")
                if issue.suggestion:
                    lines.append(
                        f"      {Colors.green('Fix:')} {issue.suggestion}"
                    )
                lines.append("")

        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            lines.append(self._separator("-", 70))
            lines.append(Colors.bold("  Recommendations"))
            lines.append(self._separator("-", 70))
            for rec in recommendations:
                lines.append(f"  {Colors.cyan('*')} {rec}")
            lines.append("")

        lines.append(self._separator("=", 70))
        lines.append(
            f"  Generated by FrameScore v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append(self._separator("=", 70))
        lines.append("")

        return "\n".join(lines)

    def format_json(self) -> str:
        """Format the report as structured JSON.

        Returns:
            JSON string with all analysis details.
        """
        report = {
            "framescore_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "project": {
                "path": self.result.project_info.root_path if self.result.project_info else "",
                "framework": self.result.project_info.framework.value if self.result.project_info else "unknown",
                "total_files": self.result.project_info.total_files if self.result.project_info else 0,
                "total_lines": self.result.project_info.total_lines if self.result.project_info else 0,
                "files_analyzed": self.result.files_analyzed,
                "rules_run": self.result.rules_run,
                "analysis_time": round(self.result.analysis_time, 3),
            },
            "score": self.score.to_dict(),
            "issues": [issue.to_dict() for issue in self.result.issues],
            "recommendations": self._generate_recommendations(),
        }
        return json.dumps(report, indent=2, ensure_ascii=False)

    def format_markdown(self) -> str:
        """Format the report as GitHub-flavored Markdown.

        Returns:
            Markdown string.
        """
        lines = []
        lines.append("# FrameScore - Code Health Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Project info
        if self.result.project_info:
            pi = self.result.project_info
            lines.append("## Project Info")
            lines.append("")
            lines.append(f"| Property | Value |")
            lines.append(f"|----------|-------|")
            lines.append(f"| **Path** | `{pi.root_path}` |")
            lines.append(f"| **Framework** | {pi.framework.value} |")
            lines.append(f"| **Files** | {pi.total_files} ({pi.total_lines} lines) |")
            lines.append(f"| **Analyzed** | {self.result.files_analyzed} files |")
            lines.append(f"| **Rules** | {self.result.rules_run} applied |")
            lines.append(f"| **Time** | {format_duration(self.result.analysis_time)} |")
            lines.append("")

        # Score
        lines.append("## Health Score")
        lines.append("")
        grade_emoji = self._grade_emoji(self.score.grade)
        lines.append(
            f"### {grade_emoji} **{self.score.overall_score:.1f}/100** - Grade: **{self.score.grade}**"
        )
        lines.append("")

        # Issue summary
        lines.append("### Issue Summary")
        lines.append("")
        lines.append(f"| Severity | Count |")
        lines.append(f"|----------|-------|")
        lines.append(f"| :red_circle: Errors | {self.score.error_count} |")
        lines.append(f"| :yellow_circle: Warnings | {self.score.warning_count} |")
        lines.append(f"| :white_circle: Info | {self.score.info_count} |")
        lines.append(f"| **Total** | **{self.score.total_issues}** |")
        lines.append(f"| **Deductions** | **-{self.score.deductions:.1f} pts** |")
        lines.append("")

        # Category breakdown
        lines.append("## Category Breakdown")
        lines.append("")
        lines.append(f"| Category | Score | Issues | Deductions |")
        lines.append(f"|----------|-------|--------|------------|")
        for cat_name, cat_score in self.score.category_scores.items():
            score_bar = self._markdown_score_bar(cat_score.score)
            lines.append(
                f"| {cat_name} | {cat_score.score:.1f}/100 {score_bar} | {cat_score.issues_count} | -{cat_score.deductions:.1f} |"
            )
        lines.append("")

        # Module breakdown
        if self.score.module_scores:
            lines.append("## Module Breakdown")
            lines.append("")
            lines.append(f"| Module | Score | Issues |")
            lines.append(f"|--------|-------|--------|")
            for mod_name, mod_score in sorted(
                self.score.module_scores.items(), key=lambda x: x[1].score
            ):
                lines.append(
                    f"| `{mod_name}` | {mod_score.score:.1f}/100 | {mod_score.issues_count} |"
                )
            lines.append("")

        # Top issues
        top_issues = self.result.get_top_issues(20)
        if top_issues:
            lines.append("## Top Issues")
            lines.append("")
            lines.append(f"| # | Severity | Rule | File | Line | Message |")
            lines.append(f"|---|----------|------|------|------|---------|")
            for i, issue in enumerate(top_issues, 1):
                sev_badge = self._severity_badge(issue.severity.value)
                lines.append(
                    f"| {i} | {sev_badge} | `{issue.rule_id}` | `{issue.file_path}` | {issue.line} | {issue.message} |"
                )
            lines.append("")

        # All issues (grouped by file)
        issues_by_file = self.result.get_issues_by_file()
        if issues_by_file:
            lines.append("## Issues by File")
            lines.append("")
            for file_path, file_issues in sorted(issues_by_file.items()):
                lines.append(f"### `{file_path}` ({len(file_issues)} issues)")
                lines.append("")
                for issue in file_issues:
                    sev_badge = self._severity_badge(issue.severity.value)
                    lines.append(
                        f"- {sev_badge} **{issue.rule_id}** (line {issue.line}): {issue.message}"
                    )
                    if issue.suggestion:
                        lines.append(f"  - *Fix: {issue.suggestion}*")
                lines.append("")

        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        lines.append("---")
        lines.append("*Generated by [FrameScore](https://github.com/framescore) v1.0.0*")

        return "\n".join(lines)

    def output(self, format_type: str = "table", output_file: Optional[str] = None) -> None:
        """Output the report in the specified format.

        Args:
            format_type: Output format ('table', 'json', 'markdown').
            output_file: Optional file path to save the report.
        """
        if format_type == "json":
            content = self.format_json()
        elif format_type == "markdown":
            content = self.format_markdown()
        else:
            content = self.format_table()

        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\n  Report saved to: {output_file}\n")
        else:
            print(content)

    def _separator(self, char: str, width: int) -> str:
        """Create a separator line.

        Args:
            char: Character to use for the separator.
            width: Width of the separator.

        Returns:
            Separator string.
        """
        return Colors.dim(char * width)

    def _category_color(self, category: str, score: float) -> str:
        """Get color function for a category based on its score.

        Args:
            category: Category name.
            score: Category score.

        Returns:
            Color function from Colors class.
        """
        if category == Category.SECURITY.value:
            if score < 80:
                return Colors.red
            elif score < 95:
                return Colors.yellow
            return Colors.green
        if score < 70:
            return Colors.red
        elif score < 85:
            return Colors.yellow
        return Colors.green

    def _score_to_grade(self, score: float) -> str:
        """Convert a numeric score to a grade.

        Args:
            score: Numeric score.

        Returns:
            Grade string.
        """
        if score >= 95:
            return "A+"
        if score >= 90:
            return "A"
        if score >= 85:
            return "B+"
        if score >= 80:
            return "B"
        if score >= 75:
            return "C+"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def _grade_emoji(self, grade: str) -> str:
        """Get emoji for a grade.

        Args:
            grade: Grade string.

        Returns:
            Emoji string.
        """
        emojis = {
            "A+": ":trophy:",
            "A": ":star:",
            "B+": ":thumbsup:",
            "B": ":neutral_face:",
            "C+": ":thinking:",
            "C": ":worried:",
            "D": ":warning:",
            "F": ":rotating_light:",
        }
        return emojis.get(grade, ":question:")

    def _severity_badge(self, severity: str) -> str:
        """Get markdown badge for severity.

        Args:
            severity: Severity string.

        Returns:
            Markdown badge string.
        """
        badges = {
            "error": ":red_circle: `ERROR`",
            "warning": ":yellow_circle: `WARN`",
            "info": ":white_circle: `INFO`",
        }
        return badges.get(severity, "`UNKNOWN`")

    def _markdown_score_bar(self, score: float) -> str:
        """Create a visual score bar for markdown.

        Args:
            score: Score value.

        Returns:
            Markdown score bar string.
        """
        filled = int(score / 10)
        empty = 10 - filled
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "yellow"
        else:
            color = "red"
        return f"`{'█' * filled}{'░' * empty}`"

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on the analysis.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        # Security recommendations
        sec_score = self.score.category_scores.get(Category.SECURITY.value)
        if sec_score and sec_score.score < 90:
            recommendations.append(
                "**Security:** Address security issues immediately. "
                "Review hardcoded secrets, XSS vulnerabilities, and injection patterns."
            )

        # Performance recommendations
        perf_score = self.score.category_scores.get(Category.PERFORMANCE.value)
        if perf_score and perf_score.score < 85:
            recommendations.append(
                "**Performance:** Consider lazy loading routes, optimizing bundle imports, "
                "and adding virtualization for large lists."
            )

        # Correctness recommendations
        corr_score = self.score.category_scores.get(Category.CORRECTNESS.value)
        if corr_score and corr_score.score < 85:
            recommendations.append(
                "**Correctness:** Fix missing keys in lists, add error handling to async functions, "
                "and clean up useEffect/useState patterns."
            )

        # Best practice recommendations
        bp_score = self.score.category_scores.get(Category.BEST_PRACTICE.value)
        if bp_score and bp_score.score < 80:
            recommendations.append(
                "**Best Practices:** Remove console statements, clean up unused imports, "
                "and add proper TypeScript types."
            )

        # Accessibility recommendations
        a11y_score = self.score.category_scores.get(Category.ACCESSIBILITY.value)
        if a11y_score and a11y_score.score < 90:
            recommendations.append(
                "**Accessibility:** Add alt attributes to images, aria-labels to interactive elements, "
                "and ensure proper semantic HTML."
            )

        # General recommendations
        if self.score.total_issues > 50:
            recommendations.append(
                "**General:** High number of issues detected. Consider addressing the most critical "
                "issues first and setting up linting rules to prevent regressions."
            )

        if self.score.error_count > 0:
            recommendations.append(
                f"**Priority:** Fix {self.score.error_count} error(s) first - these are the most "
                "critical issues that should be addressed immediately."
            )

        return recommendations
