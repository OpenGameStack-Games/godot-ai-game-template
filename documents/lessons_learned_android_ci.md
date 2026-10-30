# Lessons Learned: Godot 4 Headless Android Export & Mobile UI on GitHub Actions

Exporting a Godot 4 Android App Bundle (`.aab`) headlessly via GitHub Actions involves several undocumented edge cases and engine quirks. This document records the issues encountered across OpenGameStack production games and the workarounds required to build, validate, and sign Android and Web releases reliably.

---

## 1. The Godot 4 `.tres` Parser Requires a Blank Line Before `[resource]`
Godot's `editor_settings-4.7.tres` (and earlier `4.x` versions) requires a strict section format. If you dynamically generate this file in a CI script to inject the `$ANDROID_HOME` and `$JAVA_HOME` environment variables, you **must** include a completely blank line between the `[gd_resource]` header and the `[resource]` block.

- **Bug:** If the blank line is missing, the Godot Resource Parser silently fails to parse the file and ignores your injected SDK paths.
- **Fix:** Ensure a blank line exists before `[resource]` in any generated `.tres` files:
  ```ini
  [gd_resource type="EditorSettings" format=3]

  [resource]
  export/android/android_sdk_path = "/path/to/android/sdk"
  ```

## 2. Editor Settings Are Overwritten During Headless Asset Import
When Godot runs `godot --headless --editor --quit` to import assets, it saves its in-memory editor settings upon exiting. If the Android export templates are not yet active during that initial pass, Godot may overwrite `editor_settings-4.7.tres` and clear the injected Android SDK paths.
- **Fix:** Always generate or update `editor_settings-4.7.tres` *after* running the initial headless asset import and test steps, right before executing `--export-release "Android"`.

## 3. Blank Configuration Errors in Headless Export
When Godot 4 fails an export configuration check (e.g., missing a keystore or missing ETC2/ASTC texture compression), the C++ `has_valid_export_configuration()` check can set error flags without printing the specific error reason in headless mode.
- **Bug:** You receive the generic message `ERROR: Cannot export project with preset "Android" due to configuration errors:` followed by no details.
- **Fix:** Ensure all prerequisites in Sections 4 through 7 below are satisfied before running `--export-release`.

## 4. ETC2/ASTC Texture Compression Is Required
When building through the Godot Editor GUI, the editor warns if you export to Android without enabling ETC2/ASTC texture compression. Headless export fails with a blank configuration error instead.
- **Fix:** Ensure the following setting is present in `game/project.godot`:
  ```ini
  [rendering]
  textures/vram_compression/import_etc2_astc=true
  ```

## 5. Export Presets Require Keystore Paths Even for Unsigned Builds
When exporting an Android App Bundle using Gradle, Godot requires `game/export_presets.cfg` to contain a valid keystore file path in `keystore/release` (and `keystore/debug`). Even when `package/signed=false` because you sign the bundle later in GitHub Actions, Godot refuses to export if this path is empty or points to a non-existent file. Furthermore, paths in `export_presets.cfg` are resolved relative to the Godot project root (`res://`).
- **Fix:** Generate an ephemeral dummy keystore inside the Godot project directory (`game/debug.keystore`) during CI and point `export_presets.cfg` to `res://debug.keystore`. Then sign the resulting `.aab` with production secrets in a dedicated GitHub Actions step.

## 6. The Hidden `.build_version` File in Gradle Templates
When you click "Install Android Build Template" in the Godot GUI, Godot extracts `android_source.zip` into `game/android/build/` and writes a hidden file named `game/android/.build_version` containing the exact template version string (e.g., `4.7.2.stable`). If this hidden file is missing, headless export fails with:
`Trying to build from a gradle built template, but no version info for it exists.`
- **Fix:** In CI, write the exact template version string to `game/android/.build_version` right after unzipping `android_source.zip`.

## 7. Linux Executable Permissions on `gradlew`
If the Android build template is extracted on Windows or from certain archives, `game/android/build/gradlew` may lack the Unix executable bit, causing Ubuntu GitHub Actions runners to fail with `Permission denied`.
- **Fix:** Run `chmod +x game/android/build/gradlew` in the workflow before running the Godot Android export command.

