# Issue Resolution Workflow & Standards

This document establishes the official standards, Git worktree workflow, and coding guidelines for anyone resolving issues in the **[Game Name]** repository, whether a human contributor or an autonomous agent.

---

## 0. Operational Rules
* **PowerShell Chaining:** When executing shell commands, NEVER use `&&` to chain commands together (unsupported in Windows PowerShell 5.1). Instead, use `;` or execute commands sequentially in separate tool calls.
* **Stateless Shell Working Directory:** In agentic environments, each shell command call starts in a fresh session at the repository root (`cd` / `Set-Location` does NOT persist across separate tool calls). When operating on a worktree under `.worktrees/issue-<number>`, always pass explicit paths (`git -C .worktrees/issue-<number> ...` and `godot --headless --path .worktrees/issue-<number>/game ...`) or prefix `Set-Location .worktrees/issue-<number>;` inside the same command call.
* **File Generation Encoding:** Generating text files via PowerShell pipes (`>` or PowerShell 5.1 `Set-Content -Encoding UTF8`) adds a UTF-8 BOM (Byte Order Mark) or UTF-16 LE encoding. Godot fails to parse `.tscn`, `.tres`, and `.gd` files that contain a BOM (`Parse Error: Expected '['`). ALWAYS use the native agent file tools (`write_file` / `edit_file`, or legacy `write_to_file` / `replace_file_content`) to create and edit project files cleanly in UTF-8 without BOM.
* **Documentation Redundancy:** Before requesting the PR Reviewer to document a feature or testing steps, always verify whether the specification already exists in `documents/requirements.md` or `documents/manual_testing.md`. Do not duplicate existing specification notes.

---

## 1. Role Overview & Core Boundaries

The **Issue Resolver** is responsible for taking an open issue from conception to an unmerged, thoroughly tested, and documented Pull Request.

### Primary Responsibilities
1. **Triage & Select:** Identify the next unblocked issue based on issue number and dependencies.
2. **Worktree Isolation:** Create and work within an isolated Git worktree under `.worktrees/issue-<number>`.
3. **Implement:** Write clean, modular, and statically typed GDScript code meeting all acceptance criteria.
4. **Test:** Run the automated test suite, perform visual QA via MCP, and add new automated tests in `game/tests/`.
5. **Detailed Pull Request:** Push the feature branch and submit a detailed PR against `main`.

### Explicit Boundaries (What the Issue Resolver Does NOT Do)
* **DO NOT merge into `main`:** The Issue Resolver must never merge the PR or push directly to `main`.
* **DO NOT update project documentation (unless resolving a `Docs` issue):** Updating `documents/requirements.md`, `documents/manual_testing.md`, or `README.md` for feature/bug PRs is handled by the **PR Reviewer & Documentation Agent**. The resolver provides the necessary handoff details in the PR body so the reviewing agent can update documentation accurately.

---

## 2. Issue Discovery & Triage Protocol

When tasked with resolving an issue, follow this triage procedure:

### 1. Inspect Open Issues
List open issues via the GitHub CLI:
```powershell
gh issue list --state open
```

