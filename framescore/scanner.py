"""Project scanner - detects framework, collects files, and parses source code."""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .rules.base import FileContext, Framework
from .utils import (
    extract_exports,
    extract_imports,
    extract_vue_script,
    extract_vue_template,
    read_file,
)


@dataclass
class ProjectInfo:
    """Information about a scanned project.

    Attributes:
        root_path: Absolute path to the project root.
        framework: Detected frontend framework.
        files: List of source file paths (absolute).
        package_json: Parsed package.json content, if present.
        config_files: Dictionary of config file paths and their contents.
        total_lines: Total lines of code across all files.
        total_files: Total number of source files.
    """

    root_path: str = ""
    framework: Framework = Framework.GENERAL
    files: List[str] = field(default_factory=list)
    package_json: Optional[dict] = None
    config_files: Dict[str, str] = field(default_factory=dict)
    total_lines: int = 0
    total_files: int = 0


# File extensions by framework
FRAMEWORK_EXTENSIONS = {
    Framework.REACT: {".jsx", ".tsx", ".js", ".ts"},
    Framework.VUE: {".vue", ".js", ".ts"},
    Framework.SVELTE: {".svelte", ".js", ".ts"},
    Framework.ANGULAR: {".ts", ".html", ".js"},
    Framework.GENERAL: {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".mjs", ".cjs"},
}

# Directories to skip during scanning
SKIP_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".output",
    "coverage",
    ".cache",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "vendor",
    "bower_components",
    ".turbo",
    ".svelte-kit",
}


