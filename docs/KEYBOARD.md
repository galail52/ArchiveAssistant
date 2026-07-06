# Keyboard Workflow

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> The keyboard is the primary interface for ArchiveAssistant.

---

# Philosophy

ArchiveAssistant is designed around continuous keyboard-driven review.

The mouse is available when needed, but common workflows should never require it.

The ideal review session allows the user to keep one hand on the arrow keys and the other near the primary review shortcuts.

---

# Design Principles

Every shortcut should be:

- Easy to remember
- Easy to reach
- Consistent
- Difficult to press accidentally

Shortcuts should rarely change once established.

Muscle memory is valuable.

---

# Workflow

Typical review session:

```
→
→
F
→
R
→
M
Tab
Tab
Ctrl+Enter
→
→
```

The user should spend their time thinking about photographs, not navigating software.

---

# Navigation

| Shortcut | Action |
|----------|--------|
| ← | Previous Image |
| → | Next Image |
| Space | Next Image |
| Home | First Image |
| End | Last Image |
| Page Up | Back 10 Images |
| Page Down | Forward 10 Images |
| Ctrl + ← | Back 50 Images |
| Ctrl + → | Forward 50 Images |

---

# Review Flags

| Shortcut | Action |
|----------|--------|
| F | Favorite |
| B | Has Back |
| R | Needs Restore |
| Y | Needs Research |
| X | Delete |
| Ctrl + Z | Undo |

Review actions should require only a single keystroke whenever practical.

---

# Metadata

| Shortcut | Action |
|----------|--------|
| M | Open Metadata |
| Ctrl + S | Save Metadata |
| Ctrl + Enter | Save While Editing Notes |
| Esc | Cancel Metadata |

Metadata entry should be optimized for keyboard-only operation.

---

# Image View

| Shortcut | Action |
|----------|--------|
| 1 | Fit |
| 2 | 100% |
| 3 | 200% |
| 4 | 400% |
| + | Zoom In |
| - | Zoom Out |
| Shift + Arrow | Pan |
| A | Rotate Left |
| D | Rotate Right |

View controls should never modify archival information.

They only affect presentation.

---

# Command Palette

| Shortcut | Action |
|----------|--------|
| G | Command Palette |

The Command Palette is intended for uncommon operations.

Common review actions should never require opening the Command Palette.

---

# Keyboard Priorities

Priority 1

Continuous review.

Example:

```
→
→
F
→
B
→
```

Priority 2

Metadata entry.

Example:

```
M

Tab

Tab

Ctrl+Enter
```

Priority 3

Navigation.

Large projects require fast movement.

Examples:

- Jump 10
- Jump 50
- Find Filename
- First Unreviewed

---

# Shortcut Selection

Whenever possible:

Single key

↓

Frequently used

Modifier required

↓

Occasionally used

Command Palette

↓

Rarely used

This minimizes hand movement during long review sessions.

---

# Reserved Keys

Some keys remain intentionally unused.

These provide room for future development.

Possible future shortcuts:

| Key | Planned Use |
|-----|--------------|
| C | Copy Metadata |
| P | Paste Metadata |
| T | Metadata Templates |
| O | OCR |
| L | Location Templates |
| N | Person Templates |

Reserved keys should only be assigned after careful consideration.

---

# Future Keyboard Goals

Future development should continue reducing reliance on the mouse.

Potential improvements include:

- Metadata templates
- Copy previous metadata
- Copy selected fields
- AI suggestions
- Quick accept AI suggestions

Every new shortcut should improve workflow without increasing complexity.

---

# Accessibility

Keyboard navigation should remain fully functional.

Focus order should always be logical.

Dialogs should:

- open focused
- tab correctly
- save without mouse interaction
- return focus to the image viewer

---

# Long-Term Goal

A user reviewing thousands of photographs should be able to work for hours without touching the mouse.

The keyboard is not a convenience feature.

It is the primary interface.