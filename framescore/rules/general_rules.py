"""Framework-agnostic general analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)
from ..utils import count_lines


class GeneralFileTooLong(BaseRule):
    """GEN-001: Detect files that are too long."""

    rule_id = "GEN-001"
    name = "File too long"
    description = "Files should be under 500 lines for maintainability."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        line_count = len(file_context.lines)
        if line_count > 500:
            issues.append(
                self.create_issue(
                    f"File is too long ({line_count} lines). "
                    "Consider splitting into smaller modules.",
                    file_context,
                    1,
                    suggestion="Break this file into smaller, focused modules.",
                )
            )
        return issues


class GeneralFunctionTooComplex(BaseRule):
    """GEN-002: Detect functions that are too long/complex."""

    rule_id = "GEN-002"
    name = "Function too complex"
    description = "Functions should be under 50 lines for readability."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detect function start
            func_match = re.match(
                r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", line
            )
            if not func_match:
                # Arrow function
                func_match = re.match(
                    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>",
                    line,
                )
            if func_match:
                func_name = func_match.group(1)
                func_start = i
                brace_count = 0
                found_open = False
                j = i
                while j < len(lines):
                    for char in lines[j]:
                        if char == "{":
                            brace_count += 1
                            found_open = True
                        elif char == "}":
                            brace_count -= 1
                            if found_open and brace_count <= 0:
                                func_length = j - func_start + 1
                                if func_length > 50:
                                    issues.append(
                                        self.create_issue(
                                            f"Function '{func_name}' is too long "
                                            f"({func_length} lines). "
                                            "Consider breaking it into smaller functions.",
                                            file_context,
                                            func_start + 1,
                                            suggestion="Extract helper functions to reduce complexity.",
                                        )
                                    )
                                i = j
                                break
                    j += 1
                    if found_open and brace_count <= 0:
                        i = j
                        break
            i += 1
        return issues


class GeneralMissingFileHeader(BaseRule):
    """GEN-003: Detect files missing header comments."""

    rule_id = "GEN-003"
    name = "Missing file header comments"
    description = "Source files should have a header comment describing their purpose."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content
        lines = file_context.lines

        if not lines:
            return issues

        # Check first 5 lines for a comment
        has_header = False
        for line in lines[:5]:
            stripped = line.strip()
            if stripped.startswith("/**") or stripped.startswith("*") or stripped.startswith("//"):
                has_header = True
                break
            if stripped.startswith("<!--"):
                has_header = True
                break

        if not has_header:
            issues.append(
                self.create_issue(
                    "File missing header comment. "
                    "Add a comment describing the purpose of this file.",
                    file_context,
                    1,
                    suggestion="Add a file header comment: /** Brief description of this module */",
                )
            )
        return issues


class GeneralInconsistentNaming(BaseRule):
    """GEN-004: Detect inconsistent naming conventions."""

    rule_id = "GEN-004"
    name = "Inconsistent naming conventions"
    description = "Use consistent naming conventions: camelCase for variables/functions, PascalCase for components."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        # Check for snake_case variable declarations in JavaScript
        for i, line in enumerate(lines):
            # Check const/let/var with snake_case
            match = re.match(r"^\s*(?:const|let|var)\s+([a-z][a-z0-9_]+)\s*=", line)
            if match:
                var_name = match.group(1)
                if "_" in var_name and not var_name.isupper():
                    issues.append(
                        self.create_issue(
                            f"Variable '{var_name}' uses snake_case. "
                            "Use camelCase for JavaScript/TypeScript variables.",
                            file_context,
                            i + 1,
                            suggestion=f"Rename to camelCase: {var_name.replace('_', '') or var_name}",
                        )
                    )
        return issues


class GeneralTodoFixmeHack(BaseRule):
    """GEN-005: Detect TODO/FIXME/HACK comments."""

    rule_id = "GEN-005"
    name = "TODO/FIXME/HACK comments"
    description = "TODO/FIXME/HACK comments indicate unfinished or problematic code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r".*"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"\bTODO\b", "TODO"),
            (r"\bFIXME\b", "FIXME"),
            (r"\bHACK\b", "HACK"),
            (r"\bXXX\b", "XXX"),
            (r"\bNOQA\b", "NOQA"),
        ]
        for pattern, label in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"{label} comment found. Track and resolve these items.",
                        file_context,
                        line,
                        suggestion=f"Address the {label} item or create a tracking issue.",
                    )
                )
        return issues


class GeneralDeadCode(BaseRule):
    """GEN-006: Detect dead code (unused exports)."""

    rule_id = "GEN-006"
    name = "Dead code (unused exports)"
    description = "Exported but unused code may indicate dead code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find exported functions
        export_func_pattern = r"export\s+(?:default\s+)?function\s+(\w+)"
        for match in re.finditer(export_func_pattern, content):
            func_name = match.group(1)
            # Check usage count (excluding the definition)
            usage = len(re.findall(rf"\b{re.escape(func_name)}\b", content))
            if usage <= 1:
                line = content[: match.start()].count("\n") + 1
                issues.append(
                    self.create_issue(
                        f"Exported function '{func_name}' appears to be unused in this file. "
                        "Verify it is imported elsewhere.",
                        file_context,
                        line,
                        suggestion=f"Verify '{func_name}' is used in other files or remove it.",
                    )
                )
        return issues


class GeneralDuplicateCode(BaseRule):
    """GEN-007: Detect duplicate code blocks."""

    rule_id = "GEN-007"
    name = "Duplicate code blocks"
    description = "Duplicate code blocks should be extracted into shared functions."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines
        content = file_context.content

        # Simple heuristic: look for repeated blocks of 3+ identical lines
        line_count = len(lines)
        if line_count < 6:
            return issues

        seen_blocks = {}
        for i in range(line_count - 3):
            block = tuple(l.strip() for l in lines[i : i + 3])
            # Skip empty or trivial blocks
            if all(not b or b == "}" or b == "{" for b in block):
                continue
            block_key = "\n".join(block)
            if block_key in seen_blocks:
                prev_line = seen_blocks[block_key]
                if i - prev_line > 3:  # Not adjacent
                    issues.append(
                        self.create_issue(
                            "Duplicate code block detected (3+ identical consecutive lines). "
                            "Extract into a shared function.",
                            file_context,
                            i + 1,
                            suggestion="Extract the duplicated code into a reusable function.",
                        )
                    )
                    seen_blocks[block_key] = i  # Only report once per pair
            else:
                seen_blocks[block_key] = i

        return issues


class GeneralMissingErrorHandling(BaseRule):
    """GEN-008: Detect missing error handling."""

    rule_id = "GEN-008"
    name = "Missing error handling"
    description = "Async operations should have proper error handling."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find async functions
        async_pattern = r"async\s+function\s+(\w+)"
        for match in re.finditer(async_pattern, content):
            func_name = match.group(1)
            start = match.start()
            # Find function body
            brace_start = content.find("{", start)
            if brace_start == -1:
                continue
            depth = 0
            end = brace_start
            for i in range(brace_start, min(brace_start + 3000, len(content))):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break

            func_body = content[brace_start:end]
            has_await = bool(re.search(r"\bawait\s+", func_body))
            has_try = bool(re.search(r"\btry\s*\{", func_body))
            has_catch = bool(re.search(r"\.catch\s*\(", func_body))

            if has_await and not has_try and not has_catch:
                line = content[: start].count("\n") + 1
                issues.append(
                    self.create_issue(
                        f"Async function '{func_name}' uses await without error handling.",
                        file_context,
                        line,
                        suggestion=f"Wrap await calls in '{func_name}' with try/catch.",
                    )
                )
        return issues


class GeneralHardcodedStrings(BaseRule):
    """GEN-009: Detect hardcoded strings (potential i18n issue)."""

    rule_id = "GEN-009"
    name = "Hardcoded strings"
    description = "Hardcoded user-facing strings may need internationalization."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        # Look for hardcoded strings in JSX/template context
        # Pattern: >Some text< or title="Some text" or placeholder="Some text"
        jsx_text_pattern = r">\s*([A-Z][a-zA-Z\s]{5,})\s*<"
        for match, line in self.find_pattern(file_context.content, jsx_text_pattern):
            text = match.group(1).strip()
            # Skip common non-user-facing text
            skip_words = {"DOCTYPE", "HTML", "HEAD", "BODY", "DIV", "SPAN", "SCRIPT", "STYLE"}
            if text.upper() not in skip_words:
                issues.append(
                    self.create_issue(
                        f"Hardcoded text detected: '{text}'. Consider using i18n.",
                        file_context,
                        line,
                        suggestion="Use an i18n library for user-facing strings.",
                    )
                )

        # Limit to first 5 issues per file
        return issues[:5]


class GeneralMissingComments(BaseRule):
    """GEN-010: Detect functions missing comments."""

    rule_id = "GEN-010"
    name = "Missing or inadequate comments"
    description = "Complex functions should have comments explaining their purpose."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Find function declarations
            func_match = re.match(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", line)
            if func_match:
                func_name = func_match.group(1)
                # Skip private methods (starting with _)
                if func_name.startswith("_"):
                    continue
                # Check if previous line(s) have a comment
                has_comment = False
                for j in range(max(0, i - 3), i):
                    stripped = lines[j].strip()
                    if stripped.startswith("/**") or stripped.startswith("*") or stripped.startswith("//"):
                        has_comment = True
                        break
                    if stripped and not stripped.startswith("*") and not stripped.startswith("//"):
                        break

                if not has_comment:
                    issues.append(
                        self.create_issue(
                            f"Function '{func_name}' lacks a comment. "
                            "Add a JSDoc comment describing its purpose.",
                            file_context,
                            i + 1,
                            suggestion=f"Add /** JSDoc comment */ before function '{func_name}'.",
                        )
                    )
        return issues


class GeneralDeepNesting(BaseRule):
    """GEN-011: Detect deeply nested code."""

    rule_id = "GEN-011"
    name = "Deep nesting"
    description = "Code nested more than 4 levels deep is hard to read. Consider early returns or extraction."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Calculate indentation level
            stripped = line.lstrip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue
            indent = len(line) - len(stripped)
            # Assuming 2-space indentation
            level = indent // 2
            if level > 4:
                issues.append(
                    self.create_issue(
                        f"Deep nesting detected (level {level}). "
                        "Consider using early returns or extracting a function.",
                        file_context,
                        i + 1,
                        suggestion="Reduce nesting with early returns, guard clauses, or function extraction.",
                    )
                )
        return issues


class GeneralMagicNumbers(BaseRule):
    """GEN-012: Detect magic numbers in code."""

    rule_id = "GEN-012"
    name = "Magic numbers"
    description = "Magic numbers should be extracted into named constants for clarity."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        # Common exceptions (not magic numbers)
        exceptions = {0, 1, -1, 2, 10, 100, 1000, 0.5, 1.0}

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip comments and imports
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("import"):
                continue

            # Find numeric literals in code context
            # Pattern: = <number>, == <number>, === <number>, <number>, > <number>, etc.
            num_pattern = r"(?:[=<>!+\-*/]|return\s+)(\d+(?:\.\d+)?)\b"
            for match in re.finditer(num_pattern, stripped):
                num_str = match.group(1)
                try:
                    num = float(num_str)
                    if num == int(num):
                        num = int(num)
                except ValueError:
                    continue

                if num in exceptions:
                    continue

                issues.append(
                    self.create_issue(
                        f"Magic number {num} detected. "
                        "Extract into a named constant.",
                        file_context,
                        i + 1,
                        suggestion=f"const CONSTANT_NAME = {num};",
                    )
                )
                break  # One per line

        return issues


class GeneralLargeParameterList(BaseRule):
    """GEN-013: Detect functions with too many parameters."""

    rule_id = "GEN-013"
    name = "Large parameter lists"
    description = "Functions with more than 5 parameters are hard to use. Consider using an options object."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find function declarations with parameters
        func_pattern = r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?)\s*\(([^)]+)\)"
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1) or match.group(2) or "anonymous"
            params = match.group(3)
            # Count parameters (rough count by commas)
            param_count = len([p.strip() for p in params.split(",") if p.strip()])
            if param_count > 5:
                line = content[: match.start()].count("\n") + 1
                issues.append(
                    self.create_issue(
                        f"Function '{func_name}' has {param_count} parameters. "
                        "Consider using an options object instead.",
                        file_context,
                        line,
                        suggestion=f"Refactor '{func_name}' to accept a single options object.",
                    )
                )
        return issues


class GeneralMissingReturnType(BaseRule):
    """GEN-014: Detect functions missing return type annotations in TypeScript."""

    rule_id = "GEN-014"
    name = "Missing return type annotations"
    description = "TypeScript functions should have explicit return type annotations."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Find function declarations without return type
            match = re.match(
                r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{",
                line,
            )
            if match:
                func_name = match.group(1)
                # Check if there's a return type annotation
                if ": " not in line[match.start() : match.start() + line[match.start() :].find(")") + 1]:
                    issues.append(
                        self.create_issue(
                            f"Function '{func_name}' missing return type annotation.",
                            file_context,
                            i + 1,
                            suggestion=f"Add return type: function {func_name}(...): ReturnType",
                        )
                    )
        return issues


class GeneralInconsistentFileNaming(BaseRule):
    """GEN-015: Detect inconsistent file naming conventions."""

    rule_id = "GEN-015"
    name = "Inconsistent file naming"
    description = "File names should follow consistent naming conventions (kebab-case for most projects)."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        filename = os.path.basename(file_context.file_path) if hasattr(file_context, 'file_path') else ""

        if not filename:
            return issues

        name, ext = os.path.splitext(filename)

        # Check for mixed naming conventions
        has_upper = bool(re.search(r"[A-Z]", name))
        has_underscore = "_" in name
        has_hyphen = "-" in name

        # Component files (PascalCase) are acceptable
        if has_upper and not has_underscore and not has_hyphen:
            return issues  # PascalCase - likely a component

        if has_upper and has_underscore:
            issues.append(
                self.create_issue(
                    f"File '{filename}' uses mixed naming (PascalCase with underscores). "
                    "Use consistent naming convention.",
                    file_context,
                    1,
                    suggestion="Rename file to use consistent kebab-case or PascalCase.",
                )
            )
        elif has_upper and has_hyphen:
            issues.append(
                self.create_issue(
                    f"File '{filename}' uses mixed naming (camelCase with hyphens). "
                    "Use consistent naming convention.",
                    file_context,
                    1,
                    suggestion="Rename file to use consistent kebab-case or PascalCase.",
                )
            )
        return issues


# Need os for basename
import os

# List of all general rules
GENERAL_RULES = [
    GeneralFileTooLong(),
    GeneralFunctionTooComplex(),
    GeneralMissingFileHeader(),
    GeneralInconsistentNaming(),
    GeneralTodoFixmeHack(),
    GeneralDeadCode(),
    GeneralDuplicateCode(),
    GeneralMissingErrorHandling(),
    GeneralHardcodedStrings(),
    GeneralMissingComments(),
    GeneralDeepNesting(),
    GeneralMagicNumbers(),
    GeneralLargeParameterList(),
    GeneralMissingReturnType(),
    GeneralInconsistentFileNaming(),
]
