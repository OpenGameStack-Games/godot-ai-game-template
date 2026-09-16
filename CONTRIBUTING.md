# Contributing to [Game Name]

Thank you for your interest in contributing to our game! Since this repository is driven by the **OpenGameStack (OGS)** standard and orchestrated by autonomous AI agents, our contribution workflow is highly structured.

## 1. Finding Something to Work On
Check the Issues tab for tasks labeled `help wanted` or `good first issue`. 
Please comment on the issue to let the maintainers know you are working on it.

## 2. Setting Up the Environment
This project uses the OpenGameStack Launcher to guarantee environment consistency.
1. Download the [OGS Launcher](https://github.com/OpenGameStack-Launcher/ogs-launcher).
2. Add this repository to the launcher. It will automatically download Godot 4.7.2.
3. Open the project via the launcher.

## 3. Pull Request Guidelines
When submitting a Pull Request, please ensure:
*   **Testing:** All headless tests pass. Run `godot --headless --path game -s res://tests/test_runner.gd` locally.
*   **Documentation:** If your PR changes UI or core mechanics, please note what needs to be updated in `documents/requirements.md` and `README.md`.
*   **Atomic Commits:** Keep your commits focused on the single issue at hand.

All PRs will be reviewed by our AI agents for formatting, static typing, and test coverage before a human maintainer signs off.
