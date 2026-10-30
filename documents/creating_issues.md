# GitHub Issue Creation Standard & Guidelines

This document outlines the standard specifications, structure, and workflow for creating GitHub issues for the **[Game Name]** project. Adhering to these standards ensures that any contributor, whether a human developer or an autonomous agent, can pick up an issue, understand the context and requirements without ambiguity, implement the change, and properly verify their work.

---

## 1. Principles & Quality Bar

Every issue created in this repository must meet the following criteria:
1. **Self-Contained & Actionable:** Provide all necessary context, architectural decisions, and acceptance criteria. A contributor should never have to guess design intent or look for unlinked resources.
2. **Clear Boundaries:** Group requirements logically by affected components (e.g., UI, Core Logic, AutoLoads, Tests, Documentation).
3. **Traceability:** Explicitly list any dependencies and note which documentation files need to be synchronized as part of the implementation.
4. **No Duplicates:** Always search open and closed issues (`gh issue list --state all`) before submitting a new issue.

---

## 2. Standard Issue Structure

All issues filed in [Game Name] must follow this standardized layout. When creating an issue on GitHub, use one of the predefined templates in `.github/ISSUE_TEMPLATE/`:
* **Bug Report (`.github/ISSUE_TEMPLATE/bug_report.md`):** For defects, unexpected behavior, logic bugs, or UI glitches. Pre-labeled with `bug`.
* **Feature Request (`.github/ISSUE_TEMPLATE/feature_request.md`):** For new gameplay mechanics, visual enhancements, or architectural improvements. Pre-labeled with `enhancement`.

Both templates implement the following required markdown structure:

```markdown
**Depends on #<issue_number>** (Include only if this issue has blockers)

### 1. Problem & Context
A concise explanation of the problem, bug, or feature request.
- For bugs: Reproduction steps, observed behavior, and expected behavior.
- For features/enhancements: User story, design motivation, and why the change improves the game.

### 2. Technical Scope & Affected Files
Direct references to the files, scenes, or scripts that need modification or inspection:
- `game/scripts/<script_name>.gd`
- `game/scenes/<scene_name>.tscn`
- `game/autoloads/<autoload_name>.gd`
- `game/tests/<test_name>.gd`

### 3. Acceptance Criteria
Checklist grouped by component or responsibility:

#### [Component / Feature Area 1]
- [ ] Explicit requirement 1
- [ ] Explicit requirement 2

#### [Component / Feature Area 2]
- [ ] Explicit requirement 3

#### Automated Tests (`game/tests/`)
- [ ] Add or update unit test cases verifying the new behavior.
- [ ] Ensure all existing automated test suites pass without regressions.

#### Documentation Coordination (Mandatory)
- [ ] Update `documents/requirements.md` to reflect any new or modified specifications.
- [ ] Update `documents/manual_testing.md` with new/updated manual verification test cases.
- [ ] Update `README.md` if user-facing behavior, controls, or visuals are altered.
```

---

## 3. Title & Labeling Conventions

### Title Format
Titles must be concise and use standard prefixes to indicate the area of the codebase:
- `UI - <Action/Description>` (e.g., `UI - Add Safe-Area Top Margin to Main Menu Header`)
- `Core - <Action/Description>` (e.g., `Core - Implement Deterministic Turn State Machine`)
- `Data - <Action/Description>` (e.g., `Data - Persist Player Settings in user://settings.cfg`)
- `Docs - <Action/Description>` (e.g., `Docs - Document Scene Hierarchy in Requirements`)

Conventional commits format (`feat:`, `fix:`, `refactor:`, `docs:`) is also acceptable.

### Labels
Apply at least one standard GitHub label when creating the issue:
- `enhancement`: New features, visual improvements, or gameplay enhancements.
- `bug`: Defects, incorrect logic, UI glitches, or broken mechanics.
- `documentation`: Purely documentation-focused tasks.
- `good first issue`: Self-contained, straightforward tasks suitable for beginners.

---

## 4. Pre-Creation Checklist (For Authors & Agents)

Before publishing an issue via GitHub:
1. [ ] **Search Existing Issues:** Run `gh issue list --state all` to confirm the issue does not already exist or duplicate past work.
2. [ ] **Inspect Codebase:** Verify the exact file paths, variable names, and current behavior in the code.
3. [ ] **Clarify Design Choices:** Resolve any open design questions (e.g., color hex codes, UI behaviors, platform fallbacks) before publishing so the issue body contains firm decisions rather than open questions.
4. [ ] **Web/HTML5 Font & Symbol Guardrails:** If the issue introduces custom fonts, themes, or Unicode symbols/icons (`☰`, `✕`, `▸`, `▾`, `★`, `↺`, `↻`, `⌫`, `▶`, `→`) in UI controls, include acceptance criteria requiring `res://assets/fonts/NotoSansSymbols-Regular.ttf` and `res://assets/fonts/DejaVuSans.ttf` in the font's `fallbacks` array and unit tests asserting `font.has_char(ord(ch))` (since Web/HTML5 WASM builds cannot access host OS system fonts).
5. [ ] **Include Documentation Acceptance Criteria:** Ensure the mandatory documentation coordination checklist is included per [`documents/reviewing_and_merging_prs.md`](reviewing_and_merging_prs.md).

---

## 5. Creating Issues via GitHub CLI

Contributors and agents can create issues directly from the command line using the GitHub CLI (`gh`).

### Option A: Using `--body-file` (Recommended for Agents)
Write the formatted markdown body to a temporary file (`issue_body.tmp.md`) using the agent's native `write_file` tool to avoid PowerShell string-escaping issues, then run:
```powershell
gh issue create --title "UI - Add Pause Overlay Modal" --body-file issue_body.tmp.md --label "enhancement"
Remove-Item -Path issue_body.tmp.md -Force -ErrorAction SilentlyContinue
```

### Option B: Scripted Batch Creation
When creating multiple issues in a batch, write all issue bodies and `gh issue create` commands into a single temporary PowerShell script (`tmp_create_issues.ps1`) and run it once so the user only needs to approve a single command execution.

---

## 6. Reference Example

Below is an example of a well-scoped issue meeting all project standards:

```markdown
**Title:** `UI - Add Safe-Area Top Inset Handling to Main Screen Header`
**Labels:** `enhancement`

### 1. Problem & Context
On Android devices with display cutouts (punch-hole cameras or notches), the top header bar can be partially obscured by the system status bar. We need to query `DisplayServer.get_display_safe_area()` at runtime and add the top inset to the root margin container without adding extra padding on desktop or web builds where the inset is zero.

### 2. Technical Scope & Affected Files
- `game/scenes/main.tscn`
- `game/scripts/main_screen.gd`
- `game/tests/test_main_screen.gd`

### 3. Acceptance Criteria

#### Layout & Safe Area Handling
- [ ] Add a `MarginContainer` (`ContentMargin`) with a base `margin_top` of `16` px.
- [ ] Apply safe-area top inset adjustment in `_ready()` and on `NOTIFICATION_RESIZED`.

#### Automated Tests (`game/tests/`)
- [ ] Add unit tests in `game/tests/test_main_screen.gd` verifying base margin values and safe-area offset math.
- [ ] Ensure all existing automated test suites pass with 0 failures.

#### Documentation Coordination (Mandatory per documents/reviewing_and_merging_prs.md)
- [ ] Update `documents/requirements.md` under Section 2 (Visuals and Layout).
- [ ] Update `documents/manual_testing.md` with cutout/safe-area verification steps.
```
