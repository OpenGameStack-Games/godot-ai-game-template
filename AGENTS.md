# AGENTS.md - AI Agent Operations & Engineering Guide

Welcome to the **[Game Name]** repository, built on the **OpenGameStack (OGS) Godot AI Game Template**. This file is the primary operational manual for autonomous AI coding agents, subagents, and pair-programming assistants working in this repository.

---

## 1. Project Overview & Tech Stack

- **Engine:** Godot `4.7.2-stable` (configured in [`stack.json`](stack.json) and [`game/project.godot`](game/project.godot)).
- **Primary Language:** GDScript 2.0 (strict static typing required) and Python 3 (tooling, MCP client, and CI validation scripts).
- **Renderer:** `gl_compatibility` (OpenGL ES 3.0 / WebGL 2.0) for cross-platform parity across Android mobile devices and Web/HTML5 browsers.
- **Target Platforms:**
  - **Android:** Portrait orientation (`720x1280` logical viewport), exported as an Android App Bundle (`.aab`) with 16 KiB native page alignment, ProGuard mappings, and native debug symbols.
  - **Web (HTML5/WASM):** Exported to `game/export/web/index.html` and deployed to GitHub Releases and Itch.io via Butler.
- **Runtime AI Inspection Bridge:** [`McpInteractionServer`](game/autoloads/mcp_interaction_server.gd) runs as an AutoLoad in debug builds on `127.0.0.1:9090` (configurable via `GODOT_MCP_PORT`), paired with the zero-dependency [`mcp_client.py`](mcp_client.py) CLI.

---

## 2. Repository Directory Structure

```text
.
├── AGENTS.md                        # Root instructions for all AI agents (this file)
├── README.md                        # Project overview and setup instructions
├── CONTRIBUTING.md                  # Human & agent contribution guidelines
├── Godot-AI.code-workspace          # VS Code workspace settings and tasks
├── mcp_client.py                    # Zero-dependency CLI client for McpInteractionServer
├── stack.json                       # OpenGameStack tool version manifest (Godot 4.7.2)
├── ogs_config.json                  # OpenGameStack network/offline policy config
├── .agents/                         # Agent customizations (Rules & Skills)
│   ├── rules/
│   │   └── security_secrets.md      # Mandatory secret & keystore security rules
│   └── skills/
│       ├── issue-orchestration/     # End-to-end Issue Creator -> Resolver -> PR Reviewer pipeline
│       ├── release-management/      # Automated version bump, draft release, and CI verification
│       ├── mcp-visual-qa/           # Runbook for runtime inspection and screenshot QA via MCP
│       └── project-bootstrap/       # Runbook for initializing a new game from this template
├── .github/
│   ├── ISSUE_TEMPLATE/              # Standardized bug_report.md and feature_request.md
│   ├── pull_request_template.md     # Standardized PR body template with reviewer handoff
│   └── workflows/
│       ├── ci.yml                   # Automated PR & main branch test suite runner
│       ├── android_release.yml      # Tag-triggered Android AAB build, 16KB check, & release
│       └── web_release.yml          # Tag-triggered Web HTML5 build, Itch.io deploy, & release
├── documents/                       # Authoritative workflow & project specifications
│   ├── requirements.md              # Source of truth for gameplay, UI, and platform specs
│   ├── manual_testing.md            # Manual QA test cases maintained by the PR Reviewer
│   ├── creating_issues.md           # Issue creation standards and gh CLI patterns
│   ├── resolving_issues.md          # Worktree workflow, GDScript rules, and testing standards
│   ├── reviewing_and_merging_prs.md # PR review, doc synchronization, and merge protocol
│   └── lessons_learned_android_ci.md# Hard-won Godot 4 Android CI/CD & layout workarounds
├── game/                            # Godot 4.7.2 project root (res://)
│   ├── AGENTS.md                    # Directory-specific rules for Godot scenes, scripts, & tests
│   ├── project.godot                # Engine config (version, autoloads, display, renderer)
│   ├── export_presets.cfg           # Android and Web export preset definitions
│   ├── assets/                      # Fonts, icons, audio, textures (tracked via Git LFS)
│   ├── autoloads/                   # Global singletons (mcp_interaction_server.gd)
│   ├── resources/                   # Shared .tres resources (default_font.tres)
│   ├── scenes/                      # Godot scene files (.tscn)
│   ├── scripts/                     # Gameplay and UI GDScript files (.gd)
│   └── tests/                       # Headless GDScript unit test framework & test suites
└── scripts/                         # Build & validation utilities
    ├── validate_android_16kb.py     # ELF PT_LOAD and ZIP 16 KiB page alignment validator
    └── test_validate_android_16kb.py# Python unit tests for the 16 KiB validator
```

