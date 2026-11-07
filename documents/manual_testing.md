# Manual Testing Guide

This document outlines the strict manual testing procedures required before any release candidate can be deployed.

## Test 0.1: OpenGameStack Tool Manifest Verification
- **Step 1:** Verify `ogs_stack.json` exists in the repository root.
- **Step 2:** Validate that `ogs_stack.json` contains valid JSON declaring Godot engine version `4.7.2`.
- **Expected:** Manifest is present, valid JSON, and compatible with the OGS Launcher.

## Test 0.2: Starter Assets and Git LFS Verification
- **Step 1:** In the repository root, run `git lfs ls-files`.
- **Expected:** Verify that zero starter assets in `game/assets/fonts/` or `game/assets/icons/` appear in the output. Starter fonts and icons must be tracked directly in Git rather than via Git LFS pointers.
- **Step 2:** Inspect the size and headers of starter assets (for example, `game/assets/icons/icon.png` and `game/assets/fonts/DejaVuSans.ttf`).
- **Expected:** Files are full binaries (icon has PNG magic header `\x89PNG\r\n\x1a\n` and size > 1 KB; font has TrueType binary structure and size > 1 KB), not 130-byte LFS pointer stubs starting with `version https://git-lfs.github.com/spec/v1`.
- **Step 3:** (Template Instantiation Verification) Instantiate a fresh test repository from this template on GitHub using "Use this template" or clone without LFS endpoints.
- **Expected:** Godot headless editor import (`godot --headless --editor --quit --path game`) succeeds without 404 asset download failures or missing font/icon resource errors.


## Test 1.0: Launch & Boot
- **Step 1:** Open the app.
- **Expected:** The app boots to the main menu without crashing.
