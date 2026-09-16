# Lessons Learned: Godot 4 Headless Android Export on GitHub Actions

Exporting a Godot 4 Android App Bundle (.aab) headlessly via GitHub Actions contains several undocumented edge cases and bugs. This document serves as a record of the issues encountered and the necessary workarounds to successfully build and sign an Android release.

## 1. The Godot 4.3 \.tres\ Parser is Extremely Strict
Godot's \editor_settings-4.3.tres\ requires a very specific syntax. If you dynamically generate this file in a bash script to inject the \\\ and \\\ environment variables, you **must** include a completely blank line between the \[gd_resource]\ header and the \[resource]\ block.

**Bug:** If the blank line is missing, the Godot Resource Parser will silently fail to parse the file and completely ignore your injected SDK paths.
**Fix:** Ensure a blank line exists before \[resource]\ in any manually generated \.tres\ files.

## 2. Editor Settings Are Aggressively Wiped During Headless Asset Import
When Godot runs a headless command like \godot --editor --quit\ to import assets, it forcibly saves the editor settings upon exiting. If the Android export templates aren't fully configured or active in memory during this step, Godot may overwrite \editor_settings-4.3.tres\ and purge the Android SDK paths.
**Fix:** Always generate or modify the \editor_settings-4.3.tres\ file *after* running the initial headless asset import step, right before the actual export command.

## 3. Blank Configuration Errors
When Godot 4 fails an export configuration check (e.g., missing a keystore or missing ETC2 compression), it is supposed to output the reason. However, due to a bug in the \has_valid_export_configuration()\ C++ function in Godot 4.3, some error flags are set without appending the actual error text.
**Bug:** You will receive the generic error \ERROR: Cannot export project with preset "Android" due to configuration errors:\ followed by absolute silence.
**Fix:** Ensure all prerequisites below are met, as Godot will not explicitly tell you which one failed.

