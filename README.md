# ArchiveAssistant

> **A keyboard-first archival workbench for preserving family photographs.**
>
> ArchiveAssistant helps transform boxes of old photographs into a searchable, well-documented family archive.

---

## Why ArchiveAssistant?

Scanning photographs is easy.

Preserving their history is not.

Most photo management software assumes your pictures were taken yesterday on a smartphone.

ArchiveAssistant assumes you're opening a dusty box in the garage containing photographs from the last hundred years.

Those photographs deserve more than filenames and folders.

They deserve context.

Who is in the picture?

Where was it taken?

Why was it important?

Who wrote on the back?

ArchiveAssistant helps answer those questions while making the process as fast and enjoyable as possible.

---

## Philosophy

ArchiveAssistant is **not** a photo library.

It is an **archival workbench**.

Its job is to prepare photographs for permanent storage.

Once complete, the archive is imported into software designed for long-term browsing such as **Immich**.

ArchiveAssistant focuses on:

- Review
- Metadata
- Historical preservation
- Quality assurance
- Workflow efficiency

---

## Workflow

```
Garage Boxes
      │
      ▼
Scan Fronts
      │
      ▼
Auto Crop
      │
      ▼
ArchiveAssistant

    ├── Review
    ├── Pair Fronts & Backs
    ├── Metadata
    ├── OCR
    ├── Restoration Queue

      │
      ▼
Metadata Export
      │
      ▼
Immich
      │
      ▼
Permanent Family Archive
```

Every photograph should ideally be processed once.

Every piece of metadata should be entered once.

---

## Features

### Review

- Rotate photographs
- Favorite images
- Mark restoration candidates
- Flag photographs with backs
- Research tracking
- Delete tracking
- Undo support

### Metadata

- People
- Events
- Locations
- Dates
- Keywords
- Notes
- Confidence ratings

### Navigation

- Keyboard-first workflow
- Command Palette
- Thumbnail strip
- Resume previous session
- Find by filename
- Jump helpers

### Safety

- Automatic SQLite backups
- Persistent review state
- Project health checks
- Resume exactly where you left off

---

## Design Goals

ArchiveAssistant is designed around five principles.

### Fast

The application should disappear behind the workflow.

### Keyboard First

The mouse should always be optional.

### Safe

Autosave everything.

Never lose work.

### Simple

Small focused tools.

Clear responsibilities.

### Future Proof

Historical archives should remain usable for generations.

---

## Project Status

Current Status:

**Production Alpha**

Current focus:

- Metadata workflow polish
- Metadata export
- AI-assisted archival tools

The core architecture is considered stable.

Future development is primarily additive.

---

## Documentation

Project documentation can be found in the `docs` directory.

- Architecture
- Architecture Patterns
- Development Guide
- Keyboard Workflow
- Metadata Philosophy
- Project Roadmap
- Recommended Workflow

These documents explain both how ArchiveAssistant works and why it was designed this way.

---

## Long-Term Vision

ArchiveAssistant exists for one reason:

To make preserving family history achievable.

The software should never become the focus.

The photographs—and the stories they contain—should remain at the center of every design decision.

---

## Contributing

Contributions are welcome.

Before making significant architectural changes, please read:

- `AGENTS.md`
- `docs/architecture.md`
- `docs/development.md`

These documents describe the project's philosophy and development practices.

---

## License

*Coming soon.*

---

> *"What information would someone one hundred years from now wish had been recorded?"*
>
> Every feature in ArchiveAssistant is built to help answer that question.
