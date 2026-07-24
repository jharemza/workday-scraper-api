# Release Playbook

This playbook describes the release flow used by `.github/workflows/release.yml` and the recovery steps operators should follow when Git tags, `CHANGELOG.md`, and GitHub Releases are out of sync.

## Release trigger model

Releases are tag-driven. A release starts when either:

- a `vMAJOR.MINOR.PATCH` tag is pushed to GitHub, such as `v0.6.0`; or
- an operator runs the `Release Changelog` workflow manually and supplies an existing `vMAJOR.MINOR.PATCH` tag.

The workflow does not infer a release version from `pyproject.toml`, branch names, commit messages, or the latest changelog heading. Tags are the authoritative source of release identity.

## Normal release flow

1. Confirm `main` contains the commits intended for release and that CI is green.
2. Choose the next semantic version tag, for example `v0.6.0`.
3. Create the tag from the intended commit and push it:

   ```bash
   git checkout main
   git pull --ff-only
   git tag v0.6.0
   git push origin v0.6.0
   ```

4. GitHub Actions runs `Release Changelog` for the pushed tag.
5. The workflow checks out `main`, validates the tag format, verifies the tag exists on `origin`, and fetches that tag.
6. If `CHANGELOG.md` already has a section for the tag, the workflow reuses that section. Otherwise, it runs `git-changelog`, commits the generated changelog update to `main`, and pushes it.
7. The workflow writes the tag-specific changelog section to `LATEST_CHANGELOG.md`.
8. If a GitHub Release for the tag already exists, the workflow skips creation. Otherwise, it creates a GitHub Release titled `Release vMAJOR.MINOR.PATCH` with `LATEST_CHANGELOG.md` as the release notes.

## Expected artifacts

A completed release should have these artifacts aligned on the same version:

- a Git tag on GitHub named `vMAJOR.MINOR.PATCH`;
- a `CHANGELOG.md` section headed by that tag;
- a GitHub Release attached to that tag; and
- when the changelog was newly generated, a `docs: update changelog for vMAJOR.MINOR.PATCH` commit on `main`.

## Recovery playbook

Use the manual `workflow_dispatch` path for recovery. Always identify the intended release tag first, then make the repository state match that tag before rerunning the workflow.

### Tag exists, changelog section exists, GitHub Release is missing

1. Open **Actions** → **Release Changelog** → **Run workflow**.
2. Enter the existing tag, for example `v0.6.0`.
3. Run the workflow. It will reuse the existing changelog section and create the missing GitHub Release.

### Tag exists, GitHub Release exists, changelog section is missing

1. Run the release workflow manually with the existing tag.
2. The workflow will run `git-changelog`, commit the missing changelog entry to `main`, and skip release creation because the GitHub Release already exists.
3. If the generated notes differ from the existing release notes, update the GitHub Release notes manually to match the committed changelog section.

### Changelog section exists, tag is missing

1. Verify that the changelog section represents a real release that should exist.
2. Create the missing tag on the intended commit and push it:

   ```bash
   git tag v0.6.0 <commit-sha>
   git push origin v0.6.0
   ```

3. The tag push should trigger the release workflow. If it does not, run the workflow manually with the same tag.

### Tag points to the wrong commit

Do not move a published tag unless maintainers agree that rewriting release history is acceptable.

- If the release was not consumed externally, delete and recreate the tag on the intended commit, then rerun the workflow manually.
- If the release was consumed externally, create a new patch release tag instead and document the correction in `CHANGELOG.md`.

### Workflow fails before creating a GitHub Release

1. Inspect the failed step in the workflow logs.
2. Fix the repository state described by the error, such as a malformed tag or missing tag on `origin`.
3. Rerun the workflow manually with the same existing tag.

## Operator checks

Use these checks when validating a release:

```bash
git fetch --tags origin
git tag --list 'v*.*.*' --sort=-version:refname | head
grep -n '^## \[v0.6.0\]' CHANGELOG.md
```

Then confirm the matching GitHub Release exists in the repository Releases page.
