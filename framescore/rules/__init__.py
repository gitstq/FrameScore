"""Rule registry - manages all available rules."""

from typing import Dict, List, Optional, Type

from .base import BaseRule, Category, Framework, Severity


class RuleRegistry:
    """Registry for managing analysis rules.

    Provides methods to register, retrieve, and filter rules
    by framework, category, or severity.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._rules: Dict[str, BaseRule] = {}

    def register(self, rule: BaseRule) -> None:
        """Register a rule.

        Args:
            rule: Rule instance to register.
        """
        self._rules[rule.rule_id] = rule

    def register_all(self, rules: List[BaseRule]) -> None:
        """Register multiple rules at once.

        Args:
            rules: List of rule instances to register.
        """
        for rule in rules:
            self.register(rule)

    def get(self, rule_id: str) -> Optional[BaseRule]:
        """Get a rule by ID.

        Args:
            rule_id: Unique rule identifier.

        Returns:
            Rule instance or None if not found.
        """
        return self._rules.get(rule_id)

    def get_all(self) -> List[BaseRule]:
        """Get all registered rules.

        Returns:
            List of all registered rules.
        """
        return list(self._rules.values())

    def get_by_framework(self, framework: Framework) -> List[BaseRule]:
        """Get rules for a specific framework.

        Args:
            framework: Framework to filter by.

        Returns:
            List of rules matching the framework, plus general rules.
        """
        return [
            rule
            for rule in self._rules.values()
            if rule.framework == framework or rule.framework == Framework.GENERAL
        ]

    def get_by_category(self, category: Category) -> List[BaseRule]:
        """Get rules for a specific category.

        Args:
            category: Category to filter by.

        Returns:
            List of rules matching the category.
        """
        return [
            rule for rule in self._rules.values() if rule.category == category
        ]

    def get_by_severity(self, min_severity: Severity) -> List[BaseRule]:
        """Get rules at or above a minimum severity.

        Args:
            min_severity: Minimum severity level.

        Returns:
            List of rules at or above the severity.
        """
        severity_order = {
            Severity.INFO: 0,
            Severity.WARNING: 1,
            Severity.ERROR: 2,
        }
        min_level = severity_order.get(min_severity, 0)
        return [
            rule
            for rule in self._rules.values()
            if severity_order.get(rule.severity, 0) >= min_level
        ]

    def get_by_framework_and_severity(
        self, framework: Framework, min_severity: Severity
    ) -> List[BaseRule]:
        """Get rules for a framework at or above a minimum severity.

        Args:
            framework: Framework to filter by.
            min_severity: Minimum severity level.

        Returns:
            Filtered list of rules.
        """
        severity_order = {
            Severity.INFO: 0,
            Severity.WARNING: 1,
            Severity.ERROR: 2,
        }
        min_level = severity_order.get(min_severity, 0)
        return [
            rule
            for rule in self._rules.values()
            if (
                (rule.framework == framework or rule.framework == Framework.GENERAL)
                and severity_order.get(rule.severity, 0) >= min_level
            )
        ]

    def count(self) -> int:
        """Get total number of registered rules.

        Returns:
            Number of rules.
        """
        return len(self._rules)

    def summary(self) -> dict:
        """Get a summary of registered rules.

        Returns:
            Dictionary with counts by framework and category.
        """
        by_framework = {}
        by_category = {}
        by_severity = {"error": 0, "warning": 0, "info": 0}

        for rule in self._rules.values():
            fw = rule.framework.value
            by_framework[fw] = by_framework.get(fw, 0) + 1

            cat = rule.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

            sev = rule.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total": len(self._rules),
            "by_framework": by_framework,
            "by_category": by_category,
            "by_severity": by_severity,
        }


def create_default_registry() -> RuleRegistry:
    """Create and populate a registry with all built-in rules.

    Returns:
        RuleRegistry with all rules registered.
    """
    from .react_rules import REACT_RULES
    from .vue_rules import VUE_RULES
    from .svelte_rules import SVELTE_RULES
    from .angular_rules import ANGULAR_RULES
    from .general_rules import GENERAL_RULES
    from .security_rules import SECURITY_RULES
    from .performance_rules import PERFORMANCE_RULES

    registry = RuleRegistry()
    registry.register_all(REACT_RULES)
    registry.register_all(VUE_RULES)
    registry.register_all(SVELTE_RULES)
    registry.register_all(ANGULAR_RULES)
    registry.register_all(GENERAL_RULES)
    registry.register_all(SECURITY_RULES)
    registry.register_all(PERFORMANCE_RULES)
    return registry
