"""Shared utilities for FrameScore."""

import os
import re
import sys
import time


# ANSI color codes for terminal output (no external dependencies)
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    @staticmethod
    def supports_color():
        """Check if the terminal supports color output."""
        if os.environ.get("NO_COLOR"):
            return False
        if os.environ.get("TERM") == "dumb":
            return False
        if sys.platform == "win32":
            return os.environ.get("ANSICON") is not None or "256color" in os.environ.get("TERM", "")
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @classmethod
    def wrap(cls, text, color):
        """Wrap text with ANSI color codes."""
        if not cls.supports_color():
            return text
        return f"{color}{text}{cls.RESET}"

    @classmethod
    def red(cls, text):
        return cls.wrap(text, cls.RED)

    @classmethod
    def green(cls, text):
        return cls.wrap(text, cls.GREEN)

    @classmethod
    def yellow(cls, text):
        return cls.wrap(text, cls.YELLOW)

    @classmethod
    def blue(cls, text):
        return cls.wrap(text, cls.BLUE)

    @classmethod
    def cyan(cls, text):
        return cls.wrap(text, cls.CYAN)

    @classmethod
    def magenta(cls, text):
        return cls.wrap(text, cls.MAGENTA)

    @classmethod
    def bold(cls, text):
        return cls.wrap(text, cls.BOLD)

    @classmethod
    def dim(cls, text):
        return cls.wrap(text, cls.DIM)

    @classmethod
    def gray(cls, text):
        return cls.wrap(text, cls.GRAY)


class ProgressBar:
    """A simple progress bar for terminal output."""

    def __init__(self, total, prefix="", width=40):
        """Initialize progress bar.

        Args:
            total: Total number of items.
            prefix: Prefix text to display.
            width: Width of the progress bar in characters.
        """
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0
        self.start_time = time.time()
        self._last_update = 0

    def update(self, current=None):
        """Update the progress bar.

        Args:
            current: Current progress value. If None, increments by 1.
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1

        now = time.time()
        if now - self._last_update < 0.1 and self.current < self.total:
            return
        self._last_update = now

        if self.total == 0:
            return

        progress = self.current / self.total
        filled = int(self.width * progress)
        bar = "█" * filled + "░" * (self.width - filled)
        percent = progress * 100

        elapsed = now - self.start_time
        if self.current > 0:
            eta = elapsed / self.current * (self.total - self.current)
            eta_str = f"ETA {eta:.1f}s"
        else:
            eta_str = ""

        sys.stdout.write(
            f"\r{Colors.cyan(self.prefix)} "
            f"{Colors.green(f'[{bar}]')} "
            f"{Colors.bold(f'{percent:.0f}%')} "
            f"({self.current}/{self.total}) "
            f"{Colors.dim(eta_str)}"
        )
        sys.stdout.flush()

        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def finish(self):
        """Finish the progress bar."""
        self.update(self.total)


def read_file(file_path):
    """Read file contents safely.

    Args:
        file_path: Path to the file.

    Returns:
        File contents as string, or empty string if file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (IOError, OSError):
        return ""


