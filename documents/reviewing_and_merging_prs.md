# Pull Request Review, Documentation & Merge Standards

This document establishes the official standards and workflow for reviewing, documenting, and merging Pull Requests in the **[Game Name]** repository—whether handled by a human developer or an autonomous agent.

---

## 1. Role Overview & Responsibilities

The **PR Reviewer & Documentation Agent** acts as the quality gatekeeper and documentation steward for the repository.

### Primary Responsibilities
1. **Review Diff & Context:** Inspect the Pull Request description, code diff, and automated test results provided by the Issue Resolver.
2. **Verify Acceptance Criteria:** Confirm that all criteria in the linked issue are satisfied.
3. **Visual QA & Asset Verification:** Verify UI changes using MCP visual QA (`mcp_client.py screenshot`) and verify that all referenced asset paths exist on disk.
4. **Synchronize Documentation:** Update `documents/requirements.md`, `documents/manual_testing.md`, and `README.md` to keep all project documentation strictly aligned with code changes.
5. **Merge to Main:** Perform a standard Git merge commit (preserving full history) and delete the remote feature branch.
6. **Workspace Cleanup:** Pull latest `main` into the repository, register assets, and clean up any local worktrees.

---

## 2. Review Checklist

Before approving or merging any Pull Request, verify the following:

### 1. Pre-Review & Dependency Check
* [ ] **Dependencies Resolved:** If the linked issue or PR mentions `Depends on #<number>`, confirm that all dependency issues are `CLOSED` and their PRs are already merged into `main`.
* [ ] **Reviewer Handoff Notes:** Check the PR description's **"Handoff for PR Reviewer & Documentation Agent"** section for specific documentation and testing notes provided by the resolver.

### 2. Code Quality & Standards
* [ ] **Static Typing:** GDScript code strictly uses static typing for all variables, function arguments, and return types.
* [ ] **Naming Conventions:** Classes/Nodes use `PascalCase`; functions/variables/signals use `snake_case`; constants use `UPPER_SNAKE_CASE`.
* [ ] **Logging:** No raw `print()` statements. Uses `print_debug()`, `push_warning()`, or `push_error()`.
* [ ] **Comments:** Explains the *why*, not the obvious *what*.
* [ ] **Asset Verification:** Any file paths referenced in configuration files (like `export_presets.cfg` or `project.godot`) or dynamically constructed in GDScript must actually exist on disk.

### 3. Testing Verification
* [ ] **Automated Test Report:** PR body includes evidence that all automated tests pass (`Test Results: X Passed, 0 Failed`).
* [ ] **Independent Test Execution:** Reviewer independently runs the test suite on the checked-out branch and confirms zero failures.
* [ ] **New Tests Added:** If core logic, autoloads, or calculations were altered, corresponding unit tests are present in `game/tests/`.
* [ ] **Visual QA (MCP Bridge):** If the PR modifies UI or visual layout, launch the game locally and capture a screenshot via `python mcp_client.py screenshot` to verify the layout visually.

---

## 3. PR Inspection & Local Testing Protocol

All review operations—inspecting code, running automated tests, and committing documentation updates—should take place within an isolated Git worktree under `.worktrees/`.

### 1. View PR Overview & Diff
Inspect the PR description and diff via the GitHub CLI:

> [!WARNING]
> **NEVER run a bare `gh pr view <pr_number>` command.** The repository's token configuration will trigger a `read:project` scope error for the bare command. You must ALWAYS use the `--json` flag:

```powershell
gh pr view <pr_number> --json title,body,state,baseRefName,headRefName,commits,files
gh pr diff <pr_number>
```

### 2. Access or Create the Review Worktree
Determine whether a local worktree for this feature branch already exists:
* **If the worktree already exists locally** (e.g., at `.worktrees/issue-<number>`):
  Perform review, testing, and documentation commits directly inside that worktree directory.
* **If the worktree does not exist locally**:
  Fetch the branch and create a dedicated review worktree:
  ```powershell
  git fetch origin
  git worktree add .worktrees/review-pr-<pr_number> feature/issue-<number>-<short-description>
  ```

### 3. Run Automated Tests Locally
Inside the feature worktree, run the headless Godot test suite. Always force an asset import pass first to cache any newly added binary files:
```powershell
godot --headless --editor --quit --path game
godot --headless --path game -s res://tests/test_runner.gd
```

---

## 4. Documentation Coordination (Mandatory Prior to Merge)

The reviewing agent is directly responsible for synchronizing project documentation with code changes.

### 1. `documents/requirements.md`
* Update existing requirement specifications or add new requirement IDs if functionality, constraints, or colors changed.

### 2. `documents/manual_testing.md`
* Add or update test scenarios to provide human testers and QA agents with reproduction and validation steps for the new functionality.

### 3. `README.md`
* Update if user-facing behavior, controls, rules, or visuals are changed.

### Committing Documentation Updates
Always commit documentation updates directly to the feature branch **prior to merging**:
```powershell
git commit -m "docs: update requirements and manual testing for issue #<number>"
git push origin feature/issue-<number>-<short-description>
```

---

## 5. Review Decisions & Protocol

### Scenario A: Changes Required
If the PR violates static typing, includes raw `print()` statements, lacks necessary test cases, fails the test suite, or does not meet the linked issue's acceptance criteria, **do not merge**. Submit a review requesting changes:
```powershell
gh pr review <pr_number> --request-changes --body "<Detailed description of what needs to be fixed>"
```

### Scenario B: Approved & Ready to Merge
Once all acceptance criteria are met, automated tests pass, and documentation is updated and pushed to the feature branch, proceed to merge.

#### 1. Prepare for Merge
Before merging, exit the review worktree, terminate any background Godot processes to prevent Windows file locks, remove the worktree, and return to the main workspace:
```powershell
# Kill any background Godot instances to release Windows file locks
Stop-Process -Name "godot" -Force -ErrorAction SilentlyContinue

# Exit worktree and remove it
cd ../..
git worktree remove .worktrees/review-pr-<pr_number> --force
```

#### 2. Merge the Pull Request
Merge using the GitHub CLI with a **standard merge commit** (preserving complete Git history):
```powershell
gh pr merge <pr_number> --merge --delete-branch
```
> [!IMPORTANT]
> **DO NOT squash** (`--squash`) or rebase (`--rebase`). Standard merge commits (`--merge`) preserve the detailed history of atomic commits in the repository.

#### 3. Verify Issue Closure
Confirm that the linked issue (`Resolves #<number>`) has transitioned to `CLOSED`. If GitHub did not automatically close the issue:
```powershell
gh issue close <issue_number> --comment "Resolved via PR #<pr_number>."
```

#### 4. Local Repository Synchronization & Asset Re-registration
From the main project directory:
```powershell
# Prune worktree metadata
git worktree prune

# Ensure main is up to date with the newly merged PR
git checkout main
git pull origin main

# Delete local branch if lingering
git branch -d feature/issue-<number>-<short-description> -ErrorAction SilentlyContinue

# Force an editor import pass to register newly merged classes and assets
godot --headless --editor --quit --path game
```
