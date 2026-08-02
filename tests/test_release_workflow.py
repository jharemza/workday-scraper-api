from pathlib import Path

import yaml


WORKFLOW_PATH = Path(__file__).parents[1] / ".github" / "workflows" / "release.yml"
REQUIREMENTS_PATH = Path(__file__).parents[1] / "requirements.txt"


def load_release_workflow():
    with WORKFLOW_PATH.open(encoding="utf-8") as workflow_file:
        return yaml.safe_load(workflow_file)


def test_git_changelog_dependency_is_pinned():
    workflow = load_release_workflow()
    pinned_version = workflow["env"]["GIT_CHANGELOG_VERSION"]
    install_step = workflow["jobs"]["update-changelog"]["steps"][3]
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()

    assert pinned_version.count(".") == 2
    assert f"git-changelog=={pinned_version}" in requirements
    assert '"git-changelog==$GIT_CHANGELOG_VERSION"' in install_step["run"]


def test_release_runs_are_serialized_and_not_cancelled():
    workflow = load_release_workflow()

    assert workflow["concurrency"] == {
        "group": "release-changelog",
        "cancel-in-progress": False,
    }


def test_release_creation_verifies_existing_tag():
    workflow = load_release_workflow()
    release_step = workflow["jobs"]["update-changelog"]["steps"][5]

    assert "--verify-tag" in release_step["run"]
    assert "gh release view" in release_step["run"]
