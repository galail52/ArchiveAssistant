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

- Run unit tests if available.
- Run compileall.
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

ArchiveAssistant is intended to be maintained for many years.

Design accordingly.