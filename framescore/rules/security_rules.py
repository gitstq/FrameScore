"""Security-focused analysis rules."""

import re

from .base import (
    BaseRule,
    Category,
    FileContext,
    Framework,
    Issue,
    Severity,
)


class SecurityEvalUsage(BaseRule):
    """SEC-001: Detect eval() usage."""

    rule_id = "SEC-001"
    name = "eval() usage"
    description = "eval() is dangerous and can execute arbitrary code. Avoid it."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte|html)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        for match, line in self.find_pattern(file_context.content, r"\beval\s*\("):
            issues.append(
                self.create_issue(
                    "eval() usage detected. This is a serious security risk "
                    "as it can execute arbitrary code.",
                    file_context,
                    line,
                    suggestion="Use JSON.parse() for JSON data or Function constructor as a safer alternative.",
                )
            )
        # Also check for new Function()
        for match, line in self.find_pattern(file_context.content, r"\bnew\s+Function\s*\("):
            issues.append(
                self.create_issue(
                    "new Function() usage detected. This is similar to eval() and can execute arbitrary code.",
                    file_context,
                    line,
                    suggestion="Avoid dynamic code generation. Use safer alternatives.",
                )
            )
        return issues


class SecurityInnerHTMLAssignment(BaseRule):
    """SEC-002: Detect innerHTML assignment."""

    rule_id = "SEC-002"
    name = "innerHTML assignment"
    description = "Direct innerHTML assignment can lead to XSS attacks."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte|html)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        for match, line in self.find_pattern(file_context.content, r"\.innerHTML\s*=\s*"):
            issues.append(
                self.create_issue(
                    "Direct innerHTML assignment detected. This can lead to XSS attacks "
                    "if the content is not properly sanitized.",
                    file_context,
                    line,
                    suggestion="Use textContent or sanitize the HTML before assignment.",
                )
            )
        return issues


class SecurityHardcodedSecrets(BaseRule):
    """SEC-003: Detect hardcoded secrets and API keys."""

    rule_id = "SEC-003"
    name = "Hardcoded secrets/API keys"
    description = "Hardcoded secrets and API keys should never be in source code."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r".*"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"(?i)(?:api[_-]?key|apikey)\s*[:=]\s*['\"]([^'\"]{10,})['\"]", "API key"),
            (r"(?i)(?:secret|password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]{6,})['\"]", "secret/password"),
            (r"(?i)(?:token|auth[_-]?token|access[_-]?token)\s*[:=]\s*['\"]([^'\"]{10,})['\"]", "authentication token"),
            (r"(?i)(?:private[_-]?key)\s*[:=]\s*['\"]([^'\"]{10,})['\"]", "private key"),
            (r"(?i)(?:aws[_-]?secret|aws[_-]?access)\s*[:=]\s*['\"]([^'\"]{10,})['\"]", "AWS credential"),
            (r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*", "Bearer token"),
            (r"(?i)(?:mysql|postgres|mongo|redis|amqp)\s*[:=]\s*['\"]([^'\"]{8,})['\"]", "database connection string"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                # Mask the actual secret value in the message
                issues.append(
                    self.create_issue(
                        f"Potential hardcoded {desc} detected. "
                        "Secrets should be stored in environment variables.",
                        file_context,
                        line,
                        suggestion="Move secrets to environment variables or a secrets manager.",
                    )
                )
        return issues


class SecurityHttpInsteadOfHttps(BaseRule):
    """SEC-004: Detect http:// URLs instead of https://."""

    rule_id = "SEC-004"
    name = "Using http:// instead of https://"
    description = "Use https:// for all external communications to ensure data encryption."
    severity = Severity.WARNING
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx|vue|svelte|html|json)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        # Skip localhost and development URLs
        skip_pattern = r"http://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|::1|\[::1\]|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)"
        for match, line in self.find_pattern(file_context.content, r"http://[^\s'\"\)]+"):
            url = match.group(0)
            if not re.match(skip_pattern, url):
                issues.append(
                    self.create_issue(
                        f"Insecure HTTP URL detected: {url[:50]}. Use HTTPS instead.",
                        file_context,
                        line,
                        suggestion="Replace http:// with https:// for secure communication.",
                    )
                )
        return issues


class SecuritySQLInjectionPatterns(BaseRule):
    """SEC-005: Detect potential SQL injection patterns."""

    rule_id = "SEC-005"
    name = "SQL injection patterns"
    description = "String concatenation in SQL queries can lead to SQL injection attacks."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        # Pattern: SQL query with string concatenation
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
        for keyword in sql_keywords:
            # Look for SQL keyword followed by string concatenation with variables
            pattern = r"(?i)(?:query|sql|execute)\s*\(\s*['\"][^'\"]*\{[^}]+\}"
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Potential SQL injection: string interpolation in SQL query. "
                        "Use parameterized queries instead.",
                        file_context,
                        line,
                        suggestion="Use parameterized queries or an ORM to prevent SQL injection.",
                    )
                )
                break  # One report per file for SQL injection
        return issues


