# ArchiveAssistant Architecture

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> Every architectural decision should support speed, accuracy, maintainability, and long-term preservation.

---

# Overview

ArchiveAssistant follows a layered architecture.

```
           User
             │
             ▼
      Main Window / UI
             │
             ▼
     Project Controller
             │
             ▼
      Review Session
             │
 ┌───────────┼────────────┐
 │           │            │
 ▼           ▼            ▼
Database  Navigator   View State
 │
 ▼
Metadata
Review State
```

Each layer has a single responsibility.

Higher layers coordinate.

Lower layers own data.

---

# Core Principles

Every class should have one clear purpose.

Avoid "god classes."

If a class starts managing unrelated responsibilities, split it.

The goal is that every file can be understood independently.

---

# UI Layer

Responsible for:

- Displaying information
- Receiving user input
- Showing dialogs
- Keyboard shortcuts
- Status updates

The UI should never contain business logic.

If a review rule exists, it belongs elsewhere.

---

# Project Controller

Responsible for:

- Opening projects
- Closing projects
- Health checks
- Database startup
- Project lifecycle

The controller manages projects.

It does not manage review behavior.

---

# Review Session

The ReviewSession is the heart of ArchiveAssistant.

It coordinates:

- Current image
- Navigation
- Review state
- Metadata
- Database persistence
- Undo
- View state

It should never contain user interface code.

It answers questions like:

- What image is selected?
- What is its metadata?
- What happens when the user presses Favorite?
- What should be saved?

---

# Database Layer

The database owns persistent information.

Examples:

- Review state
- Metadata
- Resume location
- Statistics
- Health information

The database should never know about widgets.

It stores information.

Nothing more.

---

# Review State

ReviewState represents review decisions.

Examples:

- Favorite
- Has Back
- Needs Restore
- Needs Research
- Delete
- Rotation

These describe the image itself.

---

# Metadata State

MetadataState represents descriptive information.

Examples:

- People
- Event
- Location
- Date
- Keywords
- Notes
- Confidence

Metadata should remain independent from review flags.

---

# View State

ViewState exists only while ArchiveAssistant is running.

Examples:

- Zoom
- Pan
- Fit
- Rotation display

ViewState affects presentation.

It does not modify archival information.

---

# Navigator

Navigator knows how to move through images.

Examples:

- Next
- Previous
- Jump
- First
- Last

ReviewSession decides *when* to navigate.

Navigator decides *how*.

---

# Command System

Commands are centralized.

Each command contains:

- Name
- Category
- Shortcut
- Callback
- Enabled state

This allows:

- Command Palette
- Keyboard shortcuts
- Future menus
- Future toolbars

to all execute the same command.

No duplicated logic.

---

# Dialog Philosophy

Dialogs gather information.

Dialogs should not update the database directly.

Dialogs return values.

ReviewSession decides what to do with those values.

---

# Keyboard Philosophy

Keyboard is the primary workflow.

The mouse should never be required for repetitive work.

Every shortcut should have a clear purpose.

Shortcuts should remain stable over time.

---

# Persistence

ArchiveAssistant stores:

- Review state
- Metadata
- Resume position

Everything else should be reconstructable.

Persistent state should be minimized.

---

# Error Handling

Errors should be:

- Predictable
- Recoverable
- Informative

The application should never silently lose work.

Backups exist to prevent corruption.

Undo exists to prevent mistakes.

---

# Future Architecture

Future systems should plug into the existing design.

Examples:

```
ReviewSession
        │
        ├── AI Assistant
        ├── Metadata Export
        ├── OCR
        ├── Duplicate Detection
        └── Face Detection
```

New systems should extend ReviewSession rather than replace it.

---

# Architectural Rule

Before adding a feature, ask:

> Which existing class naturally owns this responsibility?

If the answer is "none," create a new focused class.

If the answer is "several," reconsider the design.

The goal is not fewer files.

The goal is clearer responsibilities.