---

## 3. Environment & Shell Constraints (Critical)

1. **Windows 11 & PowerShell:**
   - The primary development environment is Windows 11 using PowerShell.
   - **Never** use Linux-only commands (`grep`, `ls -la`, `cat`, `sed`, `awk`, `chmod`, `rm -rf`). Prefer built-in agent file tools (`read_file`, `write_file`, `edit_file`) or native PowerShell cmdlets (`Get-ChildItem`, `Select-String`, `Remove-Item`).
   - **Never** chain commands with `&&` (unsupported in Windows PowerShell 5.1). Use `;` or run commands in separate tool calls.
2. **Stateless Working Directory Across Tool Calls:**
   - Each shell command execution starts in a fresh session at the repository root. Directory changes (`cd` / `Set-Location`) do **not** persist to subsequent command calls.
   - When operating inside a Git worktree (such as `.worktrees/issue-12`), always pass explicit paths (`git -C .worktrees/issue-12 ...` and `godot --headless --path .worktrees/issue-12/game ...`) or prefix `Set-Location .worktrees/issue-12;` within the same command string.
3. **File Encoding (UTF-8 Without BOM):**
   - Godot 4 fails to parse `.tscn`, `.tres`, and `.gd` files that contain a UTF-8 BOM (`Byte Order Mark`) or UTF-16 encoding (emitting `Parse Error: Expected '['`).
   - **Never** use PowerShell redirection (`>`, `Out-File`, or PowerShell 5.1 `Set-Content -Encoding UTF8`) to generate Godot files. Always use the agent's native `write_file` / `edit_file` tools.
4. **GitHub CLI (`gh`) Token Scope Caveat:**
   - **Never** run bare `gh issue view <id>` or `gh pr view <id>` commands, as they query Classic Projects metadata and fail with a `read:project` token scope error.
   - Always pass explicit `--json` fields:
     ```powershell
     gh issue view <id> --json title,body,state,labels,assignees
     gh pr view <id> --json title,body,state,baseRefName,headRefName,commits,files
     ```
5. **Git LFS for Binary Assets:**
   - Binary assets (`.png`, `.ttf`, `.wav`, `.ogg`, `.mp3`, `.glb`, etc.) are tracked via Git LFS per [`.gitattributes`](.gitattributes). Ensure `git lfs install` is active before committing binary files.

---

## 4. Essential Commands

### Run Godot Headless Asset Import & Unit Tests
Always run an editor import pass first when new files, scenes, resources, or `class_name` scripts have been added or modified:
```powershell
godot --headless --editor --quit --path game
godot --headless --path game -s res://tests/test_runner.gd
```
- **Pass Requirement:** Output must report `Test Results: <N> Passed, 0 Failed` with exit code `0`.

### Run Python Build Validator Unit Tests
```powershell
python -m unittest discover -s scripts -p "test_*.py" -v
```