## 8. Android 16 KiB Memory Page Size Support
Google Play requires apps targeting Android 15+ to support 16 KiB memory page sizes. Two separate alignment requirements must both be satisfied:
1. **ZIP Data Alignment:** APKs produced from an App Bundle must store uncompressed `.so` native libraries on 16 KiB data boundaries (verified with `zipalign -c -P 16 -v 4`).
2. **ELF `PT_LOAD` Alignment:** Every 64-bit native shared library (`arm64-v8a`, `x86_64`) inside the AARs/APKs must be compiled with ELF `PT_LOAD` program-segment alignment of at least `16384` bytes (`16 KiB`). AGP/Gradle packaging cannot rewrite ELF program headers.

- **Fix / Mitigation:** Use Godot `4.7.2` Android export templates (whose 64-bit libraries have 16 KiB `PT_LOAD` alignment) and validate both the `.aab` ELF headers and Bundletool-generated `.apks` ZIP data alignment in CI using [`scripts/validate_android_16kb.py`](../scripts/validate_android_16kb.py) and `zipalign -c -P 16 -v 4`.

## 9. Native Debug Symbols and ProGuard Obfuscation Mapping
Google Play Console flags warnings if native debug symbols and obfuscation mapping files are not provided alongside an Android App Bundle.
- **Fix:** In `game/export_presets.cfg`, set `gradle_build/export_debug_symbols=true`. Godot outputs `*-native-debug-symbols.zip` in `game/`, and Gradle outputs `game/android/build/outputs/mapping/release/mapping.txt`. Upload both alongside `Game.aab` in `.github/workflows/android_release.yml`.

## 10. Plain Text Runtime Assets Need Explicit Export Filters
When `export_filter="all_resources"` is used, Godot only packages files it recognizes as imported engine resources. Plain data files loaded via `FileAccess` (such as `.txt` word lists or `.json` data tables) do not generate `.import` files and are omitted from exports unless `include_filter` matches them.
- **Fix:** Keep `include_filter="*.ttf, *.txt, *.json"` (and any additional runtime data extensions) on both the `Android` and `Web` presets in `game/export_presets.cfg`, and write a unit test asserting `FileAccess.file_exists(...)` for critical runtime files.

## 11. Android Display Cutouts Need Runtime Safe Area Handling
Android devices with camera cutouts or status bars report a non-zero top/bottom inset through `DisplayServer.get_display_safe_area()`. Full-screen layouts should add that runtime inset to their base margins rather than hardcoding large static offsets.
- **Fix:** Apply safe-area margin adjustments in `_ready()` and on `NOTIFICATION_RESIZED` so top headers and bottom controls remain unobstructed on cutout devices while preserving normal spacing on desktop and web.

## 12. Case Study: Keep Vertical Gameplay Flow Under One Layout Container
In portrait mobile games (such as a header + game board + on-screen keyboard stack), mixing a flow-managed `VBoxContainer` with a separately anchored bottom control makes the boundary fragile whenever safe-area insets or viewport aspect ratios change.
- **Fix:** Give a single root `MarginContainer/VBoxContainer` ownership of the vertical stack so header, gameplay area (`SIZE_EXPAND_FILL`), and bottom controls share one layout authority and never overlap.

## 13. Case Study: Responsive Portrait Sizing with `AspectRatioContainer`
Rigid minimum heights on child panels can cause `VBoxContainer` to overflow on shorter portrait viewports.
- **Fix:** Wrap fixed-aspect gameplay boards in an `AspectRatioContainer`, keep bottom controls flexible, scale font sizes dynamically from allocated rects, and apply top and bottom safe-area margins.

## 14. Deterministic Layout-Plan Tests vs. Frame-Based Integration Tests
A pure layout-calculation helper that computes target rects for UI regions allows unit tests to verify layout math deterministically in headless mode without waiting for rendered frames.
- **Recommendation:** Use deterministic layout-math unit tests as the fast CI baseline, and pair them with MCP visual QA (`python mcp_client.py screenshot`) or frame-based integration tests when tuning animations, font metrics, or theme styling.

## 15. Optional Direct Google Play Store Deployment
If automating direct uploads to Google Play via `r0adkll/upload-google-play@v1`:
- **Prerequisites:** The app must complete its first upload and review manually in Google Play Console before the Google Play Developer API allows automated releases.
- **Authentication:** Store the Google Cloud Service Account JSON in a `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON` GitHub Secret and grant it release permissions in Play Console.
- **Diagnostic Artifacts:** Upload `./game/*.aab`, `./game/android/build/outputs/mapping/release/mapping.txt`, and `./game/*-native-debug-symbols.zip` together after the signing step, guarded by `if: startsWith(github.ref, 'refs/tags/v')`.
