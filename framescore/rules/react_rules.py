"""React-specific analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)


class ReactMissingKeyProp(BaseRule):
    """REACT-001: Detect missing key prop in list rendering."""

    rule_id = "REACT-001"
    name = "Missing key prop in list rendering"
    description = "Elements in a list should have a unique 'key' prop for proper reconciliation."
    severity = Severity.ERROR
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content
        lines = file_context.lines

        # Pattern: .map( with JSX return but no key prop
        # Match patterns like: items.map((item) => <Component ...>) or <div ...>
        map_pattern = r"\.map\s*\(\s*(?:\([^)]*\)|\w+)\s*=>\s*"
        for match in re.finditer(map_pattern, content):
            start = match.end()
            # Find the JSX element after =>
            # Look for opening tag
            jsx_match = re.match(r"\s*<([A-Za-z][\w]*)", content[start:])
            if jsx_match:
                tag_content_start = start + jsx_match.start()
                # Find the end of the opening tag
                tag_end = content.find(">", tag_content_start)
                if tag_end != -1 and tag_end - tag_content_start < 500:
                    opening_tag = content[tag_content_start:tag_end]
                    if "key=" not in opening_tag:
                        line = content[:tag_content_start].count("\n") + 1
                        issues.append(
                            self.create_issue(
                                "List rendering without 'key' prop. "
                                "Add a unique 'key' prop to list items for proper React reconciliation.",
                                file_context,
                                line,
                                suggestion="Add key={item.id} or a unique identifier to the list element.",
                            )
                        )
        return issues


class ReactUseEffectMissingDeps(BaseRule):
    """REACT-002: Detect useEffect without dependency array."""

    rule_id = "REACT-002"
    name = "useEffect missing dependency array"
    description = "useEffect should have a dependency array to control when it runs."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Match useEffect(() => { without closing bracket for deps
            if re.search(r"\buseEffect\s*\(", line):
                # Look ahead for the dependency array pattern
                # Collect lines until we find the closing of useEffect
                block = line
                depth = 0
                found_arrow = False
                for j in range(i, min(i + 50, len(lines))):
                    block = lines[j] if j > i else block
                    if "=>" in lines[j]:
                        found_arrow = True
                    depth += lines[j].count("(") - lines[j].count(")")
                    if depth <= 0 and j > i:
                        break
                    # Check if there's no dependency array (no second argument)
                    if j > i and re.search(r"\)\s*;", lines[j]):
                        # Check if the closing has a dep array before it
                        check_content = "\n".join(lines[i : j + 1])
                        # Remove the callback function content
                        # Simple heuristic: if we see ) followed by , or )] or )), it has deps
                        # If we see )); it might not have deps
                        if re.search(r"\)\s*;\s*$", check_content.strip()):
                            issues.append(
                                self.create_issue(
                                    "useEffect without dependency array. "
                                    "This effect runs on every render.",
                                    file_context,
                                    i + 1,
                                    suggestion="Add a dependency array: useEffect(() => {...}, [deps])",
                                )
                            )
                        break
        return issues


class ReactDirectDOMManipulation(BaseRule):
    """REACT-003: Detect direct DOM manipulation in React components."""

    rule_id = "REACT-003"
    name = "Direct DOM manipulation"
    description = "Avoid direct DOM manipulation in React. Use refs and state instead."
    severity = Severity.WARNING
    category = Category.BEST_PRACTICE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        dom_apis = [
            (r"\bdocument\.getElementById\s*\(", "document.getElementById"),
            (r"\bdocument\.querySelector\s*\(", "document.querySelector"),
            (r"\bdocument\.querySelectorAll\s*\(", "document.querySelectorAll"),
            (r"\bdocument\.getElementsBy", "document.getElementsBy*"),
            (r"\bdocument\.createElement\s*\(", "document.createElement"),
            (r"\bdocument\.addEventListener\s*\(", "document.addEventListener"),
            (r"\bwindow\.addEventListener\s*\(", "window.addEventListener"),
            (r"\.innerHTML\s*=", ".innerHTML assignment"),
            (r"\.outerHTML\s*=", ".outerHTML assignment"),
            (r"\.appendChild\s*\(", ".appendChild"),
            (r"\.removeChild\s*\(", ".removeChild"),
        ]
        for pattern, name in dom_apis:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Direct DOM manipulation detected: {name}. "
                        "Use React state and refs instead.",
                        file_context,
                        line,
                        suggestion="Use React refs (useRef) or state to manipulate the DOM.",
                    )
                )
        return issues


class ReactMissingErrorBoundary(BaseRule):
    """REACT-004: Detect components without error boundaries."""

    rule_id = "REACT-004"
    name = "Missing error boundary"
    description = "Components should be wrapped in error boundaries to catch rendering errors."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check if file defines a component (function returning JSX)
        has_component = bool(re.search(
            r"(?:function|const)\s+\w+\s*(?:=\s*)?\([^)]*\)\s*(?::\s*\w+\s*)?(?:=>\s*)?\{",
            content,
        ))
        if not has_component:
            return issues

        # Check if file has JSX return
        has_jsx = bool(re.search(r"return\s*<", content))
        if not has_jsx:
            return issues

        # Check if there's an ErrorBoundary or error boundary pattern
        has_error_boundary = bool(
            re.search(
                r"(?:ErrorBoundary|componentDidCatch|getDerivedStateFromError)",
                content,
            )
        )
        if has_error_boundary:
            return issues

        # Check if this is a page/app level component (likely needs error boundary)
        is_page = bool(
            re.search(
                r"(?:App|Page|Layout|Root)\b",
                content,
            )
        )
        if is_page:
            issues.append(
                self.create_issue(
                    "Top-level component detected without error boundary. "
                    "Consider wrapping children with an ErrorBoundary component.",
                    file_context,
                    1,
                    suggestion="Create an ErrorBoundary class component and wrap your app.",
                )
            )
        return issues


class ReactIndexAsKey(BaseRule):
    """REACT-005: Detect using array index as key for dynamic lists."""

    rule_id = "REACT-005"
    name = "Using index as key for dynamic lists"
    description = "Using array index as key for dynamic lists can cause rendering issues."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        # Pattern: key={index} or key={i} inside .map(
        pattern = r"\.map\s*\([^)]*index\b[^)]*\)[^}]*?key\s*=\s*\{index\b"
        for match, line in self.find_pattern(file_context.content, pattern, re.DOTALL):
            issues.append(
                self.create_issue(
                    "Using array index as key for dynamic lists. "
                    "This can cause incorrect UI behavior when items are reordered.",
                    file_context,
                    line,
                    suggestion="Use a unique identifier from the data as key instead.",
                )
            )

        # Simpler pattern: key={i}
        pattern2 = r"key\s*=\s*\{\s*(?:i|idx|index)\s*\}"
        for match, line in self.find_pattern(file_context.content, pattern2):
            # Check if it's inside a .map call
            start = max(0, match.start() - 500)
            context_before = file_context.content[start : match.start()]
            if ".map(" in context_before:
                issues.append(
                    self.create_issue(
                        "Using index variable as key in list rendering. "
                        "Use a stable unique identifier instead.",
                        file_context,
                        line,
                        suggestion="Use item.id or another unique property as the key.",
                    )
                )
        return issues


class ReactUseStateObjectUpdate(BaseRule):
    """REACT-006: Detect useState with object without proper update pattern."""

    rule_id = "REACT-006"
    name = "useState object without proper update"
    description = "When using useState with objects, use the functional update form."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content
        lines = file_context.lines

        # Find useState with object initial value
        state_pattern = r"useState\s*\(\s*\{"
        for match in re.finditer(state_pattern, content):
            # Get the state variable name
            before = content[: match.start()]
            var_match = re.search(r"(?:const|let)\s+\[\s*(\w+)", before)
            if not var_match:
                continue
            state_var = var_match.group(1)
            setter = f"set{state_var[0].upper()}{state_var[1:]}" if state_var else "setState"

            # Look for direct assignment patterns like setX({...x, ...})
            # These are actually fine, so we look for setX(someObject) without spread
            direct_set_pattern = rf"{setter}\s*\(\s*(?!\.\.\.)\w+\s*\)"
            for dmatch, dline in self.find_pattern(content, direct_set_pattern):
                issues.append(
                    self.create_issue(
                        f"Direct state update for object state '{state_var}'. "
                        "Use functional update or spread operator to avoid stale state.",
                        file_context,
                        dline,
                        suggestion=f"Use {setter}(prev => ({{...prev, ...updates}})) instead.",
                    )
                )
        return issues


class ReactUseEffectMissingCleanup(BaseRule):
    """REACT-007: Detect useEffect without cleanup for side effects."""

    rule_id = "REACT-007"
    name = "useEffect missing cleanup"
    description = "useEffect with subscriptions or timers should return a cleanup function."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find useEffect blocks
        effect_pattern = r"useEffect\s*\(\s*\(\s*\)\s*=>\s*\{"
        for match in re.finditer(effect_pattern, content):
            start = match.start()
            # Find the matching closing brace
            depth = 0
            end = start
            for i in range(start, min(start + 2000, len(content))):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break

            block = content[start:end]
            # Check for side effects that need cleanup
            needs_cleanup = False
            cleanup_patterns = [
                r"\baddEventListener\s*\(",
                r"\bsetInterval\s*\(",
                r"\bsetTimeout\s*\(",
                r"\bnew\s+WebSocket\s*\(",
                r"\.subscribe\s*\(",
                r"\bwindow\.\w+\s*=\s*",
            ]
            for cp in cleanup_patterns:
                if re.search(cp, block):
                    needs_cleanup = True
                    break

            if needs_cleanup:
                # Check if there's a return cleanup function
                has_cleanup = bool(re.search(r"return\s+(?:function|\([^)]*\)\s*=>)", block))
                if not has_cleanup:
                    line = content[:start].count("\n") + 1
                    issues.append(
                        self.create_issue(
                            "useEffect with side effects (event listeners, timers, subscriptions) "
                            "missing cleanup function. This can cause memory leaks.",
                            file_context,
                            line,
                            suggestion="Return a cleanup function: useEffect(() => { ...; return () => cleanup(); }, [])",
                        )
                    )
        return issues


class ReactInlineFunctionInProps(BaseRule):
    """REACT-008: Detect inline functions in JSX props."""

    rule_id = "REACT-008"
    name = "Inline function in JSX props"
    description = "Inline functions in JSX props create new references on every render."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Match inline arrow functions in JSX props
            # Pattern: propName={() => ...} or propName={(e) => ...}
            inline_patterns = [
                r"\w+\s*=\s*\{\s*\([^)]*\)\s*=>\s*\{",
                r"\w+\s*=\s*\{\s*\([^)]*\)\s*=>\s*[^{]",
                r"\w+\s*=\s*\{\s*\(\)\s*=>\s*\{",
                r"\w+\s*=\s*\{\s*\(\)\s*=>\s*[^{]",
                r"onClick\s*=\s*\{\s*\(\)\s*=>",
                "onChange\\s*=\\s*\\{\\s*\\(\\)\\s*=>",
            ]
            for pattern in inline_patterns:
                if re.search(pattern, line):
                    # Exclude event handlers that are simple one-liners (acceptable)
                    if re.search(r"=>\s*\w+\.\w+\([^)]*\)\s*\}", line):
                        continue
                    issues.append(
                        self.create_issue(
                            "Inline function in JSX prop detected. "
                            "This creates a new function reference on every render.",
                            file_context,
                            i + 1,
                            suggestion="Use useCallback or define the function outside the JSX.",
                        )
                    )
                    break  # Only report once per line
        return issues


class ReactAnyTypeUsage(BaseRule):
    """REACT-009: Detect 'any' type usage in TypeScript React."""

    rule_id = "REACT-009"
    name = "Using 'any' type in TypeScript React"
    description = "Avoid using 'any' type. Use specific types for better type safety."
    severity = Severity.WARNING
    category = Category.CORRECTNESS
    framework = Framework.REACT
    file_patterns = [r"\.(tsx|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        # Match : any, as any, <any>
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
                        "Use specific types for better type safety and IDE support.",
                        file_context,
                        line,
                        suggestion="Replace 'any' with the appropriate type or 'unknown'.",
                    )
                )
        return issues


class ReactMissingPropTypes(BaseRule):
    """REACT-010: Detect components missing PropTypes or TypeScript types."""

    rule_id = "REACT-010"
    name = "Missing PropTypes or TypeScript types"
    description = "Components should have PropTypes or TypeScript interface definitions."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|js)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Skip if already has PropTypes
        if re.search(r"\bPropTypes\b", content):
            return issues

        # Check if file defines a component with props
        has_props = bool(re.search(
            r"(?:function|const)\s+\w+\s*\(\s*\{[^}]*\}\s*(?::\s*\w+)?\s*\)",
            content,
        ))
        if not has_props:
            has_props = bool(re.search(
                r"(?:function|const)\s+\w+\s*\(\s*\w+\s*(?::\s*\w+)?\s*\)",
                content,
            ))

        if has_props:
            has_jsx = bool(re.search(r"return\s*<", content))
            if has_jsx:
                issues.append(
                    self.create_issue(
                        "Component with props detected but no PropTypes defined. "
                        "Add PropTypes for runtime type checking.",
                        file_context,
                        1,
                        suggestion="Import PropTypes and define ComponentName.propTypes = { ... }",
                    )
                )
        return issues


class ReactUnnecessaryRerenders(BaseRule):
    """REACT-011: Detect patterns that cause unnecessary re-renders."""

    rule_id = "REACT-011"
    name = "Unnecessary re-renders (object/array props)"
    description = "Inline object/array creation in JSX causes child re-renders."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            # Match inline object literals in JSX props: prop={{ ... }}
            if re.search(r"\w+\s*=\s*\{\s*\{", line):
                issues.append(
                    self.create_issue(
                        "Inline object literal in JSX prop. "
                        "This creates a new object reference on every render, causing child re-renders.",
                        file_context,
                        i + 1,
                        suggestion="Use useMemo or define the object outside the render.",
                    )
                )
            # Match inline array literals in JSX props: prop={[ ... ]}
            if re.search(r"\w+\s*=\s*\{\s*\[", line):
                issues.append(
                    self.create_issue(
                        "Inline array literal in JSX prop. "
                        "This creates a new array reference on every render.",
                        file_context,
                        i + 1,
                        suggestion="Use useMemo or define the array outside the render.",
                    )
                )
        return issues


class ReactDangerouslySetInnerHTML(BaseRule):
    """REACT-012: Detect dangerouslySetInnerHTML usage."""

    rule_id = "REACT-012"
    name = "dangerouslySetInnerHTML usage"
    description = "dangerouslySetInnerHTML can expose the app to XSS attacks."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        for match, line in self.find_pattern(
            file_context.content, r"dangerouslySetInnerHTML"
        ):
            issues.append(
                self.create_issue(
                    "dangerouslySetInnerHTML detected. This can expose the app to XSS attacks. "
                    "Ensure the content is properly sanitized.",
                    file_context,
                    line,
                    suggestion="Use a sanitization library like DOMPurify before passing content.",
                )
            )
        return issues


class ReactMissingAltOnImg(BaseRule):
    """REACT-013: Detect img tags missing alt prop."""

    rule_id = "REACT-013"
    name = "Missing alt prop on img tags"
    description = "img tags should have an alt prop for accessibility."
    severity = Severity.WARNING
    category = Category.ACCESSIBILITY
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        # Match <img tags without alt prop
        pattern = r"<img\b(?![^>]*\balt\s*=)"
        for match, line in self.find_pattern(file_context.content, pattern):
            # Make sure it's not a self-closing tag that wraps
            tag_end = file_context.content.find(">", match.start())
            if tag_end != -1:
                tag = file_context.content[match.start() : tag_end]
                if "alt=" not in tag:
                    issues.append(
                        self.create_issue(
                            "img element missing 'alt' prop. "
                            "This is important for screen readers and accessibility.",
                            file_context,
                            line,
                            suggestion='Add alt="description" to the img element.',
                        )
                    )
        return issues


class ReactUnusedImports(BaseRule):
    """REACT-014: Detect unused imports in React files."""

    rule_id = "REACT-014"
    name = "Unused imports"
    description = "Unused imports increase bundle size and reduce code clarity."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content
        lines = file_context.lines

        # Find all imports
        import_pattern = r"^import\s+(?:(?:\{([^}]+)\})|(\w+))\s+from\s+['\"]([^'\"]+)['\"];?"
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            line = content[: match.start()].count("\n") + 1
            named_imports = match.group(1)
            default_import = match.group(2)

            # Check named imports
            if named_imports:
                for imp in named_imports.split(","):
                    imp_name = imp.strip().split(" as ")[0].strip()
                    if not imp_name or imp_name == "type":
                        continue
                    # Count usages (excluding the import line itself)
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

            # Check default import
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


class ReactConsoleStatements(BaseRule):
    """REACT-015: Detect console statements in production code."""

    rule_id = "REACT-015"
    name = "Console statements in production code"
    description = "Console statements should be removed from production code."
    severity = Severity.INFO
    category = Category.BEST_PRACTICE
    framework = Framework.REACT
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        console_methods = ["log", "warn", "error", "debug", "info", "trace", "dir", "table"]
        for method in console_methods:
            pattern = rf"\bconsole\.{method}\s*\("
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"console.{method}() found in source code. "
                        "Remove console statements before production deployment.",
                        file_context,
                        line,
                        suggestion="Remove or replace with a proper logging library.",
                    )
                )
        return issues


# List of all React rules
REACT_RULES = [
    ReactMissingKeyProp(),
    ReactUseEffectMissingDeps(),
    ReactDirectDOMManipulation(),
    ReactMissingErrorBoundary(),
    ReactIndexAsKey(),
    ReactUseStateObjectUpdate(),
    ReactUseEffectMissingCleanup(),
    ReactInlineFunctionInProps(),
    ReactAnyTypeUsage(),
    ReactMissingPropTypes(),
    ReactUnnecessaryRerenders(),
    ReactDangerouslySetInnerHTML(),
    ReactMissingAltOnImg(),
    ReactUnusedImports(),
    ReactConsoleStatements(),
]
