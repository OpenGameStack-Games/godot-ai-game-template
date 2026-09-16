# Issue Resolution Workflow & Standards

This document establishes the official standards, Git worktree workflow, and coding guidelines for anyone resolving issues in the **[Game Name]** repositoryâ€”whether human contributor or autonomous agent.

---

## 1. Role Overview & Core Boundaries

The **Issue Resolver** is responsible for taking an open issue from conception to an unmerged, thoroughly tested, and documented Pull Request.

### Primary Responsibilities
1. **Triage & Select:** Identify the next unblocked issue based on issue number and dependencies.
2. **Worktree Isolation:** Create and work within an isolated Git worktree under `.worktrees/`.
3. **Implement:** Write clean, modular, and statically typed GDScript code meeting all acceptance criteria.
4. **Test:** Run the automated test suite and add new automated tests in `game/tests/` verifying the change.
5. **Detailed Pull Request:** Push the feature branch and submit a highly detailed PR against `main`.

### Explicit Boundaries (What the Issue Resolver Does NOT Do)
* **DO NOT merge into `main`:** The Issue Resolver must never merge the PR or push directly to `main`.
* **DO NOT update project documentation:** Updating `documents/requirements.md`, `documents/manual_testing.md`, or `README.md` is handled by the **PR Reviewer & Documentation Agent**. The resolver provides the necessary handoff details in the PR body so the reviewing agent can update documentation accurately.

---

## 2. Issue Discovery & Triage Protocol

When tasked with resolving an issue, follow this triage procedure:

### 1. Inspect Open Issues
List open issues via the GitHub CLI:
```powershell
gh issue list --state open
```

Inspect the issue details using JSON output (to avoid scope permission requirements):
```powershell
gh issue view <issue_number> --json title,body,state,labels,assignees
```

### 2. Dependency Checking (`Depends on #X`)
* Read the issue description carefully.
* If the issue header contains **`Depends on #<number>`**, check the status of the dependency:
  ```powershell
  gh issue view <dependency_number> --json state
  ```
* If the dependency issue is still `OPEN`, **do not begin work on this issue**. Move to the next unblocked issue or report the blocker.
* Only begin work if all dependencies are `CLOSED` and their pull requests merged into `main`.

### 3. Issue Selection Strategy
Unless instructed to work on a specific issue:
1. Select the lowest-numbered open issue that has no open dependencies.
2. If multiple issues are ready, prioritize bugs and foundational features (`core`, `autoloads`) before downstream UI enhancements.

---

## 3. Git Worktree & Branching Workflow

All work must occur inside an isolated worktree to keep the primary working tree clean.

### 1. Ensure `main` is Synchronized
```powershell
git checkout main
git pull origin main
```

### 2. Create the Worktree
Create a new feature branch and isolated worktree inside `.worktrees/`:
```powershell
git worktree add .worktrees/issue-<number> -b feature/issue-<number>-<short-description>
```
*Example:*
```powershell
git worktree add .worktrees/issue-21 -b feature/issue-21-absent-color-red
```

### 3. Commit Guidelines
* Follow [Conventional Commits](https://www.conventionalcommits.org/):
  * `feat: <description>` for new features
  * `fix: <description>` for bug fixes
  * `test: <description>` for test additions
  * `refactor: <description>` for code restructuring
* Keep commits atomic, well-described, and focused on the issue.

---

## 4. Coding & Architecture Standards

### Godot 4.x & GDScript Standards
1. **Static Typing Everywhere:**
   * Always annotate variable types and function returns:
     ```gdscript
     var current_row: int = 0
     var secret_word: String = ""
     func evaluate_guess(guess: String) -> Array[int]:
     ```
2. **Naming Conventions:**
   * **Classes & Nodes:** `PascalCase` (e.g., `GameBoard`, `KeyboardKey`)
   * **Variables & Functions:** `snake_case` (e.g., `current_guess`, `_on_tile_pressed()`)
   * **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_ATTEMPTS = 6`, `COLOR_BG_ABSENT`)
   * **Signals:** `snake_case` in past tense or action oriented (e.g., `letter_submitted`, `row_completed`)
3. **Commenting & Documentation:**
   * Do not write redundant comments stating the obvious.
   * Document the *intent*, *assumptions*, or mathematical/algorithmic logic.
   * Every autoload and major script must contain a header docstring explaining its domain responsibility.

---

## 5. Logging Standards

Avoid raw `print()` statements in production code. Use categorized, engine-native logging:
* `print_debug(...)`: Diagnostic info and state transitions (e.g., `print_debug("GameManager: Started game in mode %s" % mode_name)`).
* `push_warning(...)`: Non-fatal issues or recoverable conditions (e.g., `push_warning("SaveManager: Corrupted save file detected, resetting.")`).
* `push_error(...)`: Critical logic failures or invariant violations.

---

## 6. Automated Testing Standards

Every feature or bug fix touching game logic or autoloads must be backed by automated tests.

### Test Architecture
* Tests are located in `game/tests/`.
* Test scripts inherit from `res://tests/test_base.gd`.
* Every test method starts with `test_`.
* Assertions use `assert_true()`, `assert_false()`, `assert_eq()`, and `assert_ne()`.

### Running Automated Tests
Run the headless Godot test suite. First, force an asset import pass to cache any newly added binary files (like PNG icons):
```powershell
godot --headless --editor --quit --path game
godot --headless --path game -s res://tests/test_runner.gd
```
*(Note: This requires the Godot executable directory to be in your system's PATH, and the executable to be named `godot` or `godot.exe`/`godot.bat`).*

### Verification Gate
* **Zero Failures:** All existing and newly created tests must pass (`Test Results: X Passed, 0 Failed`, exit code 0).
* If any test fails, resolve the regression before pushing.

---

## 7. Submitting the Pull Request

Once the fix is implemented and verified:

### 1. Push Feature Branch
```powershell
git push -u origin feature/issue-<number>-<short-description>
```

### 2. Create the Pull Request
Submit the PR targeting `main` using GitHub CLI. The PR body must follow the **Highly Detailed Pull Request Standard** (pre-populated automatically from `.github/pull_request_template.md`) so that the PR Reviewer & Documentation Agent has all the required context.

```powershell
gh pr create --title "<type>: <concise description> (Resolves #<number>)" --body "$pr_body" --base main
```

### Required PR Body Structure
Every PR submitted by an Issue Resolver must include:
1. **Closes / Resolves Link:** `Resolves #<number>`
2. **Problem & Context:** Summary of the issue being addressed and root cause.
3. **Key Changes & Technical Scope:** Detailed breakdown of modified, added, or deleted files with architectural rationale.
4. **Automated Test Results:** Test execution output confirming pass count and new test methods introduced.
5. **Handoff for PR Reviewer & Documentation Agent:**
   * Specific recommendations on which sections of `documents/requirements.md` need updates.
   * Recommended manual test cases for `documents/manual_testing.md`.
   * Any `README.md` updates if player-facing UI/mechanics changed.

### 3. Stop and Stand Down
After opening the PR:
* **Do not merge the pull request.**
* **Do not delete the worktree yet** (it can be kept until the PR is merged by the reviewer agent, or cleaned up once the PR branch is confirmed safely on remote).
* Report the PR URL and summary back to the user.

