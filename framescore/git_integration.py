"""Git history integration for score tracking."""

import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class GitCommit:
    """Information about a git commit.

    Attributes:
        hash: Commit hash (short).
        author: Author name.
        date: Commit date.
        message: Commit message (first line).
    """

    hash: str = ""
    author: str = ""
    date: str = ""
    message: str = ""


@dataclass
class ScoreHistoryEntry:
    """A single entry in the score history.

    Attributes:
        commit_hash: Commit hash.
        date: Date of the commit.
        score: Health score at this commit.
        grade: Grade at this commit.
        issues_count: Number of issues at this commit.
    """

    commit_hash: str = ""
    date: str = ""
    score: float = 100.0
    grade: str = "A+"
    issues_count: int = 0


@dataclass
class GitInfo:
    """Information about the git repository.

    Attributes:
        is_git_repo: Whether the path is a git repository.
        current_branch: Current branch name.
        total_commits: Total number of commits.
        recent_commits: List of recent commits.
    """

    is_git_repo: bool = False
    current_branch: str = ""
    total_commits: int = 0
    recent_commits: List[GitCommit] = field(default_factory=list)


class GitIntegration:
    """Integrates with git for score history tracking and blame analysis.

    Provides methods for reading git history, tracking score changes
    over time, and associating issues with commits.
    """

    def __init__(self, root_path: str):
        """Initialize git integration.

        Args:
            root_path: Path to the project root (should be a git repo).
        """
        self.root_path = os.path.normpath(os.path.abspath(root_path))

    def is_git_repo(self) -> bool:
        """Check if the path is a git repository.

        Returns:
            True if the path is inside a git repository.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_git_info(self) -> GitInfo:
        """Get information about the git repository.

        Returns:
            GitInfo with repository details.
        """
        info = GitInfo()
        info.is_git_repo = self.is_git_repo()

        if not info.is_git_repo:
            return info

        # Get current branch
        info.current_branch = self._run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"

        # Get total commits
        count_str = self._run_git(["git", "rev-list", "--count", "HEAD"])
        info.total_commits = int(count_str) if count_str else 0

        # Get recent commits
        info.recent_commits = self.get_recent_commits(20)

        return info

    def get_recent_commits(self, limit: int = 20) -> List[GitCommit]:
        """Get recent commits from the repository.

        Args:
            limit: Maximum number of commits to return.

        Returns:
            List of GitCommit objects.
        """
        if not self.is_git_repo():
            return []

        log_format = "%h|%an|%ai|%s"
        output = self._run_git([
            "git", "log", f"-{limit}", f"--format={log_format}", "--no-merges"
        ])

        if not output:
            return []

        commits = []
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|", 3)
            if len(parts) >= 4:
                commits.append(GitCommit(
                    hash=parts[0].strip(),
                    author=parts[1].strip(),
                    date=parts[2].strip(),
                    message=parts[3].strip(),
                ))

        return commits

    def get_changed_files(self, since_commit: Optional[str] = None) -> List[str]:
        """Get list of changed files.

        Args:
            since_commit: Optional commit hash to compare against.
                         If None, compares against the previous commit.

        Returns:
            List of changed file paths (relative to repo root).
        """
        if not self.is_git_repo():
            return []

        if since_commit:
            output = self._run_git([
                "git", "diff", "--name-only", since_commit, "HEAD"
            ])
        else:
            output = self._run_git([
                "git", "diff", "--name-only", "HEAD~1", "HEAD"
            ])

        if not output:
            return []

        files = []
        for line in output.strip().split("\n"):
            if line.strip():
                full_path = os.path.join(self.root_path, line.strip())
                files.append(full_path)

        return files

    def get_blame_for_line(self, file_path: str, line_number: int) -> Optional[str]:
        """Get the commit hash that last changed a specific line.

        Args:
            file_path: Path to the file.
            line_number: 1-based line number.

        Returns:
            Commit hash or None.
        """
        if not self.is_git_repo():
            return None

        rel_path = os.path.relpath(file_path, self.root_path)
        output = self._run_git([
            "git", "blame", "-L", f"{line_number},{line_number}", "-p", rel_path
        ])

        if not output:
            return None

        match = re.search(r"^([0-9a-f]{40})", output)
        return match.group(1)[:8] if match else None

    def get_score_history(self) -> List[ScoreHistoryEntry]:
        """Get score history from git notes or a history file.

        Looks for a .framescore-history.json file in the repo.

        Returns:
            List of score history entries.
        """
        history_file = os.path.join(self.root_path, ".framescore-history.json")
        if not os.path.exists(history_file):
            return []

        try:
            import json
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = []
            for entry in data.get("history", []):
                entries.append(ScoreHistoryEntry(
                    commit_hash=entry.get("commit_hash", ""),
                    date=entry.get("date", ""),
                    score=entry.get("score", 100.0),
                    grade=entry.get("grade", "A+"),
                    issues_count=entry.get("issues_count", 0),
                ))
            return entries
        except (json.JSONDecodeError, IOError, KeyError):
            return []

    def save_score_to_history(
        self,
        score: float,
        grade: str,
        issues_count: int,
    ) -> None:
        """Save the current score to the history file.

        Args:
            score: Current health score.
            grade: Current grade.
            issues_count: Number of issues.
        """
        import json

        history_file = os.path.join(self.root_path, ".framescore-history.json")

        # Load existing history
        history = {"history": []}
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Get current commit info
        commit_hash = self._run_git(["git", "rev-parse", "--short", "HEAD"]) or "unknown"
        commit_date = self._run_git(["git", "log", "-1", "--format=%ai"]) or ""

        # Add new entry
        entry = {
            "commit_hash": commit_hash,
            "date": commit_date.strip(),
            "score": score,
            "grade": grade,
            "issues_count": issues_count,
        }
        history["history"].append(entry)

        # Keep only last 100 entries
        history["history"] = history["history"][-100:]

        # Save
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except IOError:
            pass

    def _run_git(self, args: List[str]) -> Optional[str]:
        """Run a git command and return its output.

        Args:
            args: Command arguments (including 'git').

        Returns:
            Command output as string, or None on failure.
        """
        try:
            result = subprocess.run(
                args,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
