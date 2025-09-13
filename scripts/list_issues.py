import json
import os
import re
import subprocess
import sys
from urllib.request import urlopen, Request


def get_origin_repo():
    try:
        url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"])  # nosec
            .decode()
            .strip()
        )
    except Exception as e:
        print(f"Failed to read git remote: {e}", file=sys.stderr)
        return None

    # Examples:
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    m = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", url)
    if not m:
        return None
    owner = m.group("owner")
    repo = m.group("repo")
    return f"{owner}/{repo}"


def fetch_open_issues(owner_repo: str):
    api = f"https://api.github.com/repos/{owner_repo}/issues?state=open&per_page=100"
    req = Request(api, headers={"User-Agent": "codex-cli"})
    with urlopen(req, timeout=30) as resp:  # nosec - fetching public GitHub API
        data = json.loads(resp.read().decode())
    # Filter out pull requests (issues API returns PRs as issues with pull_request key)
    issues = [i for i in data if not isinstance(i, dict) or "pull_request" not in i]
    return issues


def main():
    owner_repo = get_origin_repo()
    if not owner_repo:
        print("Could not determine GitHub repo from git remotes.", file=sys.stderr)
        sys.exit(1)

    try:
        issues = fetch_open_issues(owner_repo)
    except Exception as e:
        print(f"Failed to fetch issues: {e}", file=sys.stderr)
        sys.exit(2)

    if not issues:
        print("No open issues found.")
        return

    for i in issues:
        number = i.get("number")
        title = i.get("title", "")
        state = i.get("state", "")
        labels = ",".join([l.get("name", "") for l in i.get("labels", [])]) or "-"
        url = i.get("html_url", "")
        print(f"#{number}: {title} | state={state} | labels={labels} | url={url}")


if __name__ == "__main__":
    main()

