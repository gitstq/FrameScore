"""Tests for the rules engine."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framescore.rules.base import (
    BaseRule,
    FileContext,
    Framework,
    Severity,
    Category,
    Issue,
)
from framescore.rules import create_default_registry, RuleRegistry
from framescore.rules.react_rules import (
    ReactConsoleStatements,
    ReactDangerouslySetInnerHTML,
    ReactMissingAltOnImg,
    ReactDirectDOMManipulation,
    ReactUnusedImports,
    ReactIndexAsKey,
)
from framescore.rules.vue_rules import (
    VueConsoleStatements,
    VueMissingKeyInVFor,
    VueVIfAndVForOnSameElement,
)
from framescore.rules.general_rules import (
    GeneralFileTooLong,
    GeneralTodoFixmeHack,
    GeneralDeepNesting,
    GeneralMissingErrorHandling,
)
from framescore.rules.security_rules import (
    SecurityEvalUsage,
    SecurityHardcodedSecrets,
    SecurityHttpInsteadOfHttps,
)
from framescore.rules.performance_rules import (
    PerformanceLargeBundleImports,
    PerformanceSynchronousFileOps,
)


def make_file_context(content, path="test.jsx", framework=Framework.REACT):
    """Helper to create a FileContext for testing."""
    return FileContext(
        file_path=path,
        content=content,
        lines=content.split("\n"),
        framework=framework,
        file_extension=os.path.splitext(path)[1],
        relative_path=path,
    )


class TestBaseRule(unittest.TestCase):
    """Tests for BaseRule class."""

    def test_should_check_includes_matching(self):
        """Test that should_check includes matching files."""
        rule = BaseRule()
        rule.file_patterns = [r"\.jsx$"]
        self.assertTrue(rule.should_check("test.jsx"))
        self.assertTrue(rule.should_check("/path/to/test.jsx"))

    def test_should_check_excludes_matching(self):
        """Test that should_check excludes matching patterns."""
        rule = BaseRule()
        rule.file_patterns = [r".*"]
        self.assertFalse(rule.should_check("node_modules/test.jsx"))
        self.assertFalse(rule.should_check("dist/test.js"))

    def test_create_issue(self):
        """Test issue creation."""
        rule = BaseRule()
        rule.rule_id = "TEST-001"
        rule.name = "Test Rule"
        rule.severity = Severity.ERROR
        rule.category = Category.SECURITY
        rule.framework = Framework.REACT

        ctx = make_file_context("test content")
        issue = rule.create_issue("Test message", ctx, line=5)

        self.assertEqual(issue.rule_id, "TEST-001")
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.line, 5)

    def test_find_pattern(self):
        """Test pattern finding."""
        rule = BaseRule()
        ctx = make_file_context("line1\nconsole.log('test')\nline3")
        matches = rule.find_pattern(ctx.content, r"console\.log")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0][1], 2)  # Line 2

    def test_issue_to_dict(self):
        """Test issue serialization to dict."""
        rule = BaseRule()
        rule.rule_id = "TEST-001"
        rule.name = "Test"
        rule.severity = Severity.WARNING
        rule.category = Category.PERFORMANCE
        rule.framework = Framework.GENERAL

        ctx = make_file_context("test")
        issue = rule.create_issue("msg", ctx, line=1)
        d = issue.to_dict()

        self.assertEqual(d["rule_id"], "TEST-001")
        self.assertEqual(d["severity"], "warning")
        self.assertEqual(d["category"], "performance")


class TestRuleRegistry(unittest.TestCase):
    """Tests for RuleRegistry."""

    def test_create_default_registry(self):
        """Test default registry creation."""
        registry = create_default_registry()
        self.assertGreater(registry.count(), 70)

    def test_get_by_framework(self):
        """Test filtering by framework."""
        registry = create_default_registry()
        react_rules = registry.get_by_framework(Framework.REACT)
        self.assertGreater(len(react_rules), 15)

    def test_get_by_category(self):
        """Test filtering by category."""
        registry = create_default_registry()
        security_rules = registry.get_by_category(Category.SECURITY)
        self.assertGreater(len(security_rules), 5)

    def test_summary(self):
        """Test registry summary."""
        registry = create_default_registry()
        summary = registry.summary()
        self.assertIn("total", summary)
        self.assertIn("by_framework", summary)
        self.assertGreater(summary["total"], 0)


class TestReactRules(unittest.TestCase):
    """Tests for React-specific rules."""

    def test_console_statements_detected(self):
        """Test that console statements are detected."""
        rule = ReactConsoleStatements()
        ctx = make_file_context(
            "const x = 1;\nconsole.log('test');\nconsole.warn('warn');",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_dangerously_set_inner_html_detected(self):
        """Test that dangerouslySetInnerHTML is detected."""
        rule = ReactDangerouslySetInnerHTML()
        ctx = make_file_context(
            '<div dangerouslySetInnerHTML={{ __html: content }} />',
        )
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)

    def test_missing_alt_on_img_detected(self):
        """Test that missing alt on img is detected."""
        rule = ReactMissingAltOnImg()
        ctx = make_file_context('<img src="/logo.png" />')
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)

    def test_alt_present_no_issue(self):
        """Test that img with alt doesn't trigger."""
        rule = ReactMissingAltOnImg()
        ctx = make_file_context('<img src="/logo.png" alt="Logo" />')
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 0)

    def test_direct_dom_manipulation_detected(self):
        """Test that direct DOM manipulation is detected."""
        rule = ReactDirectDOMManipulation()
        ctx = make_file_context(
            "document.getElementById('app');\n"
            "document.querySelector('.class');",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_unused_imports_detected(self):
        """Test that unused imports are detected."""
        rule = ReactUnusedImports()
        ctx = make_file_context(
            "import React from 'react';\n"
            "import unused from 'unused-module';\n"
            "function App() { return <div />; }\n"
            "export default App;",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_index_as_key_detected(self):
        """Test that index as key is detected."""
        rule = ReactIndexAsKey()
        ctx = make_file_context(
            "items.map((item, index) => <li key={index}>{item.name}</li>)",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)


class TestVueRules(unittest.TestCase):
    """Tests for Vue-specific rules."""

    def test_console_statements_detected(self):
        """Test that console statements are detected in Vue files."""
        rule = VueConsoleStatements()
        ctx = make_file_context(
            "<template><div></div></template>\n"
            "<script>\nconsole.log('test');\n</script>",
            path="test.vue",
            framework=Framework.VUE,
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_missing_key_in_vfor(self):
        """Test that missing key in v-for is detected."""
        rule = VueMissingKeyInVFor()
        ctx = make_file_context(
            '<template>\n'
            '  <div v-for="item in items">{{ item.name }}</div>\n'
            '</template>',
            path="test.vue",
            framework=Framework.VUE,
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_vif_and_vfor_same_element(self):
        """Test that v-if and v-for on same element is detected."""
        rule = VueVIfAndVForOnSameElement()
        ctx = make_file_context(
            '<template>\n'
            '  <div v-if="show" v-for="item in items">{{ item }}</div>\n'
            '</template>',
            path="test.vue",
            framework=Framework.VUE,
        )
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)


class TestGeneralRules(unittest.TestCase):
    """Tests for general rules."""

    def test_file_too_long(self):
        """Test that long files are detected."""
        rule = GeneralFileTooLong()
        content = "\n".join([f"// line {i}" for i in range(501)])
        ctx = make_file_context(content, path="test.jsx")
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)

    def test_file_not_too_long(self):
        """Test that short files don't trigger."""
        rule = GeneralFileTooLong()
        content = "\n".join([f"// line {i}" for i in range(100)])
        ctx = make_file_context(content, path="test.jsx")
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 0)

    def test_todo_detected(self):
        """Test that TODO comments are detected."""
        rule = GeneralTodoFixmeHack()
        ctx = make_file_context("// TODO: fix this later\n// FIXME: broken")
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 2)

    def test_deep_nesting_detected(self):
        """Test that deep nesting is detected."""
        rule = GeneralDeepNesting()
        # Rule uses 2-space indentation, level > 4 means indent > 8 spaces
        content = (
            "          if (a) {\n"  # 10 spaces = level 5
            "            x = 1;\n"
            "          }\n"
        )
        ctx = make_file_context(content, path="test.jsx")
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_missing_error_handling_detected(self):
        """Test that missing error handling in async functions is detected."""
        rule = GeneralMissingErrorHandling()
        ctx = make_file_context(
            "async function fetchData() {\n"
            "  const res = await fetch('/api');\n"
            "  const data = await res.json();\n"
            "  return data;\n"
            "}\n",
            path="test.jsx",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)


