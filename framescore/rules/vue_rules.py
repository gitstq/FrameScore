"""Vue-specific analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)
from ..utils import extract_vue_template, extract_vue_script


class VueMissingKeyInVFor(BaseRule):
    """VUE-001: Detect missing key in v-for directives."""

    rule_id = "VUE-001"
    name = "Missing key in v-for"
    description = "v-for directives should always have a :key attribute for proper rendering."
    severity = Severity.ERROR
    category = Category.CORRECTNESS
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        template = extract_vue_template(file_context.content)
        if not template:
            return issues

        # Find v-for without :key
        # Pattern: v-for="..." without :key or v-bind:key nearby
        lines = template.split("\n")
        for i, line in enumerate(lines):
            if re.search(r"v-for\s*=", line):
                if not re.search(r":key\s*=|v-bind:key\s*=", line):
                    # Check next few lines for key
                    found_key = False
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if re.search(r":key\s*=|v-bind:key\s*=", lines[j]):
                            found_key = True
                            break
                    if not found_key:
                        file_line = file_context.content[: file_context.content.find(line)].count("\n") + 1
                        issues.append(
                            self.create_issue(
                                "v-for directive without :key attribute. "
                                "Always use :key with v-for for proper list rendering.",
                                file_context,
                                file_line,
                                suggestion='Add :key="item.id" to the element with v-for.',
                            )
                        )
        return issues


class VueVIfAndVForOnSameElement(BaseRule):
    """VUE-002: Detect v-if and v-for on the same element."""

    rule_id = "VUE-002"
    name = "v-if and v-for on same element"
    description = "Avoid using v-if and v-for on the same element. Use a wrapper element instead."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        template = extract_vue_template(file_context.content)
        if not template:
            return issues

        for i, line in enumerate(template.split("\n")):
            has_vfor = bool(re.search(r"v-for\s*=", line))
            has_vif = bool(re.search(r"v-if\s*=", line))
            if has_vfor and has_vif:
                file_line = file_context.content[: file_context.content.find(line)].count("\n") + 1
                issues.append(
                    self.create_issue(
                        "v-if and v-for on the same element. "
                        "This can cause performance issues due to priority conflicts.",
                        file_context,
                        file_line,
                        suggestion="Use a <template v-for> wrapper or computed property to filter the list.",
                    )
                )
        return issues


class VueUnusedComponentImports(BaseRule):
    """VUE-003: Detect unused component imports in Vue files."""

    rule_id = "VUE-003"
    name = "Unused component imports"
    description = "Imported components that are not used in the template should be removed."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        template = extract_vue_template(file_context.content)
        if not script:
            return issues

        # Find component imports
        import_pattern = r"import\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"];?"
        for match in re.finditer(import_pattern, script):
            comp_name = match.group(1)
            # Check PascalCase and kebab-case usage in template
            kebab = re.sub(r"([A-Z])", r"-\1", comp_name).lower().lstrip("-")
            if comp_name not in template and kebab not in template:
                # Check if used in script (e.g., components: { ... })
                script_usage = len(re.findall(rf"\b{re.escape(comp_name)}\b", script))
                if script_usage <= 1:
                    line = script[: match.start()].count("\n") + 1
                    file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                    issues.append(
                        self.create_issue(
                            f"Imported component '{comp_name}' is not used in the template.",
                            file_context,
                            file_line,
                            suggestion=f"Remove the unused import of '{comp_name}'.",
                        )
                    )
        return issues


class VueMissingPropValidation(BaseRule):
    """VUE-004: Detect missing prop validation in Vue components."""

    rule_id = "VUE-004"
    name = "Missing prop validation"
    description = "Components should validate their props for better maintainability."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        if not script:
            return issues

        # Check if component uses props
        has_props = bool(re.search(r"\bprops\s*:", script))
        if not has_props:
            # Check if component receives props in template
            template = extract_vue_template(file_context.content)
            if not template:
                return issues
            # Check if this component has a name and is likely used with props
            has_define_props = bool(re.search(r"defineProps", script))
            if not has_define_props:
                # Check for setup function with props parameter
                has_setup_props = bool(re.search(r"setup\s*\(\s*props\s*\)", script))
                if not has_setup_props:
                    return issues

        # Check if props have validation (type, required, validator)
        if has_props:
            # Simple check: if props is just an array, it lacks validation
            props_array = re.search(r"props\s*:\s*\[([^\]]*)\]", script)
            if props_array:
                line = script[: props_array.start()].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                issues.append(
                    self.create_issue(
                        "Props defined as an array without type validation. "
                        "Use object syntax with type definitions.",
                        file_context,
                        file_line,
                        suggestion="Define props as an object with type, required, and default.",
                    )
                )
        return issues


class VueDirectMutationOfProps(BaseRule):
    """VUE-005: Detect direct mutation of props."""

    rule_id = "VUE-005"
    name = "Direct mutation of props"
    description = "Props should not be mutated directly. Use events or computed properties instead."
    severity = Severity.ERROR
    category = Category.CORRECTNESS
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        if not script:
            return issues

        # Find prop names
        prop_names = set()
        props_match = re.search(r"props\s*:\s*\{([^}]+)\}", script, re.DOTALL)
        if props_match:
            for prop_match in re.finditer(r"(\w+)\s*:", props_match.group(1)):
                prop_names.add(prop_match.group(1))
        props_array = re.search(r"props\s*:\s*\[([^\]]*)\]", script)
        if props_array:
            for prop_match in re.finditer(r"['\"](\w+)['\"]", props_array.group(1)):
                prop_names.add(prop_match.group(1))

        if not prop_names:
            return issues

        # Check for prop mutation patterns
        for prop in prop_names:
            mutation_patterns = [
                rf"\b{re.escape(prop)}\s*=\s*[^=]",  # prop = value
                rf"\b{re.escape(prop)}\.\w+\s*=\s*",  # prop.property = value
                rf"\b{re.escape(prop)}\[\w+\]\s*=\s*",  # prop[index] = value
                rf"\b{re.escape(prop)}\.push\s*\(",  # prop.push()
                rf"\b{re.escape(prop)}\.pop\s*\(",  # prop.pop()
                rf"\b{re.escape(prop)}\.splice\s*\(",  # prop.splice()
            ]
            for pattern in mutation_patterns:
                for match in re.finditer(pattern, script):
                    line = script[: match.start()].count("\n") + 1
                    file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                    issues.append(
                        self.create_issue(
                            f"Direct mutation of prop '{prop}' detected. "
                            "Props should not be mutated directly.",
                            file_context,
                            file_line,
                            suggestion=f"Use emit('{prop}-update', newValue) or a computed property.",
                        )
                    )
                    break  # One report per prop
        return issues


class VueExcessiveRefs(BaseRule):
    """VUE-006: Detect excessive use of $refs."""

    rule_id = "VUE-006"
    name = "Using $refs excessively"
    description = "Excessive use of $refs indicates imperative DOM manipulation. Prefer declarative approaches."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        if not script:
            return issues

        ref_count = len(re.findall(r"\$refs\.\w+", script))
        if ref_count > 3:
            line = 1
            file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
            issues.append(
                self.create_issue(
                    f"Excessive use of $refs ({ref_count} occurrences). "
                    "Consider using declarative data binding and v-model instead.",
                    file_context,
                    file_line,
                    suggestion="Refactor to use Vue's reactive data binding and v-model.",
                )
            )
        return issues


class VueMissingErrorHandlingAsync(BaseRule):
    """VUE-007: Detect missing error handling in async methods."""

    rule_id = "VUE-007"
    name = "Missing error handling in async methods"
    description = "Async methods should have proper error handling with try/catch."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        if not script:
            return issues

        # Find async functions/methods
        async_pattern = r"async\s+(\w+)\s*\("
        for match in re.finditer(async_pattern, script):
            func_name = match.group(1)
            start = match.start()
            # Find the function body
            brace_start = script.find("{", start)
            if brace_start == -1:
                continue
            depth = 0
            end = brace_start
            for i in range(brace_start, min(brace_start + 2000, len(script))):
                if script[i] == "{":
                    depth += 1
                elif script[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break

            func_body = script[brace_start:end]
            # Check for try/catch
            has_try_catch = bool(re.search(r"\btry\s*\{", func_body))
            # Check for .catch()
            has_catch = bool(re.search(r"\.catch\s*\(", func_body))
            # Check for await
            has_await = bool(re.search(r"\bawait\s+", func_body))

            if has_await and not has_try_catch and not has_catch:
                line = script[: start].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
                issues.append(
                    self.create_issue(
                        f"Async method '{func_name}' uses await without error handling. "
                        "Wrap await calls in try/catch.",
                        file_context,
                        file_line,
                        suggestion=f"Wrap the await calls in '{func_name}' with try/catch.",
                    )
                )
        return issues


class VueConsoleStatements(BaseRule):
    """VUE-008: Detect console statements in Vue files."""

    rule_id = "VUE-008"
    name = "Console statements"
    description = "Console statements should be removed from production code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        console_methods = ["log", "warn", "error", "debug", "info", "trace", "dir"]
        for method in console_methods:
            pattern = rf"\bconsole\.{method}\s*\("
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"console.{method}() found. Remove console statements from production code.",
                        file_context,
                        line,
                        suggestion="Remove or replace with a proper logging solution.",
                    )
                )
        return issues


class VueDeepWatchers(BaseRule):
    """VUE-009: Detect deep watchers without necessity."""

    rule_id = "VUE-009"
    name = "Deep watchers without necessity"
    description = "Deep watchers have performance implications. Use them only when necessary."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        script = extract_vue_script(file_context.content)
        if not script:
            return issues

        # Find deep watchers
        deep_pattern = r"deep\s*:\s*true"
        for match in re.finditer(deep_pattern, script):
            line = script[: match.start()].count("\n") + 1
            file_line = file_context.content[: file_context.content.find(script)].count("\n") + line
            issues.append(
                self.create_issue(
                    "Deep watcher detected. Deep watchers can be expensive for large objects.",
                    file_context,
                    file_line,
                    suggestion="Consider watching a specific nested property instead of using deep: true.",
                )
            )
        return issues


class VueMissingKeyForTransitions(BaseRule):
    """VUE-010: Detect missing key for component transitions."""

    rule_id = "VUE-010"
    name = "Missing key for component transitions"
    description = "Components inside <Transition> should have keys for proper animation."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.VUE
    file_patterns = [r"\.vue$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        template = extract_vue_template(file_context.content)
        if not template:
            return issues

        # Find <Transition> or <transition> blocks
        transition_pattern = r"<(?:Transition|transition)[^>]*>"
        for match in re.finditer(transition_pattern, template):
            start = match.end()
            # Find the content inside transition
            end_tag = re.search(r"</(?:Transition|transition)>", template[start:])
            if not end_tag:
                continue
            inner = template[start : start + end_tag.start()]
            # Check if inner elements have :key
            if not re.search(r":key\s*=", inner) and not re.search(r"v-bind:key\s*=", inner):
                line = template[: match.start()].count("\n") + 1
                file_line = file_context.content[: file_context.content.find(template)].count("\n") + line
                issues.append(
                    self.create_issue(
                        "Component inside <Transition> without :key. "
                        "Keys are needed for proper transition behavior.",
                        file_context,
                        file_line,
                        suggestion="Add :key to the component inside <Transition>.",
                    )
                )
        return issues


# List of all Vue rules
VUE_RULES = [
    VueMissingKeyInVFor(),
    VueVIfAndVForOnSameElement(),
    VueUnusedComponentImports(),
    VueMissingPropValidation(),
    VueDirectMutationOfProps(),
    VueExcessiveRefs(),
    VueMissingErrorHandlingAsync(),
    VueConsoleStatements(),
    VueDeepWatchers(),
    VueMissingKeyForTransitions(),
]
