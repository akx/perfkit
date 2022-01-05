import shutil
import subprocess

git = shutil.which("git")


def get_git_commit() -> str:
    return subprocess.check_output([git, "rev-parse", "HEAD"], encoding="utf-8").strip()
