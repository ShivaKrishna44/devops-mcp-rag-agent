"""
GitHub MCP Tools
================
Provides tools to interact with GitHub repositories, PRs, issues, and workflows.
Includes WRITE tools: create repo, push files, create PRs — all with approval gates.

Requirements:
  pip install PyGithub

Environment:
  export GITHUB_TOKEN="ghp_your_personal_access_token"
  export GITHUB_OWNER="ShivaKrishna44"

Generate token: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
Required scopes: repo, workflow, delete_repo (for create/delete)

WRITE TOOLS (require GITHUB_ALLOW_WRITES=true):
  create_repo, push_file, create_pull_request, merge_pull_request, delete_repo
"""

import os
import json
import base64
from fastmcp import FastMCP

mcp = FastMCP("GitHub Tools")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "ShivaKrishna44")

# Safety gate — write operations only work when explicitly enabled
# Set: export GITHUB_ALLOW_WRITES=true
ALLOW_WRITES = os.getenv("GITHUB_ALLOW_WRITES", "false").lower() == "true"


def _write_guard() -> str | None:
    """Returns error message if writes are disabled, None if allowed."""
    if not ALLOW_WRITES:
        return (
            "⛔ Write operations are DISABLED.\n"
            "To enable: export GITHUB_ALLOW_WRITES=true\n"
            "This prevents accidental pushes. Set only when you intend to write."
        )
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN not set. Export your token first."
    return None


@mcp.tool
def list_repos() -> str:
    """List all repositories for the configured GitHub owner."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        user = g.get_user(GITHUB_OWNER)
        repos = []
        for repo in user.get_repos():
            repos.append(f"  {repo.name} — {repo.description or 'no description'} ({'private' if repo.private else 'public'})")
        return f"Repositories for {GITHUB_OWNER}:\n" + "\n".join(repos[:20])
    except Exception as e:
        return f"Error: {str(e)}. Is GITHUB_TOKEN set?"


@mcp.tool
def list_pull_requests(repo_name: str, state: str = "open") -> str:
    """List pull requests for a repository. State: open, closed, all."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        prs = repo.get_pulls(state=state)
        result = []
        for pr in prs[:10]:
            result.append(f"  #{pr.number} [{pr.state}] {pr.title} (by {pr.user.login})")
        if not result:
            return f"No {state} pull requests in {repo_name}"
        return f"Pull Requests ({state}) for {repo_name}:\n" + "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_recent_commits(repo_name: str, count: int = 10) -> str:
    """Get the most recent commits for a repository."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        commits = repo.get_commits()[:count]
        result = []
        for c in commits:
            msg = c.commit.message.split("\n")[0][:60]
            result.append(f"  {c.sha[:7]} — {msg} ({c.commit.author.name})")
        return f"Recent commits in {repo_name}:\n" + "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def create_issue(repo_name: str, title: str, body: str = "") -> str:
    """Create a new GitHub issue in a repository."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        issue = repo.create_issue(title=title, body=body)
        return f"✅ Issue created: #{issue.number} — {issue.title}\n   URL: {issue.html_url}"
    except Exception as e:
        return f"Error creating issue: {str(e)}"


