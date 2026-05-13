"""Rule execution engine with parallel analysis support."""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set

from .rules.base import BaseRule, FileContext, Framework, Issue
from .rules import RuleRegistry
from .scanner import ProjectInfo, ProjectScanner
from .utils import ProgressBar


class AnalysisResult:
    """Container for analysis results.

    Attributes:
        issues: List of all issues found.
        files_analyzed: Number of files analyzed.
        files_skipped: Number of files skipped.
        rules_run: Number of rules executed.
        analysis_time: Time taken for analysis in seconds.
        project_info: Project information.
    """

    def __init__(self):
        """Initialize empty analysis result."""
        self.issues: List[Issue] = []
        self.files_analyzed: int = 0
        self.files_skipped: int = 0
        self.rules_run: int = 0
        self.analysis_time: float = 0.0
        self.project_info: Optional[ProjectInfo] = None

    def get_issues_by_severity(self) -> Dict[str, List[Issue]]:
        """Group issues by severity.

        Returns:
            Dictionary mapping severity to list of issues.
        """
        result = {"error": [], "warning": [], "info": []}
        for issue in self.issues:
            sev = issue.severity.value
            if sev in result:
                result[sev].append(issue)
        return result

    def get_issues_by_category(self) -> Dict[str, List[Issue]]:
        """Group issues by category.

        Returns:
            Dictionary mapping category to list of issues.
        """
        result = {}
        for issue in self.issues:
            cat = issue.category.value
            if cat not in result:
                result[cat] = []
            result[cat].append(issue)
        return result

    def get_issues_by_file(self) -> Dict[str, List[Issue]]:
        """Group issues by file path.

        Returns:
            Dictionary mapping file path to list of issues.
        """
        result = {}
        for issue in self.issues:
            fp = issue.file_path
            if fp not in result:
                result[fp] = []
            result[fp].append(issue)
        return result

    def get_top_issues(self, limit: int = 10) -> List[Issue]:
        """Get the most severe issues.

        Args:
            limit: Maximum number of issues to return.

        Returns:
            List of top issues sorted by severity.
        """
        severity_order = {"error": 0, "warning": 1, "info": 2}
        sorted_issues = sorted(
            self.issues,
            key=lambda x: severity_order.get(x.severity.value, 3),
        )
        return sorted_issues[:limit]


class Analyzer:
    """Rule execution engine that runs all applicable rules against project files.

    Supports parallel rule execution using ThreadPoolExecutor.
    """

    def __init__(
        self,
        registry: RuleRegistry,
        project_info: ProjectInfo,
        max_workers: int = 4,
        show_progress: bool = True,
    ):
        """Initialize the analyzer.

        Args:
            registry: Rule registry with all rules.
            project_info: Scanned project information.
            max_workers: Maximum number of parallel workers.
            show_progress: Whether to show progress bar.
        """
        self.registry = registry
        self.project_info = project_info
        self.max_workers = max_workers
        self.show_progress = show_progress

    def analyze(self, min_severity: str = "info") -> AnalysisResult:
        """Run all applicable rules against project files.

        Args:
            min_severity: Minimum severity level ('error', 'warning', 'info').

        Returns:
            AnalysisResult with all found issues.
        """
        from .rules.base import Severity

        start_time = time.time()
        result = AnalysisResult()
        result.project_info = self.project_info

        # Get applicable rules
        severity_map = {"error": Severity.ERROR, "warning": Severity.WARNING, "info": Severity.INFO}
        min_sev = severity_map.get(min_severity.lower(), Severity.INFO)

        framework = self.project_info.framework
        applicable_rules = self.registry.get_by_framework_and_severity(framework, min_sev)

        if not applicable_rules:
            return result

        # Build file contexts
        scanner = ProjectScanner(self.project_info.root_path)
        file_contexts = []
        for file_path in self.project_info.files:
            ctx = scanner.build_file_context(file_path, framework)
            file_contexts.append(ctx)

        # Run analysis
        if self.show_progress:
            progress = ProgressBar(
                len(file_contexts),
                prefix="Analyzing",
            )
        else:
            progress = None

        all_issues = []
        rules_run_set = set()

        # Use thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for ctx in file_contexts:
                future = executor.submit(
                    self._analyze_file, ctx, applicable_rules
                )
                futures[future] = ctx

            for future in as_completed(futures):
                ctx = futures[future]
                try:
                    file_issues = future.result()
                    all_issues.extend(file_issues)
                    result.files_analyzed += 1
                    for issue in file_issues:
                        rules_run_set.add(issue.rule_id)
                except Exception:
                    result.files_skipped += 1

                if progress:
                    progress.update()

        if progress:
            progress.finish()

        result.issues = all_issues
        result.rules_run = len(rules_run_set)
        result.analysis_time = time.time() - start_time

        return result

    def _analyze_file(
        self, file_context: FileContext, rules: List[BaseRule]
    ) -> List[Issue]:
        """Analyze a single file with all applicable rules.

        Args:
            file_context: Context for the file to analyze.
            rules: List of rules to apply.

        Returns:
            List of issues found in the file.
        """
        issues = []
        for rule in rules:
            if rule.should_check(file_context.file_path):
                try:
                    file_issues = rule.check(file_context)
                    issues.extend(file_issues)
                except Exception:
                    # Silently skip rules that fail
                    pass
        return issues

    def analyze_incremental(
        self, changed_files: List[str], min_severity: str = "info"
    ) -> AnalysisResult:
        """Analyze only changed files for incremental analysis.

        Args:
            changed_files: List of changed file paths.
            min_severity: Minimum severity level.

        Returns:
            AnalysisResult for the changed files.
        """
        from .rules.base import Severity

        start_time = time.time()
        result = AnalysisResult()
        result.project_info = self.project_info

        severity_map = {"error": Severity.ERROR, "warning": Severity.WARNING, "info": Severity.INFO}
        min_sev = severity_map.get(min_severity.lower(), Severity.INFO)

        framework = self.project_info.framework
        applicable_rules = self.registry.get_by_framework_and_severity(framework, min_sev)

        scanner = ProjectScanner(self.project_info.root_path)
        all_issues = []
        rules_run_set = set()

        for file_path in changed_files:
            if not os.path.exists(file_path):
                continue
            ctx = scanner.build_file_context(file_path, framework)
            file_issues = self._analyze_file(ctx, applicable_rules)
            all_issues.extend(file_issues)
            result.files_analyzed += 1
            for issue in file_issues:
                rules_run_set.add(issue.rule_id)

        result.issues = all_issues
        result.rules_run = len(rules_run_set)
        result.analysis_time = time.time() - start_time

        return result
