---
name: Bug report
about: Report a defect, incorrect game logic, UI glitch, or broken mechanic
title: ''
labels: 'bug'
assignees: ''
---

<!-- Include if blocked by prior work: **Depends on #<issue_number>** -->

### 1. Problem & Context
A concise explanation of the problem, reproduction steps, observed behavior, and expected behavior.

**Reproduction Steps:**
1. 
2. 
3. 

**Observed Behavior:**
<!-- What actually happened -->

**Expected Behavior:**
<!-- What should have happened per documents/requirements.md -->

### 2. Technical Scope & Affected Files
Direct references to files, scenes, or autoloads that need modification or investigation:
- `game/scripts/<script_name>.gd`
- `game/scenes/<scene_name>.tscn`
- `game/autoloads/<autoload_name>.gd`
- `game/tests/<test_name>.gd`

### 3. Acceptance Criteria

#### [Component / Fix Area]
- [ ] Describe the expected behavior or fix

#### Automated Tests (`game/tests/`)
- [ ] Add or update unit test cases verifying the fix.
- [ ] Ensure all existing automated test suites pass without regressions (`Test Results: X Passed, 0 Failed`).

#### Documentation Coordination (Mandatory per documents/reviewing_and_merging_prs.md)
- [ ] Update `documents/requirements.md` if requirements were ambiguous or changed.
- [ ] Update `documents/manual_testing.md` with regression test cases.
- [ ] Update `README.md` if user-facing controls, rules, or visuals were modified.
