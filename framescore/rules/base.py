"""Base rule class and issue data structure for FrameScore rules engine."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Severity(Enum):
    """Issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Category(Enum):
    """Rule categories."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    CORRECTNESS = "correctness"
    BEST_PRACTICE = "best-practice"
    ACCESSIBILITY = "accessibility"


class Framework(Enum):
    """Supported frameworks."""

    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    ANGULAR = "angular"
    GENERAL = "general"


@dataclass
class Issue:
    """Represents a single issue found by a rule.

    Attributes:
        rule_id: Unique identifier of the rule that found this issue.
        rule_name: Human-readable name of the rule.
        severity: Severity level of the issue.
        category: Category of the issue.
        message: Description of the issue.
        file_path: Path to the file where the issue was found.
        line: Line number where the issue was found (1-based).
        column: Optional column number.
        suggestion: Optional fix suggestion.
        framework: Framework scope of the rule.
    """

    rule_id: str
    rule_name: str
    severity: Severity
    category: Category
    message: str
    file_path: str
    line: int = 1
    column: Optional[int] = None
    suggestion: Optional[str] = None
    framework: Framework = Framework.GENERAL

    def to_dict(self) -> dict:
        """Convert issue to dictionary."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
            "framework": self.framework.value,
        }


@dataclass
class FileContext:
    """Context information about a file being analyzed.

    Attributes:
        file_path: Absolute path to the file.
        content: Full file content.
        lines: List of lines in the file.
        imports: List of import strings.
        exports: List of export names.
        framework: Detected framework for this file.
        file_extension: File extension.
        relative_path: Path relative to project root.
    """

    file_path: str
    content: str
    lines: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    framework: Framework = Framework.GENERAL
    file_extension: str = ""
    relative_path: str = ""


class BaseRule:
    """Base class for all analysis rules.

    Every rule must subclass this and implement the check method.
    """

    # Rule metadata - subclasses must define these
    rule_id: str = ""
    name: str = ""
    description: str = ""
    severity: Severity = Severity.WARNING
    category: Category = Category.BEST_PRACTICE
    framework: Framework = Framework.GENERAL

    # File patterns this rule applies to (regex)
    file_patterns: List[str] = [r".*"]

    # File patterns this rule should skip
    exclude_patterns: List[str] = [
        r"node_modules",
        r"\.min\.js",
        r"\.min\.css",
        r"dist/",
        r"build/",
        r"\.bundle\.",
        r"vendor/",
    ]

    def __init__(self):
        """Initialize the rule and compile file patterns."""
        self._compiled_patterns = [re.compile(p) for p in self.file_patterns]
        self._compiled_excludes = [re.compile(p) for p in self.exclude_patterns]

    def should_check(self, file_path: str) -> bool:
        """Check if this rule should analyze the given file.

        Args:
            file_path: Path to the file.

        Returns:
            True if the rule should check this file.
        """
        # Skip excluded paths
        for pattern in self._compiled_excludes:
            if pattern.search(file_path):
                return False
        # Check if file matches any include pattern
        for pattern in self._compiled_patterns:
            if pattern.search(file_path):
                return True
        return False

    def check(self, file_context: FileContext) -> List[Issue]:
        """Check a file for issues. Must be implemented by subclasses.

        Args:
            file_context: Context information about the file.

        Returns:
            List of issues found.
        """
        raise NotImplementedError("Subclasses must implement check()")

    def find_pattern(
        self,
        content: str,
        pattern: str,
        flags: int = 0,
    ) -> List[tuple]:
        """Find all matches of a regex pattern in content.

        Args:
            content: Source code content.
            pattern: Regex pattern string.
            flags: Regex flags.

        Returns:
            List of (match_object, line_number) tuples.
        """
        results = []
        for match in re.finditer(pattern, content, flags):
            line_num = content[: match.start()].count("\n") + 1
            results.append((match, line_num))
        return results

    def find_pattern_lines(
        self,
        lines: List[str],
        pattern: str,
        flags: int = 0,
    ) -> List[tuple]:
        """Find all matches of a regex pattern in lines.

        Args:
            lines: List of source code lines.
            pattern: Regex pattern string.
            flags: Regex flags.

        Returns:
            List of (match_object, line_number) tuples.
        """
        results = []
        for i, line in enumerate(lines):
            for match in re.finditer(pattern, line, flags):
                results.append((match, i + 1))
        return results

    def create_issue(
        self,
        message: str,
        file_context: FileContext,
        line: int = 1,
        suggestion: Optional[str] = None,
    ) -> Issue:
        """Create an issue for this rule.

        Args:
            message: Description of the issue.
            file_context: File context.
            line: Line number.
            suggestion: Optional fix suggestion.

        Returns:
            Issue instance.
        """
        return Issue(
            rule_id=self.rule_id,
            rule_name=self.name,
            severity=self.severity,
            category=self.category,
            message=message,
            file_path=file_context.relative_path or file_context.file_path,
            line=line,
            suggestion=suggestion,
            framework=self.framework,
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.rule_id}: {self.name}>"
