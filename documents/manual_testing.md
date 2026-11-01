# Manual Testing Guide

This document outlines the strict manual testing procedures required before any release candidate can be deployed.

## Test 0.1: OpenGameStack Tool Manifest Verification
- **Step 1:** Verify `ogs_stack.json` exists in the repository root.
- **Step 2:** Validate that `ogs_stack.json` contains valid JSON declaring Godot engine version `4.7.2`.
- **Expected:** Manifest is present, valid JSON, and compatible with the OGS Launcher.

## Test 1.0: Launch & Boot
- **Step 1:** Open the app.
- **Expected:** The app boots to the main menu without crashing.