> [!WARNING]
> **NEVER run a bare `gh issue view <id>` command.** The repository's token configuration will trigger a `read:project` scope error for the bare command. You must ALWAYS use the `--json` flag to avoid this error:

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
git worktree add .worktrees/issue-12 -b feature/issue-12-pause-modal
```
When editing files with `write_file` or `edit_file`, target paths inside `.worktrees/issue-<number>/game/...` (not the root `game/...`).

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
   * Always annotate variable types and function returns. This applies equally to production scripts AND unit test files (`tests/*.gd`).
   * Dynamic node lookups (`get_node()`, `get_node_or_null()`) MUST include explicit type annotations and type casting:
     ```gdscript
     var my_label: Label = get_node_or_null("Header/Title") as Label
     ```
2. **Metadata Files (`.uid`):**
   * Godot 4 generates `.uid` metadata files alongside `.gd` scripts, scenes, and assets. Always stage and commit these `.uid` files alongside your changes.
3. **Naming Conventions:**
   * **Classes & Nodes:** `PascalCase` (e.g., `GameBoard`, `ActionButton`)
   * **Variables & Functions:** `snake_case` (e.g., `current_score`, `_on_button_pressed()`)
   * **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_ATTEMPTS = 6`, `DEFAULT_MARGIN_TOP = 16`)
   * **Signals:** `snake_case` in past tense or action oriented (e.g., `turn_completed`, `score_updated`)
4. **UI Design & Responsiveness:**
   * When using `GridContainer`, Godot natively ignores invisible children (`visible = false`), causing remaining nodes to reflow. If you need fixed slot positions, keep nodes visible and clear text or set `modulate.a = 0.0`.
   * Root screen scripts are responsible for explicitly wiring child components to domain models. Verify that methods invoked on child nodes actually exist on those component scripts before calling them.
5. **Web/HTML5 Font Fallbacks & Unicode Symbols:**
   * Browser WASM builds (`Web` export) run inside a sandbox with **no access to host OS system fonts**. While `allow_system_fallback=true` masks missing glyphs on Windows and Android by falling back to system fonts, any unbundled Unicode symbol (`☰`, `✕`, `▸`, `▾`, `★`, `↺`, `↻`, `⌫`, `▶`, `→`) will render as a missing-glyph tofu box (`□`) on Web/Itch.io unless covered by an explicitly bundled fallback `FontFile`.
   * Do **NOT** use a `SystemFont` as the global `default_font` (which alters standard Latin text layout metrics across platforms); always use a `FontVariation` or `FontFile` with explicit `fallbacks` attached (such as the preconfigured `res://resources/default_font.tres`).
   * Whenever a custom `FontFile`, `FontVariation`, or `Theme` is added or overridden on UI controls, `res://assets/fonts/NotoSansSymbols-Regular.ttf` and `res://assets/fonts/DejaVuSans.ttf` **MUST** remain attached to its `fallbacks` array, and `*.ttf` must remain in `include_filter` for all export presets in `game/export_presets.cfg`.
   * Any Unicode symbol used in UI text must be verified in unit tests using `font.has_char(ord(ch))` (or `font.has_char(ch.unicode_at(0))`) against the active theme/control font.
6. **Commenting & Documentation:**
   * Do not write redundant comments stating the obvious.
   * Document the *intent*, *assumptions*, or mathematical/algorithmic logic.
   * Every autoload and major script must contain a header docstring (`##`) explaining its domain responsibility.

---

## 5. Logging Standards

Avoid raw `print()` statements in production code. Use categorized, engine-native logging:
* `print_debug(...)`: Diagnostic info and state transitions (e.g., `print_debug("GameManager: Started game in mode %s" % mode_name)`).
* `push_warning(...)`: Non-fatal issues or recoverable conditions (e.g., `push_warning("SaveManager: Corrupted save file detected, resetting.")`).
* `push_error(...)`: Critical logic failures or invariant violations.

---

## 6. Automated Testing Standards

Every feature or bug fix touching game logic, UI layout, or autoloads must be backed by automated tests.

### Agentic Visual QA (MCP Bridge)
If your issue involves UI layout, coloring, or visual polish, visually verify your changes before submitting the PR (see [`.agents/skills/mcp-visual-qa/SKILL.md`](../.agents/skills/mcp-visual-qa/SKILL.md)):
1. Stop any lingering Godot instances: `Stop-Process -Name "godot" -Force -ErrorAction SilentlyContinue`.
2. Start a fresh instance of the worktree game in the background: `godot --path .worktrees/issue-<number>/game`.
3. In debug mode, this automatically starts the `McpInteractionServer` AutoLoad on `127.0.0.1:9090`.
4. Run `python mcp_client.py ping`, `python mcp_client.py screenshot`, and `python mcp_client.py get_ui_elements` to capture `screenshot.png` and inspect the SceneTree.
5. View `screenshot.png` with `read_file` to verify that your changes look clean and do not clip or overlap.
6. **CRITICAL:** Once visual QA is complete, terminate the background Godot process (`Stop-Process -Name "godot" -Force -ErrorAction SilentlyContinue`) to close the window and release Windows file locks and port `9090`.

### Test Architecture
* Tests are located in `game/tests/`.
* Test scripts inherit from `TestBase` (`res://tests/test_base.gd`).
* Every test method starts with `test_`.
* Optional lifecycle hooks: override `before_each() -> void` and `after_each() -> void` for per-test state setup/reset, and `cleanup() -> void` for suite-level cleanup.
* Assertions provided by `TestBase`:
  * `assert_true()`, `assert_false()`
  * `assert_eq()`, `assert_ne()`
  * `assert_gt()`, `assert_gte()`, `assert_lt()`, `assert_lte()`, `assert_approx()`
  * `assert_null()`, `assert_not_null()`
  * `assert_contains()`, `assert_file_exists()`
* **CRITICAL**: When modifying UI layout or styling, write lightweight structural unit tests verifying component properties (e.g., font sizes, minimum dimensions, custom themes).
* **CRITICAL**: When adding an Autoload, configuring an asset path in `project.godot`/`export_presets.cfg`, or generating resources, assert `assert_file_exists(...)` for that exact path.
* **CRITICAL**: GDScript lambdas capture primitives by VALUE, not by reference. When using inline lambdas to verify signal emissions, capture variables via an `Array` wrapper (e.g., `var count: Array[int] = [0]`) or an object property.
* **CRITICAL**: The `test_runner.gd` does not initialize `project.godot` autoloads as global script identifiers during `_init()`. To ensure testability, avoid hardcoded singleton identifier calls inside core logic classes; use dependency injection, mock nodes, or look up peer singletons dynamically via `/root/SingletonName`.
* **CRITICAL**: When testing `Control` nodes headlessly, `_ready()` is NOT invoked organically unless nodes enter the scene tree. Use `test_root_window.add_child(node)` in your test setup, and clean up immediately with `node.free()` (never `queue_free()`, which leaks objects on headless exit).

### Running Automated Tests
> [!WARNING]
> Testing `DisplayServer` window state methods (like `screen_is_kept_on()`) will fail when running via the headless runner. Guard those assertions using `if DisplayServer.get_name() != "headless":`.

Run the headless Godot test suite against your worktree. Always run an editor import pass first to cache any newly added resources or `class_name` definitions:
```powershell
godot --headless --editor --quit --path .worktrees/issue-<number>/game
godot --headless --path .worktrees/issue-<number>/game -s res://tests/test_runner.gd
```

### Verification Gate
* **Zero Failures:** All existing and newly created tests must pass (`Test Results: X Passed, 0 Failed`, exit code 0).
* Note that `test_runner.gd` fails the suite if any `test_*.gd` script fails to compile or load. Fix any syntax or type errors before pushing.

---

## 7. Submitting the Pull Request

Once the fix is implemented and verified inside `.worktrees/issue-<number>`:

### 1. Stage, Commit, and Push Feature Branch
```powershell
git -C .worktrees/issue-<number> add -A
git -C .worktrees/issue-<number> commit -m "<type>: <concise description>"
git -C .worktrees/issue-<number> push -u origin feature/issue-<number>-<short-description>
```

### 2. Create the Pull Request
Submit the PR targeting `main` using GitHub CLI. Write the PR body to `pr_body.md` using `write_file`, pass `--body-file pr_body.md` to avoid PowerShell string-escaping issues, and then remove `pr_body.md`:

```powershell
gh pr create --title "<type>: <concise description> (Resolves #<number>)" --body-file pr_body.md --base main
Remove-Item -Path pr_body.md -Force -ErrorAction SilentlyContinue
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
* **Keep `.worktrees/issue-<number>` intact** so the PR Reviewer agent can reuse it for testing and documentation commits before cleaning it up during merge.
* Report the PR URL and summary back to the orchestrator or user.