### Runtime Visual QA via MCP Client
When verifying UI layouts, colors, or runtime scene state (see [`.agents/skills/mcp-visual-qa/SKILL.md`](.agents/skills/mcp-visual-qa/SKILL.md)):
```powershell
# 1. Start the game in the background (opens TCP bridge on 127.0.0.1:9090 in debug mode)
# 2. Query or interact with the running game:
python mcp_client.py ping
python mcp_client.py screenshot
python mcp_client.py get_scene_tree
python mcp_client.py get_ui_elements
python mcp_client.py click 360 640
python mcp_client.py key_press ENTER
python mcp_client.py get_node_info /root/Node
# 3. Stop the background Godot instance when finished to release Windows file locks:
Stop-Process -Name "godot" -Force -ErrorAction SilentlyContinue
```

---

## 5. Coding, Architecture & Testing Standards

Detailed engineering standards live in [`game/AGENTS.md`](game/AGENTS.md) and [`documents/resolving_issues.md`](documents/resolving_issues.md). Key invariants include:

1. **Strict Static Typing:** Every variable, parameter, and return type in GDScript (both production code and `game/tests/*.gd`) must be explicitly typed. Use explicit `as` casts for dynamic node lookups (`get_node_or_null("Path") as Label`).
2. **Track `.uid` Metadata:** Always commit Godot-generated `.uid` and `.import` metadata files (where not gitignored) alongside scripts and resources.
3. **Categorized Logging:** Do not use raw `print()` in gameplay or UI scripts. Use `print_debug()`, `push_warning()`, and `push_error()`.
4. **Web/HTML5 Font Fallbacks:** Browser WASM builds cannot access host OS fonts. Any custom `FontVariation`, `FontFile`, or `Theme` must retain `res://assets/fonts/NotoSansSymbols-Regular.ttf` and `res://assets/fonts/DejaVuSans.ttf` in its `fallbacks` array (see [`game/resources/default_font.tres`](game/resources/default_font.tres)), and any UI symbol used must be verified with `font.has_char(ord(ch))` in unit tests.
5. **Version Synchronization:** Keep `config/version` in [`game/project.godot`](game/project.godot) and `version/name` in [`game/export_presets.cfg`](game/export_presets.cfg) synchronized.

---

## 6. Agent Orchestration, Skills & Authorization Gates

This repository uses structured multi-agent workflows defined under [`.agents/skills/`](.agents/skills/):

- **[`issue-orchestration`](.agents/skills/issue-orchestration/SKILL.md):** Orchestrates `issue_creator`, `issue_resolver`, and `pr_reviewer` subagents sequentially (one subagent at a time, one task per subagent).
  - **Gate 1 (After Issue Creation):** Never automatically resolve a newly created issue. Stop and ask the user whether to log another issue or start resolving open issues.
  - **Gate 2 (Before Issue Resolution):** Never invoke `issue_resolver` without explicit user authorization in the current turn.
  - **Role Separation:** `issue_resolver` works in an isolated worktree (`.worktrees/issue-<number>`), runs tests, performs visual QA, opens the PR with handoff notes, and stops without modifying `documents/` or merging. `pr_reviewer` verifies tests, updates `documents/requirements.md`, `documents/manual_testing.md`, and `README.md`, removes the worktree, and merges the PR via `gh pr merge <id> --merge --delete-branch`.
- **[`release-management`](.agents/skills/release-management/SKILL.md):** Orchestrates `release_manager` to bump versions, create a draft GitHub release, push the `v<VERSION>` tag to trigger Android and Web CI workflows, monitor both runs to completion, and publish the release.
  - **Gate 3 (Before Release):** Never run the release pipeline without explicit user instruction.
- **[`mcp-visual-qa`](.agents/skills/mcp-visual-qa/SKILL.md):** Step-by-step guide for interactive visual inspection and UI verification using `McpInteractionServer` and `mcp_client.py`.
- **[`project-bootstrap`](.agents/skills/project-bootstrap/SKILL.md):** Step-by-step guide for renaming `[Game Name]` and `com.example.game` when initializing a new game from this template.
