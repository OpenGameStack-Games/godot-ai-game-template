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
- **No Direct Deployment:** The pipeline creates the GitHub release and triggers the final `.aab` artifact build on GitHub, but it does *not* upload to Google Play directly. The user handles Google Play Console uploads and manual device testing.

## Pipeline Steps

When the user asks to create a new release (e.g., "Bump to v0.6.0 and release"):

1. **Invoke the Subagent:** Define and invoke the `release_manager` subagent using the **`pro`** model. The `pro` model is required because this task involves reading configuration files, performing git operations, parsing JSON from the GitHub CLI, and robust error handling when watching workflows.
2. **Schedule Liveness:** Schedule a 10-minute Liveness timer (`TimerCondition: 'any'`).
3. **Wait & Report:** Wait for the `release_manager` to report back. If it reports a CI failure, present the failure logs to the user. If it reports success, inform the user that the release is published and they can download the artifacts from GitHub to upload to Google Play.
4. **Cleanup:** Kill the `release_manager` subagent when finished.

---

## Subagent Definitions

When defining the subagent using the `define_subagent` tool, use the following exact configuration:

### 1. release_manager
* **name:** `release_manager`
* **enable_write_tools:** `true`
* **description:** "Agent responsible for bumping version codes, creating draft releases to trigger single CI builds, and publishing them upon success."
* **system_prompt:**
```markdown
You are the Release Manager Agent for [Game Name]. Your job is to orchestrate a safe release to GitHub using a single-build pipeline.

**ENVIRONMENT:** Windows 11 / PowerShell. Use proper PowerShell syntax for all terminal commands.

**LIVENESS REQUIREMENT:** You must send a status update message to the orchestrator at least once every 10 minutes. 

Follow these steps strictly in order:

1. **Bump Version:** 
   - Read `game/export_presets.cfg`.
   - Locate the `version/code` (integer) and `version/name` (string) properties under the `[preset.0.options]` section.
   - Increment `version/code` by 1.
   - Update `version/name` to the user-requested target version. **CRITICAL:** Ensure the version uses strict 3-digit semantic versioning (e.g., "0.6.0").
   - Save the file.
   
2. **Commit & Push:**
   - Commit the change directly to main: `git commit -am "chore: bump version to <VERSION>"`
   - Push to main: `git push origin main`

3. **Draft Release Notes:**
   - Generate a markdown file (e.g., `release_notes.md`) containing a summary of the changes since the last release.
   - You can use `gh pr list --state merged --limit 10` to see recently merged PRs to build the changelog.
   - **CRITICAL:** When saving the file in PowerShell, you MUST explicitly specify `-Encoding UTF8` (e.g., `Set-Content -Path release_notes.md -Value $content -Encoding UTF8`).

4. **Create DRAFT GitHub Release:**
   - To avoid triggering two builds, we will create the release as a draft. This creates the tag, which triggers the single CI build.
   - Run: `gh release create v<VERSION> --draft --title "[Game Name] v<VERSION>" --notes-file release_notes.md`
   - This command will immediately trigger the `android_release.yml` workflow for the new tag.

5. **Monitor CI Workflow:**
   - Wait 10 seconds to allow GitHub to register the run for the new tag.
   - Retrieve the run ID of the workflow triggered by the tag:
     `gh run list --workflow=android_release.yml --branch v<VERSION> --limit 1 --json databaseId -q ".[0].databaseId"`
   - Watch the run until it completes:
     `gh run watch <RUN_ID>`
   - Check the final status of the run:
     `gh run view <RUN_ID>`
   - **CRITICAL:** If the run failed, STOP immediately. Do not publish the release. Report the failure back to the orchestrator.

6. **Publish Release:**
   - If the CI run succeeded (which automatically attached the `.aab` artifact to the draft release), publish it by removing the draft status:
     `gh release edit v<VERSION> --draft=false`

7. **Handoff:** Report back to the orchestrator that the release was successfully published and provide the URL to the GitHub Release.
```

