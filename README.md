# [Game Name] - Godot AI Template

An AI-first Godot 4.7.2 project template featuring built-in CI/CD pipelines, strict documentation standards, and automated agent orchestration.

## Getting Started
1. Click **Use this template** to create a new repository.
2. Ensure you have Godot 4.7.2 installed and add the directory containing the executable to your system's `PATH` environment variable. Make sure the executable is named `godot` (or `godot.exe` / `godot.bat` on Windows) so the command line can find it.
3. Use your AI Agent to build your game!

## OpenGameStack Integration
This project is configured as an **OpenGameStack (OGS)** project. It includes `stack.json` and `ogs_config.json` files which define the exact environment (like Godot 4.7.2) required to run and build this game.

To get started with OGS:
1. Download the [OGS Launcher](https://github.com/OpenGameStack-Launcher/ogs-launcher).
2. Open the OGS Launcher and click **Add Project** to register this repository.
3. The launcher will read `stack.json` and automatically download the correct Godot version and any other required tools for your team.

## AI Agent Integration (MCP)
This template integrates the Model Context Protocol (MCP) to allow your AI assistants (like Claude Desktop, Cursor, or Antigravity) to directly interact with the running game. 

The `McpInteractionServer` is pre-registered as an AutoLoad. When you playtest your game, it exposes a TCP bridge.

**To connect your AI Assistant:**
1. Clone or download the [godot-mcp](https://github.com/tugcantopaloglu/godot-mcp) repository locally.
2. In the `godot-mcp` directory, run `npm install` and `npm run build`.
3. Configure your AI agent to launch the node server as an MCP server. For example, in Claude Desktop, add to your `claude_desktop_config.json`:
   ```json
   "mcpServers": {
     "godot": {
       "command": "node",
       "args": ["/path/to/godot-mcp/build/index.js", "/path/to/your/game"]
     }
   }
   ```
4. Run your game! Your AI agent can now use the `screenshot` tool to visually inspect the game (which automatically saves a high-res snapshot to `res://agent_screenshot.png`), interact with UI elements, and execute runtime GDScript.

## Git LFS Requirement
This template is configured to use [Git Large File Storage (LFS)](https://git-lfs.com/) for all binary assets (images, audio, video, 3D models, fonts, etc.). It is assumed that repositories instantiated from this template will have Git LFS installed and enabled locally.

To ensure your assets are tracked correctly:
1. Ensure Git LFS is installed on your machine (`git lfs install`).
2. The provided `.gitattributes` file will automatically handle LFS tracking for standard game asset extensions.
 
## License
This project uses a split license:
- **Source Code:** Licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
- **Game Assets:** Unless otherwise specified, art, audio, and models in `game/assets/` are licensed under [Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)](LICENSE-ASSETS).
