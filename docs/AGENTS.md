# ArchiveAssistant

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> Every design decision should improve speed, accuracy, consistency, and long-term preservation.

---

# Project Overview

ArchiveAssistant is **not** a photo management application.

ArchiveAssistant is an **archival workbench**.

Its purpose is to assist with reviewing, organizing, and annotating scanned historical photographs before they are imported into long-term archive systems.

ArchiveAssistant owns the **working metadata**.

Immich and Plex own the **finished archive**.

---

# Workflow

```
Scanner
    ↓
Cropper
    ↓
ArchiveAssistant
    ↓
Review
    ↓
Metadata
    ↓
Metadata Export
    ↓
Immich
    ↓
Plex
```

ArchiveAssistant should never attempt to replace Immich or Plex.

Those applications already solve searching, browsing, sharing, facial recognition, mapping, albums, timelines, and long-term media management.

ArchiveAssistant focuses exclusively on preparing images for archival storage.

---

# Development Phase

Current Status:

- Production Alpha
- Core Architecture Stable
- Database Stable
- Metadata Foundation Complete
- Additive Development Phase

The foundation has been built.

Future development should extend existing systems rather than redesign them.

---

# Design Philosophy

ArchiveAssistant should always feel:

- Fast
- Predictable
- Safe
- Keyboard-first
- Efficient

If a feature requires additional clicks, typing, or interruption, reconsider the design.

The application should disappear behind the workflow.

The user should think about photographs—not software.

---

# Primary Goals

Every feature should improve one or more of the following:

- Review speed
- Metadata quality
- Workflow consistency
- Error prevention
- Long-term maintainability

Features should not be added simply because they are possible.

---

# Keyboard Philosophy

Keyboard is the primary interface.

Mouse support exists where appropriate but should never become required for common workflows.

Good workflow:

```
→
→
F
→
M
Tab
Tab
Ctrl+Enter
→
```

Poor workflow:

```
Click

Move Mouse

Click

Click

Move Mouse

Click
```

---

# Architecture Philosophy

Prefer:

- Small focused classes
- Single responsibility
- Composition over complexity
- Readable code
- Explicit behavior

Avoid:

- Giant utility classes
- Hidden side effects
- Clever code
- Premature abstraction

Simple code is preferred over smart code.

---

# Development Rules

Always:

- One logical feature per commit.
- Full file replacements when generating code.
- Preserve existing architecture.
- Read current files before modifying them.
- Keep GitHub as the project baseline.
- Maintain backward compatibility whenever practical.

Never:

- Rewrite unrelated systems.
- Perform large architectural changes without discussion.
- Introduce unnecessary dependencies.
- Break keyboard workflows.

---

# Sprint Scope

ArchiveAssistant follows a one logical feature per sprint philosophy.

Prefer additive changes over rewrites.

Preserve the existing architecture.

Resist implementing adjacent features unless explicitly requested.

If implementation naturally grows beyond the intended scope, stop and reassess before continuing.

Documentation-only or polish sprints should typically remain under approximately 300-400 new lines of code.

This is a guideline, not a strict limit.

Larger implementations are acceptable when they still represent a single logical subsystem, such as OCR, Relationships, or Similarity.

If additional capabilities begin appearing beyond the original sprint objective, defer them to a future sprint rather than expanding the current sprint.

## Smallest Useful Feature

When implementing a sprint, build the smallest version of the feature that future sprints can naturally extend.

ArchiveAssistant values:

- Extensible foundations
- Incremental development
- Small reviewable commits
- Long-term maintainability

over feature completeness.

## Architecture Consistency

Use the standard subsystem pattern when a feature needs a reusable core service:

```
Manager
    ↓
Models
    ↓
Optional Providers
    ↓
ReviewSession
    ↓
UI
```

Managers orchestrate.

Models remain simple and immutable where practical.

Helpers should be pure functions where practical.

ReviewSession coordinates workflows.

Dialogs remain thin.

Business logic belongs in `core`.

UI displays state but does not own business logic.

---

# User Experience Rules

Every new feature should answer:

- Does this reduce typing?
- Does this reduce clicks?
- Does this prevent mistakes?
- Does this improve consistency?
- Will Future Trent appreciate this?

If the answer is mostly "no", reconsider the feature.

---

# Metadata Philosophy

The database is the working copy.

It is not the final archive.

Metadata ultimately belongs inside the image whenever possible.

Supported future export targets include:

- EXIF
- IPTC
- XMP
- XMP Sidecars

ArchiveAssistant prepares metadata.

It does not permanently own metadata.

---

# AI Philosophy

AI assists.

Humans decide.

AI should:

- Suggest metadata
- OCR handwritten notes
- Detect faces
- Cluster duplicates
- Suggest dates
- Suggest locations

AI should never silently modify archival information.

The human remains the authority.

---

# Performance Philosophy

Large projects are expected.

Design for:

- 100,000+ photographs
- Fast startup
- Instant navigation
- Background work whenever possible

Small delays become significant over thousands of images.

Performance matters.

---

# Testing

Every completed feature should preserve:

- Review workflow
- Navigation
- Metadata editing
- Keyboard shortcuts
- Database integrity

Regression prevention is more valuable than adding features quickly.

---

# Validation

Before completing a task:

- Select the Python interpreter for the current environment.
- Do not assume `python` is available on the system PATH.
- If running inside Codex, use the active Codex runtime interpreter.
- If multiple interpreters are available, use the same interpreter that launches ArchiveAssistant.
- Run unit tests if available with the selected interpreter.
- Run compileall with the selected interpreter.
- Launch ArchiveAssistant with the selected interpreter.
- Verify successful startup.
- Clean generated runtime artifacts.
- Restore runtime-generated backup files if appropriate.
- Never leave the repository in a non-working state.
- Mention every file changed.
- Mention every command executed.

---

# Future Contributors

When making changes:

1. Understand the existing design.
2. Preserve project philosophy.
3. Keep changes focused.
4. Favor readability.
5. Respect the workflow.

Before implementing a sprint, ask:

- Is this still one logical feature?
- Am I solving today's problem rather than future hypothetical problems?
- Would this change still make sense after processing 10,000 family photographs?
- Can this capability be extended naturally in a future sprint?

ArchiveAssistant is intended to be maintained for many years.

Design accordingly.