class TestSecurityRules(unittest.TestCase):
    """Tests for security rules."""

    def test_eval_detected(self):
        """Test that eval() is detected."""
        rule = SecurityEvalUsage()
        ctx = make_file_context("eval('alert(1)');")
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_hardcoded_secrets_detected(self):
        """Test that hardcoded secrets are detected."""
        rule = SecurityHardcodedSecrets()
        ctx = make_file_context(
            'const API_KEY = "sk-1234567890abcdef";\n'
            'const PASSWORD = "supersecret";',
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)

    def test_http_detected(self):
        """Test that http:// URLs are detected."""
        rule = SecurityHttpInsteadOfHttps()
        ctx = make_file_context(
            'fetch("http://api.example.com/data");',
        )
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)

    def test_localhost_not_flagged(self):
        """Test that localhost URLs are not flagged."""
        rule = SecurityHttpInsteadOfHttps()
        ctx = make_file_context(
            'fetch("http://localhost:3000/api");',
        )
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 0)


class TestPerformanceRules(unittest.TestCase):
    """Tests for performance rules."""

    def test_large_bundle_import_detected(self):
        """Test that large library imports are detected."""
        rule = PerformanceLargeBundleImports()
        ctx = make_file_context("import lodash from 'lodash';")
        issues = rule.check(ctx)
        self.assertEqual(len(issues), 1)

    def test_sync_file_ops_detected(self):
        """Test that synchronous file operations are detected."""
        rule = PerformanceSynchronousFileOps()
        ctx = make_file_context(
            "const data = fs.readFileSync('/path/to/file');",
        )
        issues = rule.check(ctx)
        self.assertGreater(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
