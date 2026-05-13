"""Health score calculation engine."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .rules.base import Category, Issue, Severity
from .analyzer import AnalysisResult


@dataclass
class CategoryScore:
    """Score breakdown for a single category.

    Attributes:
        category: Category name.
        score: Score from 0 to 100.
        issues_count: Number of issues in this category.
        deductions: Total points deducted.
    """

    category: str
    score: float = 100.0
    issues_count: int = 0
    deductions: float = 0.0


@dataclass
class ModuleScore:
    """Score for a single module (directory or file).

    Attributes:
        module_path: Path to the module.
        score: Score from 0 to 100.
        issues_count: Total issues in this module.
    """

    module_path: str
    score: float = 100.0
    issues_count: int = 0


@dataclass
class HealthScore:
    """Overall health score for a project.

    Attributes:
        overall_score: Overall health score (0-100).
        grade: Letter grade (A+ through F).
        category_scores: Breakdown by category.
        module_scores: Breakdown by module/directory.
        total_issues: Total number of issues.
        error_count: Number of error-level issues.
        warning_count: Number of warning-level issues.
        info_count: Number of info-level issues.
        deductions: Total points deducted.
    """

    overall_score: float = 100.0
    grade: str = "A+"
    category_scores: Dict[str, CategoryScore] = field(default_factory=dict)
    module_scores: Dict[str, ModuleScore] = field(default_factory=dict)
    total_issues: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    deductions: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with all score information.
        """
        return {
            "overall_score": round(self.overall_score, 1),
            "grade": self.grade,
            "total_issues": self.total_issues,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "deductions": round(self.deductions, 1),
            "category_scores": {
                k: {
                    "score": round(v.score, 1),
                    "issues_count": v.issues_count,
                    "deductions": round(v.deductions, 1),
                }
                for k, v in self.category_scores.items()
            },
            "module_scores": {
                k: {
                    "score": round(v.score, 1),
                    "issues_count": v.issues_count,
                }
                for k, v in self.module_scores.items()
            },
        }


# Points deducted per severity level
SEVERITY_WEIGHTS = {
    Severity.ERROR: 5.0,
    Severity.WARNING: 2.0,
    Severity.INFO: 0.5,
}

# Grade thresholds
GRADE_THRESHOLDS = [
    (95, "A+"),
    (90, "A"),
    (85, "B+"),
    (80, "B"),
    (75, "C+"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


class Scorer:
    """Calculates health scores from analysis results.

    Computes weighted scores based on issue severity,
    with breakdowns by category and module.
    """

    def __init__(self):
        """Initialize the scorer with default weights."""
        self.severity_weights = dict(SEVERITY_WEIGHTS)

    def calculate(self, result: AnalysisResult) -> HealthScore:
        """Calculate the health score from analysis results.

        Args:
            result: Analysis result with all found issues.

        Returns:
            HealthScore with overall score, grade, and breakdowns.
        """
        health = HealthScore()

        if not result.issues:
            health.overall_score = 100.0
            health.grade = "A+"
            self._init_category_scores(health)
            return health

        # Count issues by severity
        health.total_issues = len(result.issues)
        for issue in result.issues:
            if issue.severity == Severity.ERROR:
                health.error_count += 1
            elif issue.severity == Severity.WARNING:
                health.warning_count += 1
            else:
                health.info_count += 1

        # Calculate total deductions
        total_deductions = 0.0
        for issue in result.issues:
            weight = self.severity_weights.get(issue.severity, 0.5)
            total_deductions += weight

        health.deductions = total_deductions

        # Calculate overall score (minimum 0)
        health.overall_score = max(0.0, 100.0 - total_deductions)

        # Assign grade
        health.grade = self._assign_grade(health.overall_score)

        # Calculate category scores
        self._calculate_category_scores(health, result.issues)

        # Calculate module scores
        self._calculate_module_scores(health, result.issues)

        return health

    def _assign_grade(self, score: float) -> str:
        """Assign a letter grade based on the score.

        Args:
            score: Numeric score (0-100).

        Returns:
            Letter grade string.
        """
        for threshold, grade in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"

    def _init_category_scores(self, health: HealthScore) -> None:
        """Initialize category scores to 100.

        Args:
            health: HealthScore to initialize.
        """
        categories = [
            Category.SECURITY.value,
            Category.PERFORMANCE.value,
            Category.CORRECTNESS.value,
            Category.BEST_PRACTICE.value,
            Category.ACCESSIBILITY.value,
        ]
        for cat in categories:
            health.category_scores[cat] = CategoryScore(
                category=cat, score=100.0, issues_count=0, deductions=0.0
            )

    def _calculate_category_scores(
        self, health: HealthScore, issues: List[Issue]
    ) -> None:
        """Calculate scores for each category.

        Args:
            health: HealthScore to populate.
            issues: List of all issues.
        """
        # Group issues by category
        category_issues: Dict[str, List[Issue]] = {}
        for issue in issues:
            cat = issue.category.value
            if cat not in category_issues:
                category_issues[cat] = []
            category_issues[cat].append(issue)

        # Calculate score for each category
        all_categories = [
            Category.SECURITY.value,
            Category.PERFORMANCE.value,
            Category.CORRECTNESS.value,
            Category.BEST_PRACTICE.value,
            Category.ACCESSIBILITY.value,
        ]

        for cat in all_categories:
            cat_issues = category_issues.get(cat, [])
            deductions = sum(
                self.severity_weights.get(i.severity, 0.5) for i in cat_issues
            )
            score = max(0.0, 100.0 - deductions)
            health.category_scores[cat] = CategoryScore(
                category=cat,
                score=score,
                issues_count=len(cat_issues),
                deductions=deductions,
            )

    def _calculate_module_scores(
        self, health: HealthScore, issues: List[Issue]
    ) -> None:
        """Calculate scores for each module/directory.

        Args:
            health: HealthScore to populate.
            issues: List of all issues.
        """
        # Group issues by directory (top-level directory)
        module_issues: Dict[str, List[Issue]] = {}
        for issue in issues:
            parts = issue.file_path.replace("\\", "/").split("/")
            if len(parts) > 1:
                module = parts[0]
            else:
                module = "(root)"
            if module not in module_issues:
                module_issues[module] = []
            module_issues[module].append(issue)

        # Calculate score for each module
        for module, mod_issues in module_issues.items():
            deductions = sum(
                self.severity_weights.get(i.severity, 0.5) for i in mod_issues
            )
            score = max(0.0, 100.0 - deductions)
            health.module_scores[module] = ModuleScore(
                module_path=module,
                score=score,
                issues_count=len(mod_issues),
            )

    def compare_scores(
        self, current: HealthScore, previous: HealthScore
    ) -> dict:
        """Compare two health scores and return the difference.

        Args:
            current: Current health score.
            previous: Previous health score.

        Returns:
            Dictionary with score differences.
        """
        return {
            "score_change": round(current.overall_score - previous.overall_score, 1),
            "issue_change": current.total_issues - previous.total_issues,
            "error_change": current.error_count - previous.error_count,
            "warning_change": current.warning_count - previous.warning_count,
            "info_change": current.info_count - previous.info_count,
            "grade_change": current.grade != previous.grade,
            "improved": current.overall_score > previous.overall_score,
        }
