# Project Requirements

This document acts as the definitive source of truth for the game's features, logic, UI dimensions, and constraints. When a subagent creates a feature or refactors code, it MUST consult this document to ensure strict adherence to the project's vision.

## 1. Core Mechanics
- Describe the core gameplay loop here.

## 2. Visuals and Layout
- Describe the UI layout, scaling, and dimensions here.

## 3. Data and Persistence
- Describe save data structure, player prefs, etc.

## 4. Platform Specifics
- Describe Android/iOS/Web specifics here.

## 5. Asset Management and Git Storage
- **Template Starter Assets:** Core template starter assets located in `game/assets/fonts/` (such as `DejaVuSans.ttf`, `NotoSansSymbols-Regular.ttf`) and `game/assets/icons/` (such as `icon.png`, `OpenGameStack.png`) are stored directly in Git as standard binary blobs. This prevents HTTP 404 pointer retrieval failures when new repositories are instantiated using GitHub's "Use this template" feature.
- **User-Added Binary Assets:** User-added binary media (such as large audio files, 3D models, textures outside the starter directories, and binary archives) continue to use Git LFS tracking per `.gitattributes`. Developers and agents adding large binary assets must have Git LFS configured (`git lfs install`).

