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

## Git LFS Requirement
This template is configured to use [Git Large File Storage (LFS)](https://git-lfs.com/) for all binary assets (images, audio, video, 3D models, fonts, etc.). It is assumed that repositories instantiated from this template will have Git LFS installed and enabled locally.

To ensure your assets are tracked correctly:
1. Ensure Git LFS is installed on your machine (`git lfs install`).
2. The provided `.gitattributes` file will automatically handle LFS tracking for standard game asset extensions.
 
## License
This project uses a split license:
- **Source Code:** Licensed under the [GNU General Public License v3.0 (GPLv3)](LICENSE).
- **Game Assets:** Unless otherwise specified, art, audio, and models in `game/assets/` are licensed under [Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)](LICENSE-ASSETS).
