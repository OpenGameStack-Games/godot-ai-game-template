# Security & Secrets Management

**CRITICAL DIRECTIVES FOR ALL AGENTS:**

1. **NEVER COMMIT SECRETS**: You are strictly forbidden from committing or pushing any of the following to the git repository:
   - Java Keystores (`.keystore`, `.jks`)
   - Private keys, PEM files, or certificates
   - API keys, access tokens, or unencrypted passwords
   - Configuration files that contain raw credentials

2. **USE GITHUB SECRETS**: For automated CI/CD pipelines (like GitHub Actions), you must configure the workflow to retrieve credentials via GitHub Secrets (e.g., `${{ secrets.KEYSTORE_BASE64 }}`).

3. **VERIFY GITIGNORE**: Always ensure that `.gitignore` is properly configured to exclude sensitive file extensions (e.g., `*.keystore`, `*.jks`) before generating them.

4. **UNSIGNED EXPORTS**: When configuring Godot's `export_presets.cfg` for automated cloud builds, leave the keystore path and password fields blank. Cloud workflows should build an unsigned `.aab`/`.apk` and sign it post-build using `jarsigner` or `apksigner` with injected secrets.