@mcp.tool
def get_workflow_runs(repo_name: str, count: int = 5) -> str:
    """Get recent GitHub Actions workflow runs (CI/CD status)."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        runs = repo.get_workflow_runs()[:count]
        result = []
        for run in runs:
            status_icon = "✅" if run.conclusion == "success" else "❌" if run.conclusion == "failure" else "⏳"
            result.append(f"  {status_icon} {run.name} — {run.conclusion or 'in_progress'} ({run.created_at.strftime('%Y-%m-%d %H:%M')})")
        if not result:
            return f"No workflow runs found in {repo_name}"
        return f"GitHub Actions runs for {repo_name}:\n" + "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool
def get_repo_branches(repo_name: str) -> str:
    """List all branches in a repository."""
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        branches = [f"  {b.name}" + (" ← default" if b.name == repo.default_branch else "") for b in repo.get_branches()]
        return f"Branches in {repo_name}:\n" + "\n".join(branches[:20])
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print(f"GitHub Tools MCP Server — Owner: {GITHUB_OWNER}")
    print(f"Token: {'configured' if GITHUB_TOKEN else 'NOT SET'}")
    print(f"Write operations: {'ENABLED ⚠️' if ALLOW_WRITES else 'disabled (safe mode)'}")
    mcp.run()


# ==========================================
# WRITE TOOLS (require GITHUB_ALLOW_WRITES=true)
# ==========================================

@mcp.tool
def create_repo(
    repo_name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = True
) -> str:
    """
    Create a new GitHub repository.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true

    Args:
        repo_name: Name of the new repository (e.g., 'my-new-repo')
        description: Short description of the repo
        private: True for private repo, False for public
        auto_init: Initialize with README (recommended: True)

    Example:
        create_repo("test-project", "My test repo", private=False)
    """
    guard = _write_guard()
    if guard:
        return guard

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        user = g.get_user(GITHUB_OWNER)
        repo = user.create_repo(
            name=repo_name,
            description=description,
            private=private,
            auto_init=auto_init
        )
        return (
            f"✅ Repository created!\n"
            f"   Name: {repo.full_name}\n"
            f"   URL: {repo.html_url}\n"
            f"   Visibility: {'private' if repo.private else 'public'}\n"
            f"   Clone: git clone {repo.clone_url}"
        )
    except Exception as e:
        return f"❌ Error creating repo: {str(e)}"


@mcp.tool
def push_file(
    repo_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str = "main"
) -> str:
    """
    Create or update a file in a GitHub repository.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true
    ⚠️ APPROVAL REQUIRED — This will directly commit to the specified branch.

    Args:
        repo_name: Target repository name
        file_path: Path in the repo (e.g., 'src/app.py', 'README.md')
        content: File content to write
        commit_message: Commit message
        branch: Branch to push to (default: main)

    Example:
        push_file("my-repo", "hello.py", "print('hello')", "Add hello.py")
    """
    guard = _write_guard()
    if guard:
        return guard

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")

        # Check if file already exists (update vs create)
        try:
            existing = repo.get_contents(file_path, ref=branch)
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=existing.sha,
                branch=branch
            )
            action = "updated"
        except Exception:
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch
            )
            action = "created"

        commit = result["commit"]
        return (
            f"✅ File {action} successfully!\n"
            f"   File: {file_path}\n"
            f"   Repo: {GITHUB_OWNER}/{repo_name}\n"
            f"   Branch: {branch}\n"
            f"   Commit: {commit.sha[:7]} — {commit_message}\n"
            f"   URL: {repo.html_url}/blob/{branch}/{file_path}"
        )
    except Exception as e:
        return f"❌ Error pushing file: {str(e)}"


@mcp.tool
def create_branch(
    repo_name: str,
    branch_name: str,
    from_branch: str = "main"
) -> str:
    """
    Create a new branch in a repository.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true

    Args:
        repo_name: Target repository
        branch_name: New branch name (e.g., 'feature/add-login')
        from_branch: Base branch to create from (default: main)

    Example:
        create_branch("my-repo", "feature/new-feature")
    """
    guard = _write_guard()
    if guard:
        return guard

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")

        # Get SHA of base branch
        base = repo.get_branch(from_branch)
        repo.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=base.commit.sha
        )
        return (
            f"✅ Branch created!\n"
            f"   Branch: {branch_name}\n"
            f"   From: {from_branch} ({base.commit.sha[:7]})\n"
            f"   Repo: {GITHUB_OWNER}/{repo_name}"
        )
    except Exception as e:
        return f"❌ Error creating branch: {str(e)}"


@mcp.tool
def create_pull_request(
    repo_name: str,
    title: str,
    body: str,
    head_branch: str,
    base_branch: str = "main"
) -> str:
    """
    Create a Pull Request for review before merging changes.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true
    ✅ SAFE — PR requires human approval before merge.

    Args:
        repo_name: Target repository
        title: PR title (keep under 70 chars)
        body: PR description — explain what changed and why
        head_branch: Branch with your changes
        base_branch: Target branch to merge into (default: main)

    Example:
        create_pull_request("my-repo", "Add login feature", "Adds OAuth login", "feature/login")
    """
    guard = _write_guard()
    if guard:
        return guard

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head_branch,
            base=base_branch
        )
        return (
            f"✅ Pull Request created!\n"
            f"   PR #{pr.number}: {pr.title}\n"
            f"   {head_branch} → {base_branch}\n"
            f"   Status: OPEN — awaiting review\n"
            f"   URL: {pr.html_url}\n\n"
            f"⏳ Changes are NOT merged yet. A human must approve and merge the PR."
        )
    except Exception as e:
        return f"❌ Error creating PR: {str(e)}"


@mcp.tool
def get_pull_request_details(repo_name: str, pr_number: int) -> str:
    """
    Get full details of a PR including review status and approvals.

    Args:
        repo_name: Repository name
        pr_number: PR number
    """
    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        pr = repo.get_pull(pr_number)
        reviews = list(pr.get_reviews())

        approved = [r for r in reviews if r.state == "APPROVED"]
        changes_requested = [r for r in reviews if r.state == "CHANGES_REQUESTED"]

        return (
            f"PR #{pr.number}: {pr.title}\n"
            f"  Status: {pr.state.upper()}\n"
            f"  Branch: {pr.head.ref} → {pr.base.ref}\n"
            f"  Author: {pr.user.login}\n"
            f"  Mergeable: {pr.mergeable}\n"
            f"  Approvals: {len(approved)} ✅\n"
            f"  Changes requested: {len(changes_requested)} ❌\n"
            f"  Reviews: {len(reviews)} total\n"
            f"  URL: {pr.html_url}"
        )
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool
def merge_pull_request(
    repo_name: str,
    pr_number: int,
    merge_message: str = "",
    method: str = "squash"
) -> str:
    """
    Merge an approved Pull Request.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true
    ⚠️ APPROVAL REQUIRED — Only merge after human review is complete.

    Args:
        repo_name: Repository name
        pr_number: PR number to merge
        merge_message: Optional merge commit message
        method: 'squash' (clean history), 'merge' (keeps all commits), 'rebase'

    Example:
        merge_pull_request("my-repo", 5, method="squash")
    """
    guard = _write_guard()
    if guard:
        return guard

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        pr = repo.get_pull(pr_number)

        # Check PR is approved
        reviews = list(pr.get_reviews())
        approved = [r for r in reviews if r.state == "APPROVED"]

        if not approved:
            return (
                f"⛔ PR #{pr_number} has no approvals yet!\n"
                f"   Current reviews: {len(reviews)}\n"
                f"   Approvals needed before merge.\n"
                f"   Get approval first, then call merge_pull_request again."
            )

        if pr.state != "open":
            return f"⛔ PR #{pr_number} is already {pr.state} — cannot merge."

        result = pr.merge(
            commit_message=merge_message or f"Merge PR #{pr_number}: {pr.title}",
            merge_method=method
        )
        return (
            f"✅ PR #{pr_number} merged successfully!\n"
            f"   Method: {method}\n"
            f"   SHA: {result.sha}\n"
            f"   Message: {result.message}"
        )
    except Exception as e:
        return f"❌ Error merging PR: {str(e)}"


@mcp.tool
def delete_repo(repo_name: str, confirm: str = "") -> str:
    """
    Delete a GitHub repository permanently.

    ⚠️ WRITE OPERATION — requires GITHUB_ALLOW_WRITES=true
    ⚠️ DESTRUCTIVE — Cannot be undone!

    Args:
        repo_name: Repository to delete
        confirm: Must pass "DELETE" to confirm deletion

    Example:
        delete_repo("test-dummy", confirm="DELETE")
    """
    guard = _write_guard()
    if guard:
        return guard

    if confirm != "DELETE":
        return (
            f"⛔ Deletion not confirmed.\n"
            f"   To delete '{repo_name}', pass confirm='DELETE'\n"
            f"   This action is PERMANENT and cannot be undone."
        )

    try:
        from github import Github
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(f"{GITHUB_OWNER}/{repo_name}")
        repo_url = repo.html_url
        repo.delete()
        return f"✅ Repository '{GITHUB_OWNER}/{repo_name}' deleted.\n   URL was: {repo_url}"
    except Exception as e:
        return f"❌ Error deleting repo: {str(e)}"
