"""Tests for the health score calculator."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framescore.scorer import Scorer, HealthScore
from framescore.analyzer import AnalysisResult
from framescore.rules.base import (
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)


class TestScorer(unittest.TestCase):
    """Tests for the Scorer class."""

    def test_perfect_score(self):
        """Test that no issues gives a perfect score."""
        scorer = Scorer()
        result = AnalysisResult()
        score = scorer.calculate(result)
        self.assertEqual(score.overall_score, 100.0)
        self.assertEqual(score.grade, "A+")
        self.assertEqual(score.total_issues, 0)

    def test_error_deduction(self):
        """Test that errors deduct 5 points each."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="TEST-001",
                rule_name="Test",
                severity=Severity.ERROR,
                category=Category.CORRECTNESS,
                message="Test error",
                file_path="test.jsx",
                line=1,
            ),
        ]
        score = scorer.calculate(result)
        self.assertEqual(score.overall_score, 95.0)
        self.assertEqual(score.error_count, 1)
        self.assertEqual(score.grade, "A+")

    def test_warning_deduction(self):
        """Test that warnings deduct 2 points each."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="TEST-001",
                rule_name="Test",
                severity=Severity.WARNING,
                category=Category.BEST_PRACTICE,
                message="Test warning",
                file_path="test.jsx",
                line=1,
            ),
        ]
        score = scorer.calculate(result)
        self.assertEqual(score.overall_score, 98.0)
        self.assertEqual(score.warning_count, 1)

    def test_info_deduction(self):
        """Test that info issues deduct 0.5 points each."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="TEST-001",
                rule_name="Test",
                severity=Severity.INFO,
                category=Category.BEST_PRACTICE,
                message="Test info",
                file_path="test.jsx",
                line=1,
            ),
        ]
        score = scorer.calculate(result)
        self.assertEqual(score.overall_score, 99.5)
        self.assertEqual(score.info_count, 1)

    def test_mixed_issues(self):
        """Test score with mixed severity issues."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="TEST-001", rule_name="Test", severity=Severity.ERROR,
                category=Category.SECURITY, message="err", file_path="a.jsx", line=1,
            ),
            Issue(
                rule_id="TEST-002", rule_name="Test", severity=Severity.WARNING,
                category=Category.PERFORMANCE, message="warn", file_path="b.jsx", line=1,
            ),
            Issue(
                rule_id="TEST-003", rule_name="Test", severity=Severity.INFO,
                category=Category.BEST_PRACTICE, message="info", file_path="c.jsx", line=1,
            ),
        ]
        score = scorer.calculate(result)
        # 100 - 5 - 2 - 0.5 = 92.5
        self.assertEqual(score.overall_score, 92.5)
        self.assertEqual(score.grade, "A")
        self.assertEqual(score.total_issues, 3)
        self.assertEqual(score.error_count, 1)
        self.assertEqual(score.warning_count, 1)
        self.assertEqual(score.info_count, 1)

    def test_score_floor(self):
        """Test that score doesn't go below 0."""
        scorer = Scorer()
        result = AnalysisResult()
        # 30 errors = 150 points deduction
        for i in range(30):
            result.issues.append(
                Issue(
                    rule_id=f"TEST-{i:03d}", rule_name="Test",
                    severity=Severity.ERROR, category=Category.SECURITY,
                    message="err", file_path="test.jsx", line=i + 1,
                )
            )
        score = scorer.calculate(result)
        self.assertEqual(score.overall_score, 0.0)
        self.assertEqual(score.grade, "F")

    def test_grade_assignment(self):
        """Test grade assignment thresholds."""
        scorer = Scorer()

        test_cases = [
            (97, "A+"),
            (92, "A"),
            (87, "B+"),
            (82, "B"),
            (77, "C+"),
            (72, "C"),
            (65, "D"),
            (50, "F"),
        ]

        for target_score, expected_grade in test_cases:
            result = AnalysisResult()
            # Calculate needed deductions
            deduction = 100.0 - target_score
            # Add errors (5 pts each)
            num_errors = int(deduction // 5)
            remaining = deduction - num_errors * 5
            num_warnings = int(remaining // 2)
            remaining = remaining - num_warnings * 2
            num_info = int(remaining // 0.5)

            for i in range(num_errors):
                result.issues.append(
                    Issue(
                        rule_id=f"E-{i}", rule_name="E", severity=Severity.ERROR,
                        category=Category.SECURITY, message="e", file_path="t.jsx", line=1,
                    )
                )
            for i in range(num_warnings):
                result.issues.append(
                    Issue(
                        rule_id=f"W-{i}", rule_name="W", severity=Severity.WARNING,
                        category=Category.PERFORMANCE, message="w", file_path="t.jsx", line=1,
                    )
                )
            for i in range(num_info):
                result.issues.append(
                    Issue(
                        rule_id=f"I-{i}", rule_name="I", severity=Severity.INFO,
                        category=Category.BEST_PRACTICE, message="i", file_path="t.jsx", line=1,
                    )
                )

            score = scorer.calculate(result)
            self.assertEqual(
                score.grade, expected_grade,
                f"Score {score.overall_score} expected grade {expected_grade}, got {score.grade}",
            )

    def test_category_breakdown(self):
        """Test category score breakdown."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="SEC-001", rule_name="Sec", severity=Severity.ERROR,
                category=Category.SECURITY, message="sec", file_path="a.jsx", line=1,
            ),
            Issue(
                rule_id="PERF-001", rule_name="Perf", severity=Severity.WARNING,
                category=Category.PERFORMANCE, message="perf", file_path="b.jsx", line=1,
            ),
        ]
        score = scorer.calculate(result)

        self.assertIn(Category.SECURITY.value, score.category_scores)
        self.assertIn(Category.PERFORMANCE.value, score.category_scores)
        self.assertEqual(score.category_scores[Category.SECURITY.value].score, 95.0)
        self.assertEqual(score.category_scores[Category.PERFORMANCE.value].score, 98.0)

    def test_module_breakdown(self):
        """Test module score breakdown."""
        scorer = Scorer()
        result = AnalysisResult()
        result.issues = [
            Issue(
                rule_id="TEST-001", rule_name="Test", severity=Severity.ERROR,
                category=Category.SECURITY, message="err",
                file_path="src/components/Header.jsx", line=1,
            ),
            Issue(
                rule_id="TEST-002", rule_name="Test", severity=Severity.WARNING,
                category=Category.BEST_PRACTICE, message="warn",
                file_path="src/components/Header.jsx", line=2,
            ),
            Issue(
                rule_id="TEST-003", rule_name="Test", severity=Severity.ERROR,
                category=Category.CORRECTNESS, message="err",
                file_path="src/utils/helpers.js", line=1,
            ),
        ]
        score = scorer.calculate(result)

        self.assertIn("src", score.module_scores)
        # src/components/Header.jsx: 2 issues = -7
        # src/utils/helpers.js: 1 issue = -5

    def test_compare_scores(self):
        """Test score comparison."""
        scorer = Scorer()

        current = HealthScore()
        current.overall_score = 85.0
        current.total_issues = 10
        current.error_count = 2
        current.warning_count = 5
        current.info_count = 3
        current.grade = "B+"

        previous = HealthScore()
        previous.overall_score = 75.0
        previous.total_issues = 15
        previous.error_count = 4
        previous.warning_count = 7
        previous.info_count = 4
        previous.grade = "C+"

        diff = scorer.compare_scores(current, previous)
        self.assertEqual(diff["score_change"], 10.0)
        self.assertEqual(diff["issue_change"], -5)
        self.assertTrue(diff["improved"])

    def test_health_score_to_dict(self):
        """Test HealthScore serialization."""
        score = HealthScore()
        score.overall_score = 92.5
        score.grade = "A"
        score.total_issues = 5
        d = score.to_dict()

        self.assertEqual(d["overall_score"], 92.5)
        self.assertEqual(d["grade"], "A")
        self.assertEqual(d["total_issues"], 5)
        self.assertIn("category_scores", d)
        self.assertIn("module_scores", d)


if __name__ == "__main__":
    unittest.main()
