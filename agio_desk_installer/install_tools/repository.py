import re
import requests
from urllib.parse import urlparse
from packaging.version import Version


def parse_repo_info(repository_url: str):
    """Extract <owner> and <repo> from URL GitHub."""
    parsed = urlparse(repository_url)
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(path_parts) < 2:
        raise ValueError("Invalid github url https://github.com/<owner>/<repo>")
    owner, repo = path_parts[:2]
    repo = repo.removesuffix(".git")
    return owner, repo


def get_release_list(owner: str, repo: str):
    """List of releases"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def filter_semver_tags(releases):
    """
    Filter tags x.y.z
    return [(tag_name, release_data)].
    """
    semver_re = re.compile(r"^\d+\.\d+\.\d+$")
    filtered = []
    for r in releases:
        tag = r.get("tag_name", "")
        if semver_re.match(tag):
            filtered.append((tag, r))
    # sorting by version
    filtered.sort(key=lambda x: Version(x[0]))
    return filtered


def get_latest_release_asset(owner: str, repo: str):
    """Looking for latest release (.whl)"""
    releases = get_release_list(owner, repo)
    semver_releases = filter_semver_tags(releases)
    if not semver_releases:
        raise RuntimeError("Releases not found x.y.z")

    latest_tag, latest_release = semver_releases[-1]

    assets = latest_release.get("assets", [])
    for asset in assets:
        url = asset.get("browser_download_url", "")
        if url.endswith(".whl"):
            return url

    raise RuntimeError(f"Release {latest_tag} has not contains .whl files")


def build_archive_url(owner: str, repo: str, ref_type: str, ref_value: str) -> str:
    """Create URL to zip-archive by link type (commit/tag/branch)."""
    if ref_type == "commit":
        return f"https://github.com/{owner}/{repo}/archive/{ref_value}.zip"
    elif ref_type == "tag":
        return f"https://github.com/{owner}/{repo}/archive/refs/tags/{ref_value}.zip"
    elif ref_type == "branch":
        return f"https://github.com/{owner}/{repo}/archive/refs/heads/{ref_value}.zip"
    else:
        raise ValueError("ref_type must be 'commit', 'tag' or 'branch'")


def package_name_to_agio_band_git_repository_url(package_name: str) -> str:
    return f"https://github.com/agio-band/{package_name.replace('_', '-')}.git"


def get_package_installation_url(repository_url: str, commit: str = None, tag: str = None, branch: str = None) -> str:
    """
    Get installation url (.whl или .zip).
    - latest release
    - by branch name
    - by tag name
    - by commit hash

    # latest release (.whl from releases)
    get_package_installation_url(url)

    # By commit
    get_package_installation_url(url, commit="181ce45e")

    # By tag
    get_package_installation_url(url, tag="r1")

    # By branch
    get_package_installation_url(url, branch="dev")

    """
    if sum([bool(commit), bool(tag), bool(branch)]) > 1:
        raise ValueError("Use only one of argument: commit, tag or branch.")

    owner, repo = parse_repo_info(repository_url)

    if commit:
        return build_archive_url(owner, repo, "commit", commit)
    elif tag:
        return build_archive_url(owner, repo, "tag", tag)
    elif branch:
        return build_archive_url(owner, repo, "branch", branch)
    else:
        return get_latest_release_asset(owner, repo)


