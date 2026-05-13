"""Svelte-specific analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)
from ..utils import extract_svelte_template, extract_svelte_script


class SvelteMissingKeyInEach(BaseRule):
    """SVELTE-001: Detect missing key in {#each} blocks."""

    rule_id = "SVELTE-001"
    name = "Missing key in {#each}"
    description = "{#each} blocks should have a key expression for proper DOM reuse."
    severity = Severity.ERROR
    category = Category.CORRECTNESS
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Pattern: {#each items as item} without (key)
        # Correct: {#each items as item (item.id)}
        pattern = r"\{#each\s+\w+\s+as\s+\w+\s*\}"
        for match, line in self.find_pattern(content, pattern):
            issues.append(
                self.create_issue(
                    "{#each} block without key expression. "
                    "Add a key for proper DOM reuse: {#each items as item (item.id)}",
                    file_context,
                    line,
                    suggestion="Add a key: {#each items as item (item.id)}",
                )
            )
        return issues


class SvelteUnusedVariables(BaseRule):
    """SVELTE-002: Detect unused variables in Svelte components."""

    rule_id = "SVELTE-002"
    name = "Unused variables"
    description = "Unused variables should be removed for cleaner code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_svelte_script(file_context.content)
        if not script:
            return issues

        # Find variable declarations
        var_pattern = r"(?:let|const|var)\s+(\w+)\s*="
        for match in re.finditer(var_pattern, script):
            var_name = match.group(1)
            # Skip common patterns
            if var_name.startswith("_") or var_name in ("undefined", "null", "true", "false"):
                continue

            # Count usages
            usage_pattern = rf"\b{re.escape(var_name)}\b"
            usages = re.findall(usage_pattern, script)
            if len(usages) <= 1:
                # Check if used in template
                template = extract_svelte_template(file_context.content)
                if var_name not in template:
                    line = script[: match.start()].count("\n") + 1
                    file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                    issues.append(
                        self.create_issue(
                            f"Unused variable '{var_name}' declared but never used.",
                            file_context,
                            file_line,
                            suggestion=f"Remove the unused variable '{var_name}'.",
                        )
                    )
        return issues


class SvelteMissingStorePrefix(BaseRule):
    """SVELTE-003: Detect missing $ prefix for reactive store access."""

    rule_id = "SVELTE-003"
    name = "Missing $ prefix for reactive stores"
    description = "Stores should be accessed with $ prefix for reactivity."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_svelte_script(file_context.content)
        template = extract_svelte_template(file_context.content)
        if not script:
            return issues

        # Find store imports (typically from writable, readable, derived)
        store_imports = re.findall(
            r"import\s+\{([^}]+)\}\s+from\s+['\"]svelte/store['\"]", script
        )
        if not store_imports:
            return issues

        # Find store variable assignments
        store_names = set()
        writable_pattern = r"(?:const|let)\s+(\w+)\s*=\s*writable\s*\("
        store_names.update(re.findall(writable_pattern, script))
        readable_pattern = r"(?:const|let)\s+(\w+)\s*=\s*readable\s*\("
        store_names.update(re.findall(readable_pattern, script))
        derived_pattern = r"(?:const|let)\s+(\w+)\s*=\s*derived\s*\("
        store_names.update(re.findall(derived_pattern, script))

        for store in store_names:
            # Check for usage without $ prefix in template
            # Pattern: {storeName} instead of {$storeName}
            bare_pattern = rf"\{{\s*{re.escape(store)}\s*\}}"
            for match in re.finditer(bare_pattern, template):
                line = template[: match.start()].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(template)].count("\n") + line
                issues.append(
                    self.create_issue(
                        f"Store '{store}' accessed without $ prefix. "
                        "Use ${store} for reactive store access.",
                        file_context,
                        file_line,
                        suggestion=f"Use ${store} instead of {store} for reactive access.",
                    )
                )
        return issues


class SvelteConsoleStatements(BaseRule):
    """SVELTE-004: Detect console statements in Svelte components."""

    rule_id = "SVELTE-004"
    name = "Console statements"
    description = "Console statements should be removed from production code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        console_methods = ["log", "warn", "error", "debug", "info", "trace"]
        for method in console_methods:
            pattern = rf"\bconsole\.{method}\s*\("
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"console.{method}() found. Remove console statements from production.",
                        file_context,
                        line,
                        suggestion="Remove or replace with a proper logging solution.",
                    )
                )
        return issues


class SvelteUnnecessaryReactive(BaseRule):
    """SVELTE-005: Detect unnecessary reactive declarations."""

    rule_id = "SVELTE-005"
    name = "Unnecessary reactive declarations"
    description = "$: declarations that simply reassign a variable are unnecessary."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_svelte_script(file_context.content)
        if not script:
            return issues

        # Pattern: $: x = something (simple assignment, not a statement that depends on x)
        # These are fine and expected. But $: x = x + 1 (self-referencing) is a problem
        pattern = r"\$:\s*(\w+)\s*=\s*\1\b"
        for match in re.finditer(pattern, script):
            var_name = match.group(1)
            line = script[: match.start()].count("\n") + 1
            file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
            issues.append(
                self.create_issue(
                    f"Self-referencing reactive statement '$: {var_name} = {var_name} ...' "
                    "may cause infinite loops.",
                    file_context,
                    file_line,
                    suggestion="Review the reactive statement logic to avoid infinite loops.",
                )
            )
        return issues


