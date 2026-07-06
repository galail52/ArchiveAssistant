# Project History

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> This document explains the major design decisions that shaped the project.

---

# Why ArchiveAssistant Exists

The project began with a simple problem.

Thousands of family photographs needed to be scanned, organized, annotated, and preserved.

Existing software solved pieces of the problem.

None solved the complete workflow.

The goal was never to replace existing photo libraries.

The goal was to create the missing step between scanning and long-term archival storage.

---

# Why a Desktop Application?

Historical archives are often:

- Very large
- Stored locally
- Sensitive
- Long-lived

A desktop application provides:

- Speed
- Offline operation
- Local ownership
- Better keyboard workflows
- Better handling of large archives

No cloud account should be required to preserve family history.

---

# Why Python?

Python was chosen because it provides:

- Rapid development
- Excellent image libraries
- Strong SQLite support
- Good AI ecosystem
- Cross-platform capability

Performance-critical code can always be optimized later.

Correct architecture is more valuable than premature optimization.

---

# Why Qt / PySide?

ArchiveAssistant is intended to feel like a native desktop application.

Qt provides:

- Mature widgets
- Excellent keyboard support
- Cross-platform compatibility
- Long-term stability

The application is designed around desktop productivity rather than web technologies.

---

# Why SQLite?

SQLite provides nearly everything the project requires.

Benefits include:

- Zero configuration
- Excellent reliability
- Simple backups
- High performance
- Portable projects

Projects remain self-contained.

No separate database server is required.

---

# Why Database-First Metadata?

Many photo applications immediately write metadata into image files.

ArchiveAssistant intentionally does not.

Instead:

```
Image

+

SQLite Database

↓

Review

↓

Metadata

↓

Export

↓

Embedded Metadata
```

Reasons:

- Easier editing
- Undo support
- Faster iteration
- Safer experimentation
- Better recovery

The database is the working copy.

The exported image becomes the permanent copy.

---

# Why Keyboard-First?

Large archival projects involve repetitive work.

Thousands of mouse movements become exhausting.

The application was intentionally designed so that most work can be completed without leaving the keyboard.

Every shortcut exists to reduce friction.

---

# Why Full File Replacements?

During development, complete file replacements were preferred over partial code snippets.

Reasons:

- Easier review
- Fewer merge mistakes
- Clearer commits
- Predictable changes
- Simpler collaboration

This approach dramatically reduced accidental regressions.

---

# Why Small Commits?

Development follows a simple rule:

One logical feature.

One commit.

Benefits include:

- Easier testing
- Easier rollback
- Cleaner history
- Better documentation

Small commits encourage thoughtful development.

---

# Why So Much Documentation?

Documentation was intentionally written early.

Not because the project is finished.

Because architecture is easiest to document while the reasoning is still fresh.

The documentation exists to preserve decisions, not just implementation.

---

# Why Immich?

Immich already excels at:

- Searching
- Albums
- Maps
- Timelines
- Sharing
- Mobile access

Recreating those features would duplicate years of work.

ArchiveAssistant prepares photographs.

Immich presents them.

Each application focuses on its strengths.

---

# Why Not Build Everything?

One of the earliest design decisions was that ArchiveAssistant should remain focused.

Many ideas were intentionally rejected.

Examples include:

- Full photo library
- Cloud storage
- Built-in image editor
- Genealogy software
- Backup software

Existing applications already solve those problems well.

ArchiveAssistant fills the gap they leave behind.

---

# Why AI Assistance Instead of AI Automation?

Historical archives deserve accuracy.

AI is extremely useful for:

- OCR
- Face suggestions
- Duplicate detection
- Metadata suggestions

However...

History should never be rewritten automatically.

Every AI suggestion requires human approval.

The archivist remains the authority.

---

# The Turning Point

Early versions of ArchiveAssistant focused primarily on reviewing photographs.

As development continued, the project's purpose became clearer.

ArchiveAssistant was not simply reviewing photographs.

It was preserving history.

That realization influenced every major architectural decision that followed.

---

# Development Philosophy

Several principles emerged naturally during development.

- Small focused classes.
- Keyboard-first workflows.
- Autosave everything.
- Eliminate unnecessary clicks.
- Preserve user trust.
- Keep architecture simple.

These principles now guide every future feature.

---

# Looking Forward

The project has reached a stable foundation.

Future work will focus on:

- Workflow refinement
- Metadata export
- AI assistance
- Large archive performance
- Long-term maintainability

The architecture is intended to evolve gradually rather than through major rewrites.

---

# Final Reflection

Software has a limited lifespan.

Family history does not.

Every design decision in ArchiveAssistant ultimately serves one purpose:

To ensure that future generations inherit not only photographs, but the stories behind them.