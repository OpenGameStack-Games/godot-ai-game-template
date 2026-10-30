# [Game Name] - Godot AI Template

An AI-first Godot 4.7.2 project template featuring built-in CI/CD pipelines, strict documentation standards, and automated agent orchestration.

## Getting Started
1. Click **Use this template** to create a new repository.
2. Ensure you have Godot 4.7.2 installed and add the directory containing the executable to your system's `PATH` environment variable. Make sure the executable is named `godot` (or `godot.exe` / `godot.bat` on Windows) so the command line can find it.
3. Ask your AI Agent to run the [`project-bootstrap`](.agents/skills/project-bootstrap/SKILL.md) skill to rename `[Game Name]` and `com.example.game` and set up your initial game requirements!

## AI Agent Architecture (`AGENTS.md` & `.agents/`)
This repository is structured for autonomous and pair-programming AI agents:
- **[`AGENTS.md`](AGENTS.md) & [`game/AGENTS.md`](game/AGENTS.md):** Hierarchical instruction manuals automatically loaded by AI coding agents (such as Google Antigravity, Claude Code, Cursor, and Codex), defining environment constraints, GDScript static typing rules, testing requirements, and workflow guardrails.
- **Agent Rules ([`.agents/rules/`](.agents/rules/)):** Always-on security and secret management policies ([`security_secrets.md`](.agents/rules/security_secrets.md)).
- **Agent Skills ([`.agents/skills/`](.agents/skills/)):**
  - **[`issue-orchestration`](.agents/skills/issue-orchestration/SKILL.md):** Multi-agent pipeline orchestrating `issue_creator`, `issue_resolver`, and `pr_reviewer` subagents across isolated Git worktrees.
  - **[`release-management`](.agents/skills/release-management/SKILL.md):** Automated version bumping, draft release creation, CI monitoring, and release publication.
  - **[`mcp-visual-qa`](.agents/skills/mcp-visual-qa/SKILL.md):** Runbook for interactive visual inspection and UI verification via the MCP TCP bridge.
  - **[`project-bootstrap`](.agents/skills/project-bootstrap/SKILL.md):** Runbook for initializing a new game project from this template.

## OpenGameStack Integration
This project is configured as an **OpenGameStack (OGS)** project. It includes `stack.json` and `ogs_config.json` files which define the exact environment (like Godot 4.7.2) required to run and build this game.

To get started with OGS:
1. Download the [OGS Launcher](https://github.com/OpenGameStack-Launcher/ogs-launcher).
2. Open the OGS Launcher and click **Add Project** to register this repository.
3. The launcher will read `stack.json` and automatically download the correct Godot version and any other required tools for your team.

## AI Agent Integration (MCP)
This template integrates the Model Context Protocol (MCP) to allow AI assistants (like Antigravity, Claude Desktop, or Cursor) to directly interact with the running game.

The `McpInteractionServer` is pre-registered as an AutoLoad (`res://autoloads/mcp_interaction_server.gd`). When you run your game in debug mode (`godot --path game`), it exposes a local TCP bridge on `127.0.0.1:9090` (automatically disabled in non-debug release exports and Web builds).

### Option A: Zero-Dependency Python Client (Recommended for Agents)
A lightweight CLI script [`mcp_client.py`](mcp_client.py) is included in the project root. While the game is running, execute:
```powershell
python mcp_client.py ping                        # Verifies McpInteractionServer is reachable
python mcp_client.py screenshot                  # Saves high-res visual snapshot to screenshot.png
python mcp_client.py click 360 640               # Sends click input at coordinates (x, y)
python mcp_client.py key_press ENTER             # Sends key or action press
python mcp_client.py get_scene_tree              # Returns full SceneTree hierarchy as JSON
python mcp_client.py get_ui_elements             # Lists visible UI controls with rects and text
python mcp_client.py get_node_info /root/Node    # Inspects properties, signals, and methods of a node
python mcp_client.py get_property /root/Node name
python mcp_client.py set_property /root/Node visible true
python mcp_client.py get_performance             # Returns FPS, frame times, and orphan node counts
python mcp_client.py eval "return 2 + 2"         # Evaluates runtime GDScript expression
python mcp_client.py raw --file payload.json     # Sends custom MCP JSON payload
```

### Option B: Full Node.js MCP Server Bridge
For assistant integration in Claude Desktop or IDEs:
1. Clone or download the [godot-mcp](https://github.com/tugcantopaloglu/godot-mcp) repository locally.
2. In the `godot-mcp` directory, run `npm install` and `npm run build`.
3. Configure your AI agent configuration (e.g. `claude_desktop_config.json`):
   ```json
   "mcpServers": {
     "godot": {
       "command": "node",
       "args": ["/path/to/godot-mcp/build/index.js", "/path/to/your/game"]
     }
   }
   ```
4. Run your game! Your AI agent can now use the `screenshot` tool to visually inspect the game (which automatically saves a high-res snapshot to `res://agent_screenshot.png`), interact with UI elements, and execute runtime GDScript.

## Cross-Platform Builds & CI/CD
This template includes production-tested GitHub Actions workflows:
- **Continuous Integration (`ci.yml`):** Automatically runs on every Pull Request and push to `main`. Executes Python unit tests, runs a headless Godot asset import pass, and runs the GDScript unit test suite (`res://tests/test_runner.gd`).
- **Android Release (`android_release.yml`):** Automatically triggers on tag push (`v*`). Runs headless tests, validates 16 KiB page size compliance, builds an Android App Bundle (`.aab`) with ProGuard mappings and native debug symbols, signs the bundle, and publishes release assets.
- **Web Release (`web_release.yml`):** Automatically builds an HTML5 Web export, attaches a zip archive to GitHub Releases, and supports automated deployment to Itch.io via Butler when `BUTLER_API_KEY`, `ITCH_USERNAME`, and `ITCH_GAME` secrets are configured.
- **GL Compatibility Renderer:** Configured out of the box with `gl_compatibility` (OpenGL ES 3.0 / WebGL 2.0), guaranteeing optimal compatibility across Web/HTML5 exports and Android mobile hardware.

## Git LFS Requirement
This template is configured to use [Git Large File Storage (LFS)](https://git-lfs.com/) for all binary assets (images, audio, video, 3D models, fonts, etc.). It is assumed that repositories instantiated from this template will have Git LFS installed and enabled locally.

To ensure your assets are tracked correctly:
1. Ensure Git LFS is installed on your machine (`git lfs install`).
2. The provided `.gitattributes` file will automatically handle LFS tracking for standard game asset extensions.

## License
This project uses a split license:
- **Source Code:** Licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
- **Game Assets:** Unless otherwise specified, art, audio, and models in `game/assets/` are licensed under [Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)](LICENSE-ASSETS).
