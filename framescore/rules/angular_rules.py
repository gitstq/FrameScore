"""Angular-specific analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)


class AngularMissingTrackBy(BaseRule):
    """ANGULAR-001: Detect missing trackBy in *ngFor directives."""

    rule_id = "ANGULAR-001"
    name = "Missing trackBy in *ngFor"
    description = "*ngFor should use trackBy for better performance with large lists."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.ANGULAR
    file_patterns = [r"\.(ts|html)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Pattern: *ngFor without trackBy
        pattern = r"\*ngFor\s*=\s*['\"]"
        for match in re.finditer(pattern, content):
            # Find the full directive value
            start = match.end()
            end = content.find('"', start)
            if end == -1:
                end = content.find("'", start)
            if end == -1:
                continue
            directive_value = content[start:end]
            if "trackBy" not in directive_value:
                line = content[: match.start()].count("\n") + 1
                issues.append(
                    self.create_issue(
                        "*ngFor directive without trackBy function. "
                        "Add trackBy for better rendering performance.",
                        file_context,
                        line,
                        suggestion="Add trackBy to *ngFor: *ngFor='let item of items; trackBy: trackById'",
                    )
                )
        return issues


class AngularAnyType(BaseRule):
    """ANGULAR-002: Detect 'any' type usage in Angular TypeScript files."""

    rule_id = "ANGULAR-002"
    name = "Using 'any' type"
    description = "Avoid using 'any' type in TypeScript. Use specific types for better type safety."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r":\s*any\b", "explicit 'any' type annotation"),
            (r"\bas\s+any\b", "'as any' type assertion"),
            (r"<any>", "generic 'any' type parameter"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"TypeScript 'any' type detected ({desc}). "
                        "Use specific types for better type safety.",
                        file_context,
                        line,
                        suggestion="Replace 'any' with the appropriate type or 'unknown'.",
                    )
                )
        return issues


class AngularConsoleStatements(BaseRule):
    """ANGULAR-003: Detect console statements in Angular files."""

    rule_id = "ANGULAR-003"
    name = "Console statements"
    description = "Console statements should be removed from production code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.ANGULAR
    file_patterns = [r"\.(ts|html)$"]

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
                        suggestion="Use Angular's logging service or remove console statements.",
                    )
                )
        return issues


class AngularUnusedImports(BaseRule):
    """ANGULAR-004: Detect unused imports in Angular TypeScript files."""

    rule_id = "ANGULAR-004"
    name = "Unused imports"
    description = "Unused imports should be removed for cleaner code and smaller bundles."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find all imports
        import_pattern = r"^import\s+(?:(?:\{([^}]+)\})|(\w+))\s+from\s+['\"]([^'\"]+)['\"];?"
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            line = content[: match.start()].count("\n") + 1
            named_imports = match.group(1)
            default_import = match.group(2)

            if named_imports:
                for imp in named_imports.split(","):
                    imp_name = imp.strip().split(" as ")[0].strip()
                    if not imp_name or imp_name == "type":
                        continue
                    usage_pattern = rf"\b{re.escape(imp_name)}\b"
                    usages = re.findall(usage_pattern, content)
                    if len(usages) <= 1:
                        issues.append(
                            self.create_issue(
                                f"Unused import: '{imp_name}' is imported but never used.",
                                file_context,
                                line,
                                suggestion=f"Remove '{imp_name}' from the import statement.",
                            )
                        )

            if default_import:
                usage_pattern = rf"\b{re.escape(default_import)}\b"
                usages = re.findall(usage_pattern, content)
                if len(usages) <= 1:
                    issues.append(
                        self.create_issue(
                            f"Unused import: '{default_import}' is imported but never used.",
                            file_context,
                            line,
                            suggestion=f"Remove the import of '{default_import}'.",
                        )
                    )
        return issues


class AngularMissingOnPush(BaseRule):
    """ANGULAR-005: Detect components missing OnPush change detection strategy."""

    rule_id = "ANGULAR-005"
    name = "Missing OnPush change detection"
    description = "Components should use OnPush change detection for better performance."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check if file is a component (has @Component decorator)
        has_component = bool(re.search(r"@Component\s*\(", content))
        if not has_component:
            return issues

        # Check if OnPush is already set
        has_onpush = bool(re.search(r"changeDetection\s*:\s*ChangeDetectionStrategy\.OnPush", content))
        if has_onpush:
            return issues

        issues.append(
            self.create_issue(
                "Angular component without OnPush change detection strategy. "
                "OnPush can significantly improve performance.",
                file_context,
                1,
                suggestion="Add changeDetection: ChangeDetectionStrategy.OnPush to @Component.",
            )
        )
        return issues


class AngularDirectDOMAccess(BaseRule):
    """ANGULAR-006: Detect direct DOM access in Angular components."""

    rule_id = "ANGULAR-006"
    name = "Direct DOM access"
    description = "Avoid direct DOM access. Use Angular's Renderer2 or template references instead."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        dom_patterns = [
            (r"\bdocument\.getElementById\s*\(", "document.getElementById"),
            (r"\bdocument\.querySelector\s*\(", "document.querySelector"),
            (r"\bdocument\.querySelectorAll\s*\(", "document.querySelectorAll"),
            (r"\bdocument\.createElement\s*\(", "document.createElement"),
            (r"\bnativeElement\b", "nativeElement direct access"),
        ]
        for pattern, name in dom_patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Direct DOM access detected: {name}. "
                        "Use Angular's Renderer2 or @ViewChild instead.",
                        file_context,
                        line,
                        suggestion="Use Renderer2 or @ViewChild/@ViewChildren for DOM access.",
                    )
                )
        return issues


class AngularMissingSubscriptionUnsubscribe(BaseRule):
    """ANGULAR-007: Detect missing subscription unsubscribe in Angular components."""

    rule_id = "ANGULAR-007"
    name = "Missing subscription unsubscribe"
    description = "Observable subscriptions should be unsubscribed to prevent memory leaks."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check if file is a component
        has_component = bool(re.search(r"@Component\s*\(", content))
        if not has_component:
            return issues

        # Find .subscribe() calls
        subscribe_pattern = r"\.subscribe\s*\("
        subscribe_matches = list(re.finditer(subscribe_pattern, content))

        if not subscribe_matches:
            return issues

        # Check for unsubscribe patterns
        has_unsubscribe = bool(
            re.search(
                r"(?:unsubscribe|takeUntil|async\s*pipe|\.pipe\s*\(\s*takeUntil)",
                content,
            )
        )
        has_destroy = bool(re.search(r"ngOnDestroy", content))

        if subscribe_matches and not has_unsubscribe:
            if has_destroy:
                # Has ngOnDestroy but no unsubscribe pattern
                for match in subscribe_matches[:3]:  # Report first 3
                    line = content[: match.start()].count("\n") + 1
                    issues.append(
                        self.create_issue(
                            "Observable subscription without unsubscribe. "
                            "Use takeUntil pattern or manual unsubscribe in ngOnDestroy.",
                            file_context,
                            line,
                            suggestion="Use takeUntil(this.destroy$) or call .unsubscribe() in ngOnDestroy.",
                        )
                    )
            else:
                # No ngOnDestroy at all
                for match in subscribe_matches[:3]:
                    line = content[: match.start()].count("\n") + 1
                    issues.append(
                        self.create_issue(
                            "Observable subscription without cleanup. "
                            "Implement ngOnDestroy and unsubscribe.",
                            file_context,
                            line,
                            suggestion="Add ngOnDestroy and unsubscribe from all observables.",
                        )
                    )
        return issues


class AngularLargeComponentFiles(BaseRule):
    """ANGULAR-008: Detect large Angular component files."""

    rule_id = "ANGULAR-008"
    name = "Large component files"
    description = "Component files should be under 300 lines for maintainability."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.ANGULAR
    file_patterns = [r"\.ts$"]

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
                    suggestion="Break this component into smaller, focused components.",
                )
            )
        return issues


# List of all Angular rules
ANGULAR_RULES = [
    AngularMissingTrackBy(),
    AngularAnyType(),
    AngularConsoleStatements(),
    AngularUnusedImports(),
    AngularMissingOnPush(),
    AngularDirectDOMAccess(),
    AngularMissingSubscriptionUnsubscribe(),
    AngularLargeComponentFiles(),
]