## 4. ETC2/ASTC Texture Compression is Strictly Required
When building through the Godot Editor GUI, the editor will display a large red warning if you try to export to Android without enabling ETC2/ASTC texture compression. Headless export does not give this warning; it simply fails with a blank configuration error (see #3).
**Fix:** Ensure the following is in your \project.godot\ file:
\\\ini
[rendering]
textures/vram_compression/import_etc2_astc=true
\\\

## 5. Export Presets Require Keystore Paths Even for Unsigned Builds
When exporting an Android App Bundle using Gradle, Godot requires the \export_presets.cfg\ to contain a valid keystore path in the \keystore/release\ property. Even if you have \package/signed=false\ or plan to sign the app later using GitHub Actions, Godot will refuse to export if this path is empty or points to a non-existent file. Furthermore, Godot strictly expects paths in \export_presets.cfg\ to be relative to the Godot project root (e.g., \es://\).
**Fix:** Generate a dummy keystore inside the Godot project directory and point \export_presets.cfg\ to it (\es://debug.keystore\). You can then strip and re-sign the resulting unsigned \.aab\ using a dedicated GitHub Action later in the pipeline.

## 6. The Hidden \.build_version\ File in Gradle Templates
When you click "Install Android Build Template" in the Godot GUI, Godot extracts the \ndroid_source.zip\ into the \ndroid/build/\ directory. Crucially, it also creates a hidden file named \.build_version\ in the parent directory (\ndroid/\). This file contains the exact engine version string (e.g., \4.3.stable\). 
If you commit the extracted template to Git and this hidden file is lost or missing, Godot's headless export will fail with: \Trying to build from a gradle built template, but no version info for it exists.\
**Fix:** Manually create \ndroid/.build_version\ and ensure it contains the exact Godot version string (e.g., \4.3.stable\).

## 7. Windows Strips Executable Permissions from \gradlew\
If the Android build template is extracted and committed to Git from a Windows machine, the \gradlew\ (Gradle Wrapper) script will lose its Linux executable permissions. When GitHub Actions (running on Ubuntu) attempts to invoke Gradle, it will fail with \Permission denied\.
**Fix:** Add a step in the GitHub workflow to restore the permissions before exporting: \chmod +x game/android/build/gradlew\.


## 8. Android 16 KB Memory Page Size Support
Google Play requires apps targeting Android 15+ to support 16 KB memory page sizes. There are two distinct alignment considerations that must both be satisfied:

1. ZIP data alignment: APKs produced from an App Bundle must store native libraries on 16 KiB data boundaries (this is controlled by the packaging step and can be verified with `zipalign -c -P 16`).
2. ELF PT_LOAD alignment: The native shared libraries themselves (the ELF files inside AARs/APKs) must have PT_LOAD program-segment alignment of 16 KiB. This alignment is a property of how the native library was built and cannot be rewritten by AGP/Gradle packaging.

**Root cause observed:** In this incident the critical failure was not solely ZIP local-header offsets — the committed Godot 4.3 template AARs included 64-bit libraries whose ELF PT_LOAD alignments were 4096 bytes. Upgrading AGP/Gradle alone did not change those ELF headers. The correct remediation was to update the Godot Android templates to a version whose 64-bit libraries expose PT_LOAD alignment of 16384 (16 KiB) and to add CI-side validation.

**Fix / Mitigation:** Replace or rebuild Android template AARs so 64-bit libraries (arm64-v8a, x86_64) have PT_LOAD alignment 16 KiB (the PR updates use Godot 4.7.2 templates). In CI, validate both the ELF PT_LOAD alignment and the APK/ZIP data alignment (for example using `scripts/validate_android_16kb.py` plus Bundletool and `zipalign -c -P 16`). This distinction is important: ZIP local-header offsets, AAB bundle internals, and ELF PT_LOAD alignment are related but separate checks — failing to validate the ELF headers can silently allow an AAB to be uploaded that Play will reject.
## 9. Native Debug Symbols and Obfuscation Mapping
Google Play Console flags warnings if native symbols and obfuscation mapping files are not uploaded with the Android App Bundle.
**Fix:** In `game/export_presets.cfg`, enable `gradle_build/export_debug_symbols=true`. When exporting with Gradle, Godot outputs `*-native-debug-symbols.zip` in the root export directory and Gradle produces `mapping.txt` at `game/android/build/outputs/mapping/release/mapping.txt`. Include these paths in the artifact upload step in `.github/workflows/android_release.yml`.

## 10. Plain Text Runtime Assets Need Explicit Export Filters
When `export_filter="all_resources"` is used, Godot only packages files it recognizes as exportable resources. Plain text runtime assets such as `res://assets/words/words.txt` do not generate `.import` metadata, so they are silently omitted from Android exports unless `include_filter` explicitly matches them (for example, `*.txt`).
**Fix:** Treat any `FileAccess`-loaded runtime asset as an export dependency and add an explicit `include_filter` entry for the file type or path. For critical data such as dictionaries, also keep a loud `push_error(...)` path in the loader so empty or missing packaged assets fail fast instead of producing a silent empty state.

## 11. Android Display Cutouts Need Runtime Safe Area Handling
Android devices with punch-hole cameras or notches can report a non-zero top safe area through Godot 4's `DisplayServer.get_display_safe_area()`. Full-screen layouts should add that runtime inset to their existing base top margin instead of hardcoding a larger offset, or flat-screen devices will end up with unnecessary extra padding.
**Fix:** Apply the safe-area adjustment during `_ready()` and again on `NOTIFICATION_RESIZED` so the Main Game, Main Menu, and Statistics Screen all keep their top headers visible on cutout devices while preserving the original design spacing when the safe-area top inset is zero.

## 12. Keep the Main Game Vertical Flow Under One Layout Authority
Mixing a flow-managed `VBoxContainer` with a separately anchored keyboard block made the board/keyboard boundary fragile as soon as the keyboard height, key padding, or safe-area inset changed. The fix was to give `ContentMargin/VBoxContainer` full ownership of the Main Game's vertical stack, keep `Header`, `ToastOverlay`, `BoardArea`, and `KeyboardWrapper` as sequential siblings, and let only `BoardArea` expand while the keyboard stays in a full-rect wrapper with its own intrinsic height.
**Fix:** When refactoring responsive gameplay layouts, keep the board and keyboard inside one shared vertical flow so safe-area padding, bottom breathing room, and viewport resizing are applied consistently without overlap.

## 13. Main Game Portrait Layout Needs Container-Owned Flow, Not Rigid Keyboard Offsets
The Main Game overlap regression showed that a plain `Control` board wrapper, a rigid keyboard wrapper, and fixed keyboard/tile sizing can trick `VBoxContainer` into under-allocating height on tall portrait devices. When that happens, the keyboard steals space from the board and can bleed below the viewport even if the top safe area is handled correctly.
**Fix:** Give the board its own `AspectRatioContainer`, let the keyboard own only a flexible minimum height, scale tile and key typography from the actual allocated rect, and apply both top and bottom safe-area margins so portrait Android devices keep all six board rows visible without overlap.

## 14. Deterministic Layout-Plan Tests vs. Frame-Based Integration Tests
A deterministic layout-region helper that computes the planned rects for header, board, keyboard, and breathing buffers allows unit tests to validate layout math without depending on an asynchronous rendered frame. This approach makes automated CI fast, deterministic, and cross-platform.

**Trade-offs & Recommendation:**
- Deterministic layout-plan tests are sufficient to catch regressions in the layout calculations (ratios, clamping, ordering, and non-overlap guarantees). They should be the baseline for CI and PR acceptance.
- However, engine-specific rendering, font metrics, and theme-driven layout adjustments can produce small visual differences at runtime. For pixel-perfect or animation/transition-sensitive validations (e.g., toast fade timings, staggered reveals, or font rendering quirks on certain devices), add frame-based integration tests or manual verification steps in `documents/manual_testing.md`.
- If additional confidence is required, add a small set of end-to-end integration tests that run inside the Godot test runner and await a frame or two (e.g., using `yield(get_tree(), "idle_frame")`) before reading `get_global_rect()` values to validate actual rendered sizes on a CI agent with the target platform's render environment.

This balances fast, deterministic CI with a path for manual and frame-based validation where device-specific rendering differences matter.
