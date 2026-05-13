"""Performance-focused analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)


class PerformanceLargeBundleImports(BaseRule):
    """PERF-001: Detect importing entire libraries when only parts are needed."""

    rule_id = "PERF-001"
    name = "Large bundle imports"
    description = "Import only what you need from large libraries to reduce bundle size."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    # Libraries known to support tree-shaking / named imports
    large_libs = {
        "lodash": "lodash",
        "moment": "moment (consider using date-fns or dayjs)",
        "underscore": "underscore",
        "jquery": "jQuery",
        "d3": "d3",
        "three": "three.js",
        "firebase": "firebase",
        "aws-sdk": "AWS SDK",
    }

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check for default import of large libraries
        import_pattern = r"import\s+\w+\s+from\s+['\"]([^'\"]+)['\"];?"
        for match in re.finditer(import_pattern, content):
            lib_path = match.group(1)
            lib_name = lib_path.split("/")[0]
            if lib_name in self.large_libs:
                line = content[: match.start()].count("\n") + 1
                display = self.large_libs[lib_name]
                issues.append(
                    self.create_issue(
                        f"Default import of large library '{display}'. "
                        "Import specific functions to enable tree-shaking.",
                        file_context,
                        line,
                        suggestion=f"Use named imports: import {{ specificFn }} from '{lib_name}'",
                    )
                )
        return issues


class PerformanceMissingLazyLoading(BaseRule):
    """PERF-002: Detect routes that could benefit from lazy loading."""

    rule_id = "PERF-002"
    name = "Missing lazy loading for routes"
    description = "Use lazy loading for route components to reduce initial bundle size."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check for React Router route definitions without lazy loading
        # Pattern: <Route path="..." component={Component} /> or element={<Component />}
        route_pattern = r"<(?:Route|route)\s+[^>]*(?:component|element)\s*=\s*"
        lazy_pattern = r"(?:lazy|React\.lazy|import\()"

        for match in re.finditer(route_pattern, content):
            line = content[: match.start()].count("\n") + 1
            # Check if this route uses lazy loading
            context = content[max(0, match.start() - 200) : match.end() + 200]
            if not re.search(lazy_pattern, context):
                issues.append(
                    self.create_issue(
                        "Route component without lazy loading. "
                        "Use React.lazy() or dynamic import() for code splitting.",
                        file_context,
                        line,
                        suggestion="Use const LazyComponent = React.lazy(() => import('./Component'))",
                    )
                )
        return issues


class PerformanceUnoptimizedImages(BaseRule):
    """PERF-003: Detect images without width/height attributes."""

    rule_id = "PERF-003"
    name = "Unoptimized images (no width/height)"
    description = "Images should have explicit width and height to prevent layout shift."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(jsx|tsx|js|ts|vue|svelte|html)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Match img tags
        img_pattern = r"<img\b([^>]*)/?>"
        for match in re.finditer(img_pattern, content):
            attrs = match.group(1)
            has_width = bool(re.search(r"\bwidth\s*=", attrs))
            has_height = bool(re.search(r"\bheight\s*=", attrs))
            if not has_width or not has_height:
                line = content[: match.start()].count("\n") + 1
                missing = []
                if not has_width:
                    missing.append("width")
                if not has_height:
                    missing.append("height")
                issues.append(
                    self.create_issue(
                        f"Image missing {' and '.join(missing)} attribute(s). "
                        "This can cause Cumulative Layout Shift (CLS).",
                        file_context,
                        line,
                        suggestion=f"Add {' and '.join(missing)} attributes to the image element.",
                    )
                )
        return issues


class PerformanceSynchronousFileOps(BaseRule):
    """PERF-004: Detect synchronous file system operations."""

    rule_id = "PERF-004"
    name = "Synchronous file operations"
    description = "Synchronous file operations block the event loop. Use async versions instead."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        sync_patterns = [
            (r"\breadFileSync\s*\(", "readFileSync"),
            (r"\bwriteFileSync\s*\(", "writeFileSync"),
            (r"\bexistsSync\s*\(", "existsSync"),
            (r"\breaddirSync\s*\(", "readdirSync"),
            (r"\bstatSync\s*\(", "statSync"),
            (r"\bunlinkSync\s*\(", "unlinkSync"),
            (r"\bmkdirSync\s*\(", "mkdirSync"),
            (r"\brmdirSync\s*\(", "rmdirSync"),
            (r"\bcopyFileSync\s*\(", "copyFileSync"),
        ]
        for pattern, name in sync_patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Synchronous file operation '{name}' detected. "
                        "This blocks the event loop and hurts performance.",
                        file_context,
                        line,
                        suggestion=f"Use the async version: {name.replace('Sync', '')} with await/promises.",
                    )
                )
        return issues


class PerformanceUnnecessaryRerenders(BaseRule):
    """PERF-005: Detect patterns that cause unnecessary re-renders."""

    rule_id = "PERF-005"
    name = "Unnecessary re-renders patterns"
    description = "Certain patterns in React cause unnecessary re-renders."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Detect creating new objects/arrays in render body
        # Pattern: const obj = { ... } inside a component function
        lines = content.split("\n")
        in_component = False
        component_brace_depth = 0

        for i, line in enumerate(lines):
            # Track if we're inside a component function
            if re.match(r"^(?:export\s+)?(?:default\s+)?(?:function|const)\s+\w+", line):
                in_component = True
                component_brace_depth = 0

            if in_component:
                component_brace_depth += line.count("{") - line.count("}")
                if component_brace_depth <= 0:
                    in_component = False

                # Check for object/array creation that could be memoized
                if component_brace_depth > 0:
                    if re.match(r"^\s+const\s+\w+\s*=\s*\{", line):
                        # Check if it's a style object or config
                        if re.search(r"(?:style|config|options|props)", line):
                            issues.append(
                                self.create_issue(
                                    "Object created in component render body. "
                                    "This creates a new reference on every render.",
                                    file_context,
                                    i + 1,
                                    suggestion="Use useMemo to memoize the object.",
                                )
                            )
        return issues


class PerformanceMissingDebounceThrottle(BaseRule):
    """PERF-006: Detect event handlers missing debounce/throttle."""

    rule_id = "PERF-006"
    name = "Missing debounce/throttle on events"
    description = "High-frequency event handlers should use debounce or throttle."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check for high-frequency events without debounce/throttle
        high_freq_events = [
            r"(?:on(?:Input|Change|KeyDown|KeyUp|KeyPress|MouseMove|Scroll|Resize|Wheel))\s*[=:]\s*",
        ]
        debounce_pattern = r"(?:debounce|throttle|_.debounce|_.throttle|lodash\.debounce)"

        for event_pattern in high_freq_events:
            for match in re.finditer(event_pattern, content):
                line = content[: match.start()].count("\n") + 1
                # Check context for debounce/throttle
                context = content[max(0, match.start() - 200) : match.end() + 200]
                if not re.search(debounce_pattern, context):
                    issues.append(
                        self.create_issue(
                            "High-frequency event handler without debounce/throttle. "
                            "This can cause performance issues.",
                            file_context,
                            line,
                            suggestion="Wrap the handler with debounce or throttle.",
                        )
                    )
        return issues


class PerformanceLargeStateObjects(BaseRule):
    """PERF-007: Detect large state objects."""

    rule_id = "PERF-007"
    name = "Large state objects"
    description = "Large state objects can cause performance issues. Consider splitting state."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find useState with large initial objects
        state_pattern = r"useState\s*\(\s*\{"
        for match in re.finditer(state_pattern, content):
            start = match.end()
            # Find the matching closing brace
            depth = 1
            end = start
            for i in range(start, min(start + 2000, len(content))):
                if content[i] == "{":
                    depth += 1
                elif content[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break

            obj_content = content[start:end]
            # Count properties
            prop_count = len(re.findall(r"\w+\s*:", obj_content))
            if prop_count > 10:
                line = content[: match.start()].count("\n") + 1
                issues.append(
                    self.create_issue(
                        f"Large state object with {prop_count} properties. "
                        "Consider splitting into multiple state variables or useReducer.",
                        file_context,
                        line,
                        suggestion="Split the state into smaller pieces or use useReducer.",
                    )
                )
        return issues


class PerformanceUnoptimizedLoops(BaseRule):
    """PERF-008: Detect unoptimized nested loops."""

    rule_id = "PERF-008"
    name = "Unoptimized loops (nested forEach/map)"
    description = "Deeply nested loops can cause performance issues. Consider optimization."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        lines = file_context.lines

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Count nesting of loops/map/forEach
            if re.search(r"\.(?:map|forEach|filter|reduce|some|every|find)\s*\(", stripped):
                indent = len(line) - len(stripped)
                level = indent // 2
                if level >= 3:
                    issues.append(
                        self.create_issue(
                            f"Deeply nested loop/map at level {level}. "
                            "This may cause O(n^2) or worse time complexity.",
                            file_context,
                            i + 1,
                            suggestion="Consider using Map/Set for lookups or restructuring the algorithm.",
                        )
                    )
        return issues


class PerformanceMemoryLeakPatterns(BaseRule):
    """PERF-009: Detect potential memory leak patterns."""

    rule_id = "PERF-009"
    name = "Memory leak patterns (event listeners not cleaned)"
    description = "Event listeners and intervals not cleaned up can cause memory leaks."
    severity = Severity.WARNING
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Find addEventListener without matching removeEventListener
        add_pattern = r"\.addEventListener\s*\(\s*['\"](\w+)['\"]"
        remove_pattern = r"\.removeEventListener\s*\(\s*['\"](\w+)['\"]"

        added_events = []
        for match in re.finditer(add_pattern, content):
            event_name = match.group(1)
            line = content[: match.start()].count("\n") + 1
            added_events.append((event_name, line))

        removed_events = set()
        for match in re.finditer(remove_pattern, content):
            event_name = match.group(1)
            removed_events.add(event_name)

        for event_name, line in added_events:
            if event_name not in removed_events:
                issues.append(
                    self.create_issue(
                        f"addEventListener('{event_name}') without matching removeEventListener. "
                        "This can cause memory leaks.",
                        file_context,
                        line,
                        suggestion=f"Add removeEventListener('{event_name}') in cleanup/unmount.",
                    )
                )

        # Check for setInterval without clearInterval
        set_interval = len(re.findall(r"\bsetInterval\s*\(", content))
        clear_interval = len(re.findall(r"\bclearInterval\s*\(", content))
        if set_interval > clear_interval:
            for match in re.finditer(r"\bsetInterval\s*\(", content):
                line = content[: match.start()].count("\n") + 1
                issues.append(
                    self.create_issue(
                        "setInterval without matching clearInterval. "
                        "This can cause memory leaks.",
                        file_context,
                        line,
                        suggestion="Store the interval ID and call clearInterval in cleanup.",
                    )
                )
                break  # One report per file

        return issues


class PerformanceMissingVirtualization(BaseRule):
    """PERF-010: Detect large list rendering without virtualization."""

    rule_id = "PERF-010"
    name = "Missing virtualization for large lists"
    description = "Rendering large lists without virtualization can cause performance issues."
    severity = Severity.INFO
    category = Category.PERFORMANCE
    framework = Framework.GENERAL
    file_patterns = [r"\.(jsx|tsx|js|ts)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check for .map() rendering lists
        map_pattern = r"\.map\s*\("
        map_count = len(re.findall(map_pattern, content))
        if map_count < 1:
            return issues

        # Check for virtualization libraries
        virtual_libs = [
            r"(?:react-window|react-virtualized|react-virtual|VirtualList|virtualize)",
            r"(?:RecycleScroller|VirtualScroller)",
        ]
        has_virtual = any(re.search(lib, content) for lib in virtual_libs)

        if not has_virtual:
            # Check if the list might be large (heuristic: data from API or large array)
            large_data_patterns = [
                r"(?:fetchAll|getAll|getItems|loadAll|fetchList|loadMore)",
                r"(?:\.length\s*>\s*\d{3})",
                r"(?:pagination|pageSize|limit\s*[:=]\s*\d{3})",
            ]
            has_large_data = any(re.search(p, content) for p in large_data_patterns)

            if has_large_data:
                for match in re.finditer(map_pattern, content):
                    line = content[: match.start()].count("\n") + 1
                    issues.append(
                        self.create_issue(
                            "List rendering without virtualization detected. "
                            "Large lists should use virtualization for performance.",
                            file_context,
                            line,
                            suggestion="Use react-window, react-virtualized, or similar for large lists.",
                        )
                    )
                    break  # One report per file
        return issues


# List of all performance rules
PERFORMANCE_RULES = [
    PerformanceLargeBundleImports(),
    PerformanceMissingLazyLoading(),
    PerformanceUnoptimizedImages(),
    PerformanceSynchronousFileOps(),
    PerformanceUnnecessaryRerenders(),
    PerformanceMissingDebounceThrottle(),
    PerformanceLargeStateObjects(),
    PerformanceUnoptimizedLoops(),
    PerformanceMemoryLeakPatterns(),
    PerformanceMissingVirtualization(),
]
