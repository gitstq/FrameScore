"""Dependency health analysis for package.json and requirements.txt."""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DependencyInfo:
    """Information about a single dependency.

    Attributes:
        name: Package name.
        version: Installed version.
        is_dev: Whether this is a dev dependency.
        is_outdated: Whether a newer version may be available.
        has_known_issues: Whether the dependency has known issues.
    """

    name: str
    version: str = ""
    is_dev: bool = False
    is_outdated: bool = False
    has_known_issues: bool = False


@dataclass
class DepHealthResult:
    """Result of dependency health analysis.

    Attributes:
        total_deps: Total number of dependencies.
        dev_deps: Number of dev dependencies.
        prod_deps: Number of production dependencies.
        outdated_count: Number of potentially outdated dependencies.
        issues_count: Number of dependencies with known issues.
        has_lock_file: Whether a lock file exists.
        has_non_semver: Whether non-semver versions are used.
        duplicate_deps: List of duplicate dependency names.
        missing_lock: Whether the lock file is missing.
        health_score: Dependency health score (0-100).
        details: Detailed dependency information.
    """

    total_deps: int = 0
    dev_deps: int = 0
    prod_deps: int = 0
    outdated_count: int = 0
    issues_count: int = 0
    has_lock_file: bool = False
    has_non_semver: bool = False
    duplicate_deps: List[str] = field(default_factory=list)
    missing_lock: bool = False
    health_score: float = 100.0
    details: List[DependencyInfo] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_deps": self.total_deps,
            "dev_deps": self.dev_deps,
            "prod_deps": self.prod_deps,
            "outdated_count": self.outdated_count,
            "issues_count": self.issues_count,
            "has_lock_file": self.has_lock_file,
            "has_non_semver": self.has_non_semver,
            "duplicate_deps": self.duplicate_deps,
            "missing_lock": self.missing_lock,
            "health_score": round(self.health_score, 1),
        }


# Known problematic version patterns
NON_SEMVER_PATTERNS = [
    r"^[~^]?(?:latest|next|canary|nightly|experimental|unstable|rc|beta|alpha|dev|master|main)$",
    r"\*",
    r"^file:",
    r"^link:",
    r"^github:",
    r"^git:",
    r"^http:",
    r"^git\+",
]

# Commonly outdated or problematic packages (heuristic)
KNOWN_PROBLEMATIC = {
    "moment": "Consider using date-fns or dayjs instead (smaller bundle).",
    "underscore": "Consider using lodash or native methods instead.",
    "jquery": "Consider using modern DOM APIs instead.",
    "request": "Deprecated - use node-fetch, axios, or native fetch.",
    "bluebird": "Native Promises are now well-supported.",
    "core-js": "Check if you need the full build vs. targeted polyfills.",
}


class DependencyAnalyzer:
    """Analyzes dependency health for JavaScript and Python projects.

    Parses package.json and requirements.txt to check for:
    - Outdated dependencies (basic heuristic)
    - Known problematic packages
    - Missing lock files
    - Non-semver version specifications
    - Duplicate dependencies
    """

    def __init__(self, root_path: str):
        """Initialize the dependency analyzer.

        Args:
            root_path: Path to the project root.
        """
        self.root_path = os.path.normpath(os.path.abspath(root_path))

    def analyze(self) -> DepHealthResult:
        """Analyze dependency health.

        Returns:
            DepHealthResult with analysis findings.
        """
        result = DepHealthResult()

        # Check for package.json (JavaScript/Node.js)
        pkg_path = os.path.join(self.root_path, "package.json")
        if os.path.exists(pkg_path):
            self._analyze_package_json(pkg_path, result)

        # Check for requirements.txt (Python)
        req_path = os.path.join(self.root_path, "requirements.txt")
        if os.path.exists(req_path):
            self._analyze_requirements_txt(req_path, result)

        # Check for lock files
        result.has_lock_file = self._check_lock_file()
        if not result.has_lock_file and result.total_deps > 0:
            result.missing_lock = True

        # Calculate health score
        result.health_score = self._calculate_health_score(result)

        return result

    def _analyze_package_json(self, pkg_path: str, result: DepHealthResult) -> None:
        """Analyze a package.json file.

        Args:
            pkg_path: Path to package.json.
            result: Result object to populate.
        """
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        all_deps = {}
        # Production dependencies
        prod_deps = pkg.get("dependencies", {})
        for name, version in prod_deps.items():
            all_deps[name] = DependencyInfo(
                name=name,
                version=str(version),
                is_dev=False,
            )

        # Dev dependencies
        dev_deps = pkg.get("devDependencies", {})
        for name, version in dev_deps.items():
            all_deps[name] = DependencyInfo(
                name=name,
                version=str(version),
                is_dev=True,
            )

        result.prod_deps = len(prod_deps)
        result.dev_deps = len(dev_deps)
        result.total_deps = result.prod_deps + result.dev_deps

        # Check for duplicates between dependencies and devDependencies
        for name in prod_deps:
            if name in dev_deps:
                result.duplicate_deps.append(name)

        # Check each dependency
        for dep_info in all_deps.values():
            # Check for non-semver versions
            for pattern in NON_SEMVER_PATTERNS:
                if re.match(pattern, dep_info.version):
                    result.has_non_semver = True
                    break

            # Check for known problematic packages
            base_name = dep_info.name.split("/")[0].split("@")[0].lower()
            if base_name in KNOWN_PROBLEMATIC:
                dep_info.has_known_issues = True
                result.issues_count += 1

            # Check for potentially outdated (very old major versions)
            version_match = re.match(r"^[\^~]?(0|[1-9]\d*)", dep_info.version)
            if version_match:
                major = int(version_match.group(1))
                if major == 0:
                    dep_info.is_outdated = True
                    result.outdated_count += 1

            result.details.append(dep_info)

    def _analyze_requirements_txt(self, req_path: str, result: DepHealthResult) -> None:
        """Analyze a requirements.txt file.

        Args:
            req_path: Path to requirements.txt.
            result: Result object to populate.
        """
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except IOError:
            return

        seen_packages = set()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package name and version
            match = re.match(
                r"^([A-Za-z0-9][\w.-]*)\s*(?:[=<>!~]+\s*(\S+))?", line
            )
            if match:
                name = match.group(1)
                version = match.group(2) or ""

                result.total_deps += 1

                if name.lower() in seen_packages:
                    result.duplicate_deps.append(name)
                seen_packages.add(name.lower())

                dep_info = DependencyInfo(
                    name=name,
                    version=version,
                    is_dev=False,
                )

                # Check for non-semver or unversioned
                if not version:
                    result.has_non_semver = True

                result.details.append(dep_info)

    def _check_lock_file(self) -> bool:
        """Check if a lock file exists.

        Returns:
            True if a lock file is found.
        """
        lock_files = [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "bun.lockb",
        ]
        for lf in lock_files:
            if os.path.exists(os.path.join(self.root_path, lf)):
                return True
        return False

    def _calculate_health_score(self, result: DepHealthResult) -> float:
        """Calculate dependency health score.

        Args:
            result: Dependency analysis result.

        Returns:
            Health score from 0 to 100.
        """
        score = 100.0

        # Deductions
        if result.missing_lock:
            score -= 10
        if result.has_non_semver:
            score -= 5
        score -= result.issues_count * 3
        score -= result.outdated_count * 2
        score -= len(result.duplicate_deps) * 5

        return max(0.0, score)
