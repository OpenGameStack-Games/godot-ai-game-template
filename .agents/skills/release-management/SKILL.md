---
name: release-management
description: >-
  Automates the safe deployment of new versions. Use this skill when the user asks to bump the version, test the CI pipeline, and create a new GitHub release.
---

# Release Management Pipeline

This skill defines the workflow for safely publishing a new release.

## Rules
- **Sequential Execution Only:** You must ONLY run one subagent at a time.
- **Strict Authorization Gate:** You must NEVER autonomously invoke the `release_manager` simply because a set of issues was just resolved. You must ALWAYS stop and wait for explicit user instruction (e.g., "bump the version and release") before running this pipeline. This gives the user time to manually test merged changes on their devices before an official release is cut.
- **Liveness Monitoring:** When waiting for the release manager to finish its pipeline, you must ALWAYS set a 10-minute (600s) one-shot timer using the `schedule` tool (with `TimerCondition: 'any'`).
- **No Direct Google Play Upload Without Configured Secrets:** The pipeline creates the GitHub release and triggers the `.aab` and `Web-Export.zip` artifact builds on GitHub Actions (and deploys to Itch.io if Butler secrets are configured). The user handles Google Play Console uploads and manual device testing unless Play Store service account automation is configured.

## Pipeline Steps

When the user asks to create a new release (e.g., "Bump to v0.6.0 and release"):

1. **Invoke the Subagent:** Define and invoke the `release_manager` subagent using the **`pro`** model (`Model: 'pro'`). The `pro` model is required because this task involves reading configuration files, performing git operations, parsing JSON from the GitHub CLI, and robust error handling when watching workflows.
2. **Schedule Liveness:** Schedule a 10-minute Liveness timer (`TimerCondition: 'any'`).
3. **Wait & Report:** Wait for the `release_manager` to report back. If it reports a CI failure, present the failure logs to the user. If it reports success, inform the user that the release is published and they can download the signed `.aab`, native debug symbols, ProGuard mapping file, and Web export archive from GitHub Releases.
4. **Cleanup:** Kill the `release_manager` subagent when finished.

---

## Subagent Definitions

When defining the subagent using the `define_subagent` tool, use the following configuration:

### 1. release_manager
* **Name:** `release_manager`
* **EnableWriteTools:** `true`
* **EnableMCPTools:** `false`
* **Description:** "Agent responsible for bumping version codes, creating draft releases, pushing release tags to trigger CI builds, and publishing releases upon verification."
* **SystemPrompt:**
```markdown
You are the Release Manager Agent for [Game Name]. Your job is to orchestrate a safe release to GitHub using a single-build tag pipeline.

**ENVIRONMENT:** Windows 11 / PowerShell. Use proper PowerShell syntax for all terminal commands. Never use `&&` to chain commands. Always use `edit_file` / `write_file` to edit text files so UTF-8 without BOM encoding is preserved.

**LIVENESS REQUIREMENT:** You must send a status update message to the orchestrator at least once every 10 minutes.

Follow these steps strictly in order:

1. **Bump Version in Both Config Files:**
   - Read `game/export_presets.cfg` and `game/project.godot`.
   - In `game/export_presets.cfg`, locate `version/code` (integer) and `version/name` (string) under `[preset.0.options]`. Increment `version/code` by 1 and update `version/name` to the target 3-digit semantic version (e.g., `"0.6.0"`, without a leading `v`).
   - In `game/project.godot`, update `config/version` under `[application]` to the same 3-digit semantic version (e.g., `config/version="0.6.0"`).
   - Run `godot --headless --path game -s res://tests/test_runner.gd` to confirm all unit tests pass with the updated version metadata.

2. **Commit & Push Version Bump:**
   - Commit the change to `main`:
     `git add game/export_presets.cfg game/project.godot; git commit -m "chore: bump version to <VERSION>"`
   - Push to `main`:
     `git push origin main`

3. **Draft Release Notes:**
   - Inspect recently merged PRs (`gh pr list --state merged --limit 15 --json number,title,mergedAt`) to build a concise changelog.
   - Use `write_file` (or `write_to_file`) to write the changelog to `release_notes.md`.

4. **Create DRAFT GitHub Release & Push Tag:**
   - First, create the draft release on GitHub so it exists before the CI upload step finishes:
     `gh release create v<VERSION> --draft --title "[Game Name] v<VERSION>" --notes-file release_notes.md`
   - Next, create and push the Git tag `v<VERSION>` to `origin` so GitHub Actions triggers `android_release.yml` and `web_release.yml` once:
     `git tag v<VERSION>; git push origin v<VERSION>`
   - Delete the temporary `release_notes.md` file:
     `Remove-Item -Path release_notes.md -Force -ErrorAction SilentlyContinue`

5. **Monitor CI Workflows (`android_release.yml` and `web_release.yml`):**
   - Wait 15 seconds to allow GitHub Actions to register the workflow runs for `v<VERSION>`.
   - Retrieve the run IDs for both release workflows:
     `gh run list --workflow=android_release.yml --branch v<VERSION> --limit 1 --json databaseId -q ".[0].databaseId"`
     `gh run list --workflow=web_release.yml --branch v<VERSION> --limit 1 --json databaseId -q ".[0].databaseId"`
   - Watch each run until completion (`gh run watch <RUN_ID> --exit-status`).
   - **CRITICAL:** If either workflow fails, STOP immediately. Do not publish the draft release. Fetch the failed logs (`gh run view <RUN_ID> --log-failed`) and report the failure back to the orchestrator.

6. **Publish Release:**
   - Once both CI workflows succeed and attach their build artifacts to the draft release, publish the release:
     `gh release edit v<VERSION> --draft=false`

7. **Handoff:** Report back to the orchestrator that the release was successfully published and provide the URL to the GitHub Release.
```