class SvelteMissingTypeAnnotations(BaseRule):
    """SVELTE-006: Detect missing type annotations in TypeScript Svelte components."""

    rule_id = "SVELTE-006"
    name = "Missing type annotations"
    description = "TypeScript Svelte components should have proper type annotations."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_svelte_script(file_context.content)
        if not script:
            return issues

        # Check if using TypeScript (lang="ts")
        lang_match = re.search(r'<script\s+[^>]*lang\s*=\s*["\']ts["\']', file_context.content)
        if not lang_match:
            return issues

        # Find function parameters without types
        func_pattern = r"(?:function\s+\w+|\w+)\s*\(([^)]+)\)"
        for match in re.finditer(func_pattern, script):
            params = match.group(1)
            # Check for untyped parameters
            for param in params.split(","):
                param = param.strip()
                if not param:
                    continue
                # Remove default values
                param_name = param.split("=")[0].strip()
                if ":" not in param_name and param_name and not param_name.startswith("..."):
                    line = script[: match.start()].count("\n") + 1
                    file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                    issues.append(
                        self.create_issue(
                            f"Parameter '{param_name}' missing type annotation in TypeScript component.",
                            file_context,
                            file_line,
                            suggestion=f"Add type annotation: {param_name}: TypeName",
                        )
                    )
        return issues


class SvelteAccessibilityIssues(BaseRule):
    """SVELTE-007: Detect accessibility issues in Svelte components."""

    rule_id = "SVELTE-007"
    name = "Accessibility issues (missing aria labels)"
    description = "Interactive elements should have proper ARIA labels for accessibility."
    severity = Severity.WARNING
    category = Category.ACCESSIBILITY
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        template = extract_svelte_template(file_context.content)
        if not template:
            return issues

        # Check for buttons without text content or aria-label
        btn_pattern = r"<button\b([^>]*)>\s*(?:<\/button>|<\/\s*button>)"
        for match in re.finditer(btn_pattern, template):
            attrs = match.group(1)
            if not re.search(r"aria-label|aria-labelledby", attrs):
                line = template[: match.start()].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(template)].count("\n") + line
                issues.append(
                    self.create_issue(
                        "Button element without text content or aria-label attribute.",
                        file_context,
                        file_line,
                        suggestion='Add aria-label="description" or text content to the button.',
                    )
                )

        # Check for images without alt
        img_pattern = r"<img\b([^>]*?)(?<!\balt\s*=\s*[^>]*?)(/?)>"
        for match in re.finditer(img_pattern, template):
            attrs = match.group(1)
            if not re.search(r"\balt\s*=", attrs):
                line = template[: match.start()].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(template)].count("\n") + line
                issues.append(
                    self.create_issue(
                        "img element missing alt attribute for accessibility.",
                        file_context,
                        file_line,
                        suggestion='Add alt="description" to the img element.',
                    )
                )

        # Check for inputs without labels
        input_pattern = r"<input\b([^>]*)>"
        for match in re.finditer(input_pattern, template):
            attrs = match.group(1)
            input_id = re.search(r"id\s*=\s*['\"]([^'\"]+)['\"]", attrs)
            if input_id:
                input_id_val = input_id.group(1)
                # Check if there's a label for this input
                label_pattern = rf'<label\s+[^>]*for\s*=\s*["\']' + re.escape(input_id_val) + r'["\']'
                if not re.search(label_pattern, template):
                    line = template[: match.start()].count("\n") + 1
                    file_line = file_context.content[: file_context.content.find(template)].count("\n") + line
                    issues.append(
                        self.create_issue(
                            f"Input with id='{input_id_val}' missing associated label element.",
                            file_context,
                            file_line,
                            suggestion=f"Add a <label for='{input_id_val}'> element.",
                        )
                    )
        return issues


class SvelteLargeComponentFiles(BaseRule):
    """SVELTE-008: Detect large Svelte component files."""

    rule_id = "SVELTE-008"
    name = "Large component files"
    description = "Component files should be under 300 lines for maintainability."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.SVELTE
    file_patterns = [r"\.svelte$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        line_count = len(file_context.lines)
        if line_count > 300:
            issues.append(
                self.create_issue(
                    f"Large component file ({line_count} lines). "
                    "Consider splitting into smaller components.",
                    file_context,
                    1,
                    suggestion="Break this component into smaller, focused sub-components.",
                )
            )
        return issues


# List of all Svelte rules
SVELTE_RULES = [
    SvelteMissingKeyInEach(),
    SvelteUnusedVariables(),
    SvelteMissingStorePrefix(),
    SvelteConsoleStatements(),
    SvelteUnnecessaryReactive(),
    SvelteMissingTypeAnnotations(),
    SvelteAccessibilityIssues(),
    SvelteLargeComponentFiles(),
]