def read_file_lines(file_path):
    """Read file contents as list of lines.

    Args:
        file_path: Path to the file.

    Returns:
        List of lines, or empty list if file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except (IOError, OSError):
        return []


def count_lines(content):
    """Count the number of lines in content.

    Args:
        content: String content.

    Returns:
        Number of lines.
    """
    if not content:
        return 0
    return content.count("\n") + (1 if not content.endswith("\n") else 0)


def extract_imports(content):
    """Extract import statements from source code.

    Args:
        content: Source code content.

    Returns:
        List of import strings.
    """
    imports = []
    # Match ES6 imports
    pattern = r"^import\s+.*?['\"](.+?)['\"];?\s*$"
    imports.extend(re.findall(pattern, content, re.MULTILINE))
    # Match require statements
    pattern = r"(?:const|let|var)\s+\w+\s*=\s*require\(['\"](.+?)['\"]\)"
    imports.extend(re.findall(pattern, content))
    return imports


def extract_exports(content):
    """Extract export statements from source code.

    Args:
        content: Source code content.

    Returns:
        List of export names.
    """
    exports = []
    # Match named exports
    pattern = r"export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)"
    exports.extend(re.findall(pattern, content))
    # Match export { ... }
    pattern = r"export\s+\{([^}]+)\}"
    for match in re.findall(pattern, content):
        for name in match.split(","):
            name = name.strip().split(" as ")[0].strip()
            if name:
                exports.append(name)
    return exports


def extract_functions(content):
    """Extract function definitions from source code.

    Args:
        content: Source code content.

    Returns:
        List of tuples (function_name, start_line, end_line).
    """
    functions = []
    lines = content.split("\n")

    # Match function declarations and arrow functions
    for i, line in enumerate(lines):
        # Regular function
        match = re.match(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", line)
        if match:
            name = match.group(1)
            start = i + 1
            end = _find_function_end(lines, i)
            functions.append((name, start, end))
            continue

        # Arrow function assigned to const/let/var
        match = re.match(
            r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>",
            line,
        )
        if match:
            name = match.group(1)
            start = i + 1
            end = _find_function_end(lines, i)
            functions.append((name, start, end))
            continue

        # Method in object/class
        match = re.match(r"^\s+(?:async\s+)?(\w+)\s*\(", line)
        if match and not re.match(r"^\s+(if|for|while|switch|catch)\s*\(", line):
            name = match.group(1)
            start = i + 1
            end = _find_function_end(lines, i)
            functions.append((name, start, end))

    return functions


def _find_function_end(lines, start_idx):
    """Find the approximate end line of a function.

    Args:
        lines: List of source code lines.
        start_idx: Index of the function start line.

    Returns:
        1-based line number of the approximate end.
    """
    brace_count = 0
    found_open = False
    for i in range(start_idx, len(lines)):
        for char in lines[i]:
            if char == "{":
                brace_count += 1
                found_open = True
            elif char == "}":
                brace_count -= 1
                if found_open and brace_count <= 0:
                    return i + 1
    return len(lines)


def extract_jsx_elements(content):
    """Extract JSX element tags from React content.

    Args:
        content: Source code content.

    Returns:
        List of JSX tag names found.
    """
    # Match JSX opening tags (capitalized for components, lowercase for HTML)
    pattern = r"<([A-Z][a-zA-Z0-9]*)\b"
    components = re.findall(pattern, content)
    # Match HTML tags in JSX
    pattern = r"<([a-z][a-zA-Z0-9]*)\b"
    html_tags = re.findall(pattern, content)
    return list(set(components + html_tags))


def extract_vue_template(content):
    """Extract the template section from a Vue single-file component.

    Args:
        content: Vue SFC content.

    Returns:
        Template section as string, or empty string.
    """
    match = re.search(r"<template>(.*?)</template>", content, re.DOTALL)
    return match.group(1) if match else ""


def extract_vue_script(content):
    """Extract the script section from a Vue single-file component.

    Args:
        content: Vue SFC content.

    Returns:
        Script section as string, or empty string.
    """
    match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    return match.group(1) if match else ""


def extract_svelte_template(content):
    """Extract the template section from a Svelte component.

    Args:
        content: Svelte component content.

    Returns:
        Template section as string (everything before <script>).
    """
    match = re.search(r"<script[^>]*>", content)
    if match:
        return content[: match.start()]
    return content


def extract_svelte_script(content):
    """Extract the script section from a Svelte component.

    Args:
        content: Svelte component content.

    Returns:
        Script section as string, or empty string.
    """
    match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    return match.group(1) if match else ""


def find_matching_brace(content, start):
    """Find the position of the matching closing brace.

    Args:
        content: Source code content.
        start: Index of the opening brace.

    Returns:
        Index of the matching closing brace, or -1.
    """
    if start >= len(content) or content[start] != "{":
        return -1
    depth = 1
    in_string = None
    i = start + 1
    while i < len(content) and depth > 0:
        char = content[i]
        if in_string:
            if char == "\\" and i + 1 < len(content):
                i += 2
                continue
            if char == in_string:
                in_string = None
        else:
            if char in ('"', "'"):
                in_string = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
        i += 1
    return i - 1 if depth == 0 else -1


def get_line_number(content, position):
    """Get the 1-based line number for a character position.

    Args:
        content: Source code content.
        position: Character position in the content.

    Returns:
        1-based line number.
    """
    return content[:position].count("\n") + 1


def normalize_path(path):
    """Normalize a file path.

    Args:
        path: File path string.

    Returns:
        Normalized absolute path.
    """
    return os.path.normpath(os.path.abspath(path))


def is_valid_source_file(file_path, extensions=None):
    """Check if a file is a valid source file based on extension.

    Args:
        file_path: Path to the file.
        extensions: List of valid extensions. Defaults to common web extensions.

    Returns:
        True if the file has a valid source extension.
    """
    if extensions is None:
        extensions = {
            ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte",
            ".mjs", ".cjs", ".json",
        }
    _, ext = os.path.splitext(file_path)
    return ext.lower() in extensions


def severity_to_color(severity):
    """Get ANSI color for a severity level.

    Args:
        severity: Severity string ('error', 'warning', 'info').

    Returns:
        ANSI color code string.
    """
    colors = {
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.CYAN,
    }
    return colors.get(severity.lower(), Colors.WHITE)


def grade_to_color(grade):
    """Get ANSI color for a grade letter.

    Args:
        grade: Grade string (e.g., 'A+', 'B', 'F').

    Returns:
        ANSI color code string.
    """
    grade_colors = {
        "A+": Colors.GREEN,
        "A": Colors.GREEN,
        "B+": Colors.CYAN,
        "B": Colors.CYAN,
        "C+": Colors.YELLOW,
        "C": Colors.YELLOW,
        "D": Colors.RED,
        "F": Colors.BG_RED,
    }
    return grade_colors.get(grade, Colors.WHITE)


def format_duration(seconds):
    """Format a duration in seconds to a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string.
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"