class ProjectScanner:
    """Scans a project directory to detect framework and collect source files.

    Provides methods for framework detection, file collection, and
    basic source code parsing.
    """

    def __init__(self, root_path: str, framework_override: Optional[str] = None):
        """Initialize the scanner.

        Args:
            root_path: Path to the project root directory.
            framework_override: Override auto-detected framework ('react', 'vue', etc.).
        """
        self.root_path = os.path.normpath(os.path.abspath(root_path))
        self.framework_override = framework_override

    def scan(self) -> ProjectInfo:
        """Scan the project and return project information.

        Returns:
            ProjectInfo with detected framework, files, and metadata.
        """
        info = ProjectInfo(root_path=self.root_path)

        # Detect framework
        info.framework = self.detect_framework()

        # Collect source files
        info.files = self.collect_files(info.framework)

        # Parse package.json
        info.package_json = self.parse_package_json()

        # Find config files
        info.config_files = self.find_config_files()

        # Count lines
        info.total_files = len(info.files)
        info.total_lines = self._count_total_lines(info.files)

        return info

    def detect_framework(self) -> Framework:
        """Detect the frontend framework used by the project.

        Returns:
            Detected Framework enum value.
        """
        if self.framework_override and self.framework_override != "auto":
            fw_map = {
                "react": Framework.REACT,
                "vue": Framework.VUE,
                "svelte": Framework.SVELTE,
                "angular": Framework.ANGULAR,
                "general": Framework.GENERAL,
            }
            return fw_map.get(self.framework_override.lower(), Framework.GENERAL)

        # Check package.json dependencies
        pkg = self.parse_package_json()
        if pkg:
            deps = {}
            deps.update(pkg.get("dependencies", {}))
            deps.update(pkg.get("devDependencies", {}))

            dep_lower = {k.lower(): v for k, v in deps.items()}

            # Angular detection
            if any(
                k in dep_lower
                for k in [
                    "@angular/core",
                    "@angular/common",
                    "angular",
                ]
            ):
                return Framework.ANGULAR

            # React detection
            if any(
                k in dep_lower
                for k in [
                    "react",
                    "react-dom",
                    "next",
                    "next.js",
                    "gatsby",
                    "remix",
                ]
            ):
                return Framework.REACT

            # Vue detection
            if any(
                k in dep_lower
                for k in [
                    "vue",
                    "nuxt",
                    "nuxt.js",
                    "@vue/runtime-core",
                ]
            ):
                return Framework.VUE

            # Svelte detection
            if any(
                k in dep_lower
                for k in [
                    "svelte",
                    "@sveltejs/kit",
                    "@sveltejs/vite-plugin-svelte",
                ]
            ):
                return Framework.SVELTE

        # Check config files
        config_files = os.listdir(self.root_path) if os.path.isdir(self.root_path) else []

        if "angular.json" in config_files:
            return Framework.ANGULAR
        if "vue.config.js" in config_files or "vite.config.ts" in config_files:
            # Could be Vue or Svelte, check further
            vite_config = os.path.join(self.root_path, "vite.config.ts")
            if os.path.exists(vite_config):
                content = read_file(vite_config)
                if "svelte" in content:
                    return Framework.SVELTE
                if "vue" in content:
                    return Framework.VUE
        if "svelte.config.js" in config_files or "svelte.config.cjs" in config_files:
            return Framework.SVELTE
        if "next.config.js" in config_files or "next.config.mjs" in config_files:
            return Framework.REACT

        # Check file extensions in the project
        framework_by_ext = self._detect_framework_by_extensions()
        if framework_by_ext:
            return framework_by_ext

        return Framework.GENERAL

    def _detect_framework_by_extensions(self) -> Optional[Framework]:
        """Detect framework by analyzing file extensions in the project.

        Returns:
            Framework if a clear match is found, None otherwise.
        """
        ext_counts = {}
        for root, dirs, files in os.walk(self.root_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for f in files:
                _, ext = os.path.splitext(f)
                ext = ext.lower()
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

        # Count framework-specific files
        react_count = ext_counts.get(".jsx", 0) + ext_counts.get(".tsx", 0)
        vue_count = ext_counts.get(".vue", 0)
        svelte_count = ext_counts.get(".svelte", 0)

        # Need at least a few files to make a determination
        if react_count > 2:
            return Framework.REACT
        if vue_count > 2:
            return Framework.VUE
        if svelte_count > 2:
            return Framework.SVELTE

        return None

    def collect_files(
        self,
        framework: Framework = Framework.GENERAL,
        max_files: int = 5000,
    ) -> List[str]:
        """Collect all source files in the project.

        Args:
            framework: Framework to determine which extensions to include.
            max_files: Maximum number of files to collect.

        Returns:
            List of absolute file paths.
        """
        extensions = FRAMEWORK_EXTENSIONS.get(framework, FRAMEWORK_EXTENSIONS[Framework.GENERAL])
        files = []

        for root, dirs, filenames in os.walk(self.root_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    full_path = os.path.join(root, filename)
                    files.append(full_path)
                    if len(files) >= max_files:
                        return files

        return files

    def parse_package_json(self) -> Optional[dict]:
        """Parse the project's package.json file.

        Returns:
            Parsed package.json as dict, or None if not found.
        """
        pkg_path = os.path.join(self.root_path, "package.json")
        if not os.path.exists(pkg_path):
            return None

        content = read_file(pkg_path)
        if not content:
            return None

        try:
            return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return None

    def find_config_files(self) -> Dict[str, str]:
        """Find and read configuration files.

        Returns:
            Dictionary mapping config file names to their contents.
        """
        configs = {}
        config_names = [
            "package.json",
            "tsconfig.json",
            ".eslintrc",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yml",
            ".prettierrc",
            ".prettierrc.js",
            ".prettierrc.json",
            "vite.config.js",
            "vite.config.ts",
            "webpack.config.js",
            "next.config.js",
            "vue.config.js",
            "svelte.config.js",
            "angular.json",
            ".babelrc",
            ".babelrc.js",
            "babel.config.js",
            "tailwind.config.js",
            "postcss.config.js",
            "jest.config.js",
        ]

        for name in config_names:
            path = os.path.join(self.root_path, name)
            if os.path.exists(path):
                content = read_file(path)
                if content:
                    configs[name] = content

        return configs

    def build_file_context(self, file_path: str, framework: Framework) -> FileContext:
        """Build a FileContext for a given file.

        Args:
            file_path: Absolute path to the file.
            framework: Project framework.

        Returns:
            FileContext with parsed file information.
        """
        content = read_file(file_path)
        lines = content.split("\n") if content else []
        _, ext = os.path.splitext(file_path)
        relative = os.path.relpath(file_path, self.root_path)

        imports = extract_imports(content)
        exports = extract_exports(content)

        # Determine file-level framework
        file_framework = framework
        if ext == ".vue":
            file_framework = Framework.VUE
        elif ext == ".svelte":
            file_framework = Framework.SVELTE
        elif ext in (".jsx", ".tsx"):
            if framework == Framework.GENERAL:
                file_framework = Framework.REACT

        return FileContext(
            file_path=file_path,
            content=content,
            lines=lines,
            imports=imports,
            exports=exports,
            framework=file_framework,
            file_extension=ext,
            relative_path=relative,
        )

    def _count_total_lines(self, files: List[str]) -> int:
        """Count total lines across all files.

        Args:
            files: List of file paths.

        Returns:
            Total line count.
        """
        total = 0
        for f in files:
            content = read_file(f)
            if content:
                total += content.count("\n") + 1
        return total
