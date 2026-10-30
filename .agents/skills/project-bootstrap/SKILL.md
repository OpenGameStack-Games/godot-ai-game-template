---
name: project-bootstrap
description: >-
  Use this skill when the user wants to initialize a new game project from this template, rename "[Game Name]" and "com.example.game", set up initial project metadata, or define the initial game requirements.
---

# Project Bootstrap & Template Initialization

Use this skill when turning a fresh clone or template instantiation of `godot-ai-game-template` into a specific game project.

## 1. Gather Project Metadata
Confirm the following parameters with the user before making changes:
1. **Game Title** (replaces `[Game Name]`, e.g., `Starlight Tactics`).
2. **Android Package / Application ID** (replaces `com.example.game`, e.g., `com.opengamestack.starlighttactics`, using lowercase reverse-domain notation).
3. **Short Project Description** (replaces `"A generic AI-first Godot 4.7.2 project."` in `game/project.godot`).
4. **Initial Version** (defaults to `0.1.0` with `version/code=1`).

## 2. Files Requiring Placeholder Replacement
Use `edit_file` (never PowerShell redirection, which can introduce UTF-8 BOMs) to replace `[Game Name]` and `com.example.game` across the following files:

### Engine & OpenGameStack Configuration
1. [`game/project.godot`](../../../game/project.godot):
   - `config/name="<Game Title>"`
   - `config/description="<Short Project Description>"`
   - `config/version="<Initial Version>"`
2. [`game/export_presets.cfg`](../../../game/export_presets.cfg):
   - `package/unique_name="<Android Package ID>"`
   - `package/name="<Game Title>"`
   - `version/name="<Initial Version>"`
3. [`stack.json`](../../../stack.json):
   - `"stack_name": "<Game Title>"`

### Documentation & Agent Instructions
4. [`AGENTS.md`](../../../AGENTS.md)
5. [`README.md`](../../../README.md)
6. [`CONTRIBUTING.md`](../../../CONTRIBUTING.md)
7. [`documents/creating_issues.md`](../../../documents/creating_issues.md)
8. [`documents/resolving_issues.md`](../../../documents/resolving_issues.md)
9. [`documents/reviewing_and_merging_prs.md`](../../../documents/reviewing_and_merging_prs.md)
10. [`.github/ISSUE_TEMPLATE/feature_request.md`](../../../.github/ISSUE_TEMPLATE/feature_request.md)
11. [`.agents/skills/issue-orchestration/SKILL.md`](../issue-orchestration/SKILL.md)
12. [`.agents/skills/release-management/SKILL.md`](../release-management/SKILL.md)

## 3. Populate Initial Requirements
If the user has described their game concept, update [`documents/requirements.md`](../../../documents/requirements.md) with:
- Core gameplay loop and rules.
- Target UI screens, portrait/landscape orientation, and layout hierarchy.
- Persistence and save data format (`user://` paths).
- Platform-specific constraints (Android safe areas, Web/HTML5 font fallbacks).

## 4. Verification Steps
After updating the files, verify that no placeholders remain and all tests pass:
```powershell
# 1. Verify no "[Game Name]" or "com.example.game" placeholders remain outside project-bootstrap
Select-String -Path "game\project.godot","game\export_presets.cfg","stack.json","README.md","AGENTS.md" -Pattern "\[Game Name\]|com\.example\.game"

# 2. Run headless Godot asset import and unit tests
godot --headless --editor --quit --path game
godot --headless --path game -s res://tests/test_runner.gd

# 3. Run Python Android 16 KiB validator unit tests
python -m unittest discover -s scripts -p "test_*.py" -v
```
