import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional

from commit_critic.utils import console


class GitOperations:
    """Handle all Git-related operations."""

    @staticmethod
    def is_git_repo(path: str = ".") -> bool:
        try:
            subprocess.run(
                ["git", "-C", path, "rev-parse", "--git-dir"],
                capture_output=True, check=True, text=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_commits(
        repo_path: str = ".",
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        limit = min(limit, 100)
        try:
            cmd = ["git", "-C", repo_path, "log", f"-{limit}", "--format=%H|%s|%b"]
            if branch:
                cmd.append(branch)
            if start_date:
                cmd += [f"--after={start_date}"]
            if end_date:
                cmd += [f"--before={end_date}"]

            result = subprocess.run(cmd, capture_output=True, check=True, text=True)

            commits = []
            for line in result.stdout.split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|", 2)
                if len(parts) >= 2:
                    hash_val, subject = parts[0], parts[1]
                    body = parts[2] if len(parts) > 2 else ""
                    full_message = subject
                    if body.strip():
                        full_message += "\n" + body.strip()
                    commits.append({"hash": hash_val[:8], "message": full_message.strip()})
            return commits

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error reading git log: {e}[/red]")
            return []

    @staticmethod
    def get_staged_diff() -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True, check=True, text=True
            )
            return result.stdout if result.stdout.strip() else None
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error reading staged changes: {e}[/red]")
            return None

    @staticmethod
    def get_diff_stats() -> Optional[Dict[str, int]]:
        try:
            result = subprocess.run(
                ["git", "diff", "--staged", "--numstat"],
                capture_output=True, check=True, text=True
            )
            if not result.stdout.strip():
                return None

            files_changed = additions = deletions = 0
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        try:
                            additions += int(parts[0]) if parts[0] != "-" else 0
                            deletions += int(parts[1]) if parts[1] != "-" else 0
                            files_changed += 1
                        except ValueError:
                            continue
            return {"files": files_changed, "additions": additions, "deletions": deletions}

        except subprocess.CalledProcessError:
            return None

    @staticmethod
    def clone_repo(url: str, depth: int = 50) -> Optional[str]:
        temp_dir = tempfile.mkdtemp(prefix="commit_critic_")
        try:
            console.print(f"[cyan]Cloning repository from {url}...[/cyan]")
            subprocess.run(
                ["git", "clone", "--depth", str(depth), url, temp_dir],
                capture_output=True, check=True, text=True
            )
            return temp_dir
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error cloning repository: {e.stderr}[/red]")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
