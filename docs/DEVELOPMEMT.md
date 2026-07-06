# Development Guide

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> Every development decision should support speed, accuracy, maintainability, and long-term preservation.

---

# Purpose

This document describes **how ArchiveAssistant is developed.**

It is intended for:

- Future maintainers
- AI coding assistants
- Contributors
- Future versions of ourselves

Following these guidelines keeps the project consistent as it grows.

---

# Development Philosophy

The project has moved beyond the prototype phase.

The architecture is considered stable.

Future work should be:

- additive
- incremental
- well-tested
- reversible

Large rewrites should be avoided unless absolutely necessary.

---

# Git Workflow

GitHub is the project's source of truth.

Development workflow:

```
Design
    ↓
Implement
    ↓
Test
    ↓
Commit
    ↓
Push
```

Every commit should leave the project in a working state.

Never accumulate large batches of unrelated changes.

---

# Commit Philosophy

One logical feature per commit.

Good:

```
Add metadata summary panel

Add undo support

Improve date validation
```

Bad:

```
Fix metadata
UI cleanup
Database changes
Keyboard shortcuts
Random bug fixes
```

Small commits are easier to:

- review
- test
- revert
- understand

---

# File Editing Philosophy

Prefer replacing complete files rather than generating partial snippets.

Reasons:

- easier review
- easier copy/paste
- fewer merge mistakes
- deterministic results

Large files should still remain focused.

If a file becomes difficult to understand, split it.

---

# Read Before Writing

Before modifying code:

1. Read the current implementation.
2. Understand existing architecture.
3. Preserve current behavior.
4. Modify only what is necessary.

Never assume file contents.

GitHub is the authoritative baseline.

---

# Coding Style

Prefer:

- descriptive names
- readable code
- explicit logic
- short methods
- small classes

Avoid:

- clever tricks
- deeply nested logic
- hidden side effects
- unnecessary abstractions

Code should be easy to understand six months later.

---

# Class Design

Every class should have one responsibility.

Examples:

ReviewSession

- coordinates review

Navigator

- moves through images

Database

- stores persistent information

MetadataState

- stores metadata

ViewState

- stores display state

Avoid classes that manage unrelated systems.

---

# Keyboard First

Keyboard is the primary interface.

Every repetitive task should be possible without touching the mouse.

When adding a feature, ask:

"Can this be completed from the keyboard?"

If not, reconsider the design.

---

# User Experience

Speed matters.

The user may review tens of thousands of photographs.

Small delays become significant.

Optimize for:

- fewer clicks
- fewer keystrokes
- fewer interruptions

---

# Database Rules

The database stores working information.

It should never become tightly coupled to the UI.

Database changes should include:

- migrations
- backward compatibility
- validation

Never break existing projects.

---

# Error Handling

Errors should:

- explain the problem
- avoid data loss
- preserve user work

Unexpected failures should never silently discard metadata.

---

# Testing Checklist

Before committing:

Application launches.

Project opens.

Images load.

Navigation works.

Review flags work.

Metadata edits save.

Undo works.

Database updates correctly.

Keyboard shortcuts still function.

---

# Performance

Performance is a feature.

Design for projects containing:

- tens of thousands of photographs

Avoid unnecessary work during:

- startup
- navigation
- metadata editing

Prefer lazy loading whenever practical.

---

# AI Development

AI should enhance the workflow.

AI should never replace human decisions.

Examples:

✔ OCR

✔ Face suggestions

✔ Duplicate detection

✔ Metadata suggestions

Not acceptable:

Automatically changing metadata without user approval.

---

# Future Features

When adding a feature, ask:

Does it:

- reduce clicks?
- reduce typing?
- prevent mistakes?
- improve consistency?
- scale to large archives?

If not, reconsider whether it belongs.

---

# Code Reviews

Every change should preserve:

- readability
- architecture
- keyboard workflow
- existing behavior

A working feature is not automatically a good feature.

Maintainability matters.

---

# Long-Term Vision

ArchiveAssistant is intended to remain useful for decades.

Design decisions should favor:

- simplicity
- stability
- clarity

Future maintainers should understand the code without reverse engineering it.

Good software is easy to change.

Great software is easy to understand.