class SecurityPathTraversalPatterns(BaseRule):
    """SEC-006: Detect potential path traversal patterns."""

    rule_id = "SEC-006"
    name = "Path traversal patterns"
    description = "User input in file paths can lead to path traversal attacks."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"(?:readFile|writeFile|unlink|mkdir|readdir|rmdir|stat)\s*\(\s*[^)]*\+[^)]*\)", "file system operation with concatenation"),
            (r"(?:readFile|writeFile|unlink|mkdir|readdir|rmdir|stat)\s*\(\s*[^)]*`\$\{", "file system operation with template literal"),
            (r"require\s*\(\s*[^)]*\+[^)]*\)", "dynamic require with concatenation"),
            (r"import\s*\(\s*[^)]*\+[^)]*\)", "dynamic import with concatenation"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Potential path traversal: {desc}. "
                        "Validate and sanitize file paths from user input.",
                        file_context,
                        line,
                        suggestion="Use path.resolve() and validate paths against an allowlist.",
                    )
                )
        return issues


class SecurityCommandInjectionPatterns(BaseRule):
    """SEC-007: Detect potential command injection patterns."""

    rule_id = "SEC-007"
    name = "Command injection patterns"
    description = "User input in shell commands can lead to command injection attacks."
    severity = Severity.ERROR
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"\bexec\s*\(\s*[^)]*\+[^)]*\)", "exec() with string concatenation"),
            (r"\bexec\s*\(\s*[^)]*`\$\{", "exec() with template literal"),
            (r"\bspawn\s*\(\s*['\"][^'\"]*['\"]\s*,\s*\[?[^]]*\+[^]]*\]?", "spawn() with concatenation"),
            (r"\bchild_process\b", "child_process module usage"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"Potential command injection: {desc}. "
                        "Never pass untrusted input to shell commands.",
                        file_context,
                        line,
                        suggestion="Use strict input validation and avoid shell execution with user input.",
                    )
                )
        return issues


class SecurityInsecureRandom(BaseRule):
    """SEC-008: Detect insecure random usage."""

    rule_id = "SEC-008"
    name = "Insecure random usage"
    description = "Math.random() is not cryptographically secure. Use crypto module for security purposes."
    severity = Severity.WARNING
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        content = file_context.content

        # Check for Math.random() in security-sensitive contexts
        security_contexts = [
            (r"(?:token|password|secret|key|session|nonce|salt|hash|auth)\w*\s*[:=]\s*[^;]*Math\.random\(\)", "security-sensitive context"),
        ]
        for pattern, desc in security_contexts:
            for match, line in self.find_pattern(content, pattern):
                issues.append(
                    self.create_issue(
                        f"Math.random() used in {desc}. "
                        "Use crypto.randomBytes() for cryptographic purposes.",
                        file_context,
                        line,
                        suggestion="Use require('crypto').randomBytes() for secure random generation.",
                    )
                )
        return issues


class SecurityCORSWildcard(BaseRule):
    """SEC-009: Detect CORS wildcard configuration."""

    rule_id = "SEC-009"
    name = "CORS wildcard configuration"
    description = "CORS wildcard (*) configuration can expose the API to any origin."
    severity = Severity.WARNING
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"(?i)Access-Control-Allow-Origin\s*[:=]\s*['\"]?\*['\"]?", "CORS Allow-Origin wildcard"),
            (r"(?i)cors\s*\(\s*\{[^}]*origin\s*[:=]\s*['\"]?\*['\"]?", "CORS origin wildcard"),
            (r"(?i)use\s*\(\s*cors\s*\(\s*\)\s*\)", "CORS middleware without configuration"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"{desc} detected. "
                        "Restrict CORS to specific trusted origins.",
                        file_context,
                        line,
                        suggestion="Configure CORS with specific allowed origins instead of '*'.",
                    )
                )
        return issues


class SecuritySensitiveDataInLocalStorage(BaseRule):
    """SEC-010: Detect sensitive data stored in localStorage."""

    rule_id = "SEC-010"
    name = "Sensitive data in localStorage"
    description = "Sensitive data should not be stored in localStorage as it's accessible via JavaScript."
    severity = Severity.WARNING
    category = Category.SECURITY
    framework = Framework.GENERAL
    file_patterns = [r"\.(js|jsx|ts|tsx)$"]

    def check(self, file_context: FileContext) -> list:
        issues = []
        patterns = [
            (r"localStorage\.(setItem|setItem)\s*\(\s*['\"](?:token|password|secret|key|auth|session|credential)", "sensitive data in localStorage"),
            (r"sessionStorage\.(setItem|setItem)\s*\(\s*['\"](?:token|password|secret|key|auth|session|credential)", "sensitive data in sessionStorage"),
        ]
        for pattern, desc in patterns:
            for match, line in self.find_pattern(file_context.content, pattern):
                issues.append(
                    self.create_issue(
                        f"{desc} detected. "
                        "localStorage is accessible via XSS attacks. Use httpOnly cookies instead.",
                        file_context,
                        line,
                        suggestion="Use httpOnly, secure cookies for storing sensitive authentication data.",
                    )
                )
        return issues


# List of all security rules
SECURITY_RULES = [
    SecurityEvalUsage(),
    SecurityInnerHTMLAssignment(),
    SecurityHardcodedSecrets(),
    SecurityHttpInsteadOfHttps(),
    SecuritySQLInjectionPatterns(),
    SecurityPathTraversalPatterns(),
    SecurityCommandInjectionPatterns(),
    SecurityInsecureRandom(),
    SecurityCORSWildcard(),
    SecuritySensitiveDataInLocalStorage(),
]
