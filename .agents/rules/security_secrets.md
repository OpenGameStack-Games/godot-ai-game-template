# Security & Secrets Management

**CRITICAL DIRECTIVES FOR ALL AGENTS:**

1. **NEVER COMMIT SECRETS**: You are strictly forbidden from committing or pushing any of the following to the git repository:
   - Java Keystores (`.keystore`, `.jks`)
   - Private keys, PEM files, service account JSON files, or certificates
   - API keys, access tokens, or unencrypted passwords
   - Configuration files that contain raw production credentials

2. **USE GITHUB SECRETS**: For automated CI/CD pipelines (like GitHub Actions), always retrieve production credentials via GitHub Secrets (e.g., `${{ secrets.KEYSTORE_BASE64 }}`, `${{ secrets.BUTLER_API_KEY }}`).

3. **VERIFY GITIGNORE**: Always ensure that [`.gitignore`](../../.gitignore) excludes sensitive and generated credential files (`*.keystore`, `*.jks`) before generating them locally or in CI.

4. **GODOT EXPORT PRESETS & DUMMY KEYSTORE**:
   - Never place real release keystore paths, aliases, or passwords in [`game/export_presets.cfg`](../../game/export_presets.cfg).
   - However, do **not** leave `keystore/debug` or `keystore/release` blank in `game/export_presets.cfg`. Godot 4's headless Gradle exporter refuses to build an Android App Bundle if `keystore/release` is empty, even when `package/signed=false` (see Lesson #5 in [`documents/lessons_learned_android_ci.md`](../../documents/lessons_learned_android_ci.md)).
   - Instead, keep `package/signed=false` and leave `keystore/debug` and `keystore/release` pointing to `res://debug.keystore` with the standard dummy credentials (`androiddebugkey` / `android`). CI generates `game/debug.keystore` ephemerally during the workflow and re-signs the `.aab` post-build using injected GitHub Secrets.

5. **DEBUG-ONLY MCP BRIDGE**:
   - [`McpInteractionServer`](../../game/autoloads/mcp_interaction_server.gd) exposes a local TCP bridge (`127.0.0.1:9090`) that supports runtime GDScript evaluation (`eval`).
   - It must remain restricted to `127.0.0.1` and guarded by `OS.is_debug_build() and not OS.has_feature("web")` so that production release builds never open a listening socket.
