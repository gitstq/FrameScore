"""Tests for the project scanner."""

import os
import sys
import unittest

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framescore.scanner import ProjectScanner, ProjectInfo
from framescore.rules.base import Framework


class TestProjectScanner(unittest.TestCase):
    """Tests for ProjectScanner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = os.path.join(
            os.path.dirname(__file__), "fixtures"
        )
        self.react_project = os.path.join(self.fixtures_dir, "react_project")
        self.vue_project = os.path.join(self.fixtures_dir, "vue_project")

    def test_detect_react_framework(self):
        """Test that React framework is detected from package.json."""
        scanner = ProjectScanner(self.react_project)
        framework = scanner.detect_framework()
        self.assertEqual(framework, Framework.REACT)

    def test_detect_vue_framework(self):
        """Test that Vue framework is detected from package.json."""
        scanner = ProjectScanner(self.vue_project)
        framework = scanner.detect_framework()
        self.assertEqual(framework, Framework.VUE)

    def test_framework_override(self):
        """Test that framework override works."""
        scanner = ProjectScanner(self.react_project, framework_override="vue")
        framework = scanner.detect_framework()
        self.assertEqual(framework, Framework.VUE)

    def test_collect_react_files(self):
        """Test that React files are collected."""
        scanner = ProjectScanner(self.react_project)
        files = scanner.collect_files(Framework.REACT)
        self.assertGreater(len(files), 0)

        # Check that .jsx files are included
        extensions = [os.path.splitext(f)[1] for f in files]
        self.assertIn(".jsx", extensions)

    def test_collect_vue_files(self):
        """Test that Vue files are collected."""
        scanner = ProjectScanner(self.vue_project)
        files = scanner.collect_files(Framework.VUE)
        self.assertGreater(len(files), 0)

        # Check that .vue files are included
        extensions = [os.path.splitext(f)[1] for f in files]
        self.assertIn(".vue", extensions)

    def test_parse_package_json(self):
        """Test package.json parsing."""
        scanner = ProjectScanner(self.react_project)
        pkg = scanner.parse_package_json()
        self.assertIsNotNone(pkg)
        self.assertIn("dependencies", pkg)
        self.assertIn("react", pkg["dependencies"])

    def test_parse_package_json_missing(self):
        """Test handling of missing package.json."""
        scanner = ProjectScanner("/tmp/nonexistent")
        pkg = scanner.parse_package_json()
        self.assertIsNone(pkg)

    def test_scan_react_project(self):
        """Test full scan of React project."""
        scanner = ProjectScanner(self.react_project)
        info = scanner.scan()
        self.assertEqual(info.framework, Framework.REACT)
        self.assertGreater(info.total_files, 0)
        self.assertGreater(info.total_lines, 0)
        self.assertIsNotNone(info.package_json)

    def test_scan_vue_project(self):
        """Test full scan of Vue project."""
        scanner = ProjectScanner(self.vue_project)
        info = scanner.scan()
        self.assertEqual(info.framework, Framework.VUE)
        self.assertGreater(info.total_files, 0)

    def test_build_file_context(self):
        """Test building file context."""
        scanner = ProjectScanner(self.react_project)
        files = scanner.collect_files(Framework.REACT)
        if files:
            ctx = scanner.build_file_context(files[0], Framework.REACT)
            self.assertIsNotNone(ctx.content)
            self.assertGreater(len(ctx.lines), 0)
            self.assertEqual(ctx.framework, Framework.REACT)

    def test_skip_node_modules(self):
        """Test that node_modules is skipped during scanning."""
        scanner = ProjectScanner(self.react_project)
        files = scanner.collect_files(Framework.GENERAL)
        for f in files:
            self.assertNotIn("node_modules", f)

    def test_find_config_files(self):
        """Test config file detection."""
        scanner = ProjectScanner(self.react_project)
        configs = scanner.find_config_files()
        self.assertIn("package.json", configs)


class TestProjectInfo(unittest.TestCase):
    """Tests for ProjectInfo dataclass."""

    def test_default_values(self):
        """Test ProjectInfo default values."""
        info = ProjectInfo()
        self.assertEqual(info.root_path, "")
        self.assertEqual(info.framework, Framework.GENERAL)
        self.assertEqual(info.files, [])
        self.assertEqual(info.total_files, 0)
        self.assertEqual(info.total_lines, 0)


if __name__ == "__main__":
    unittest.main()
