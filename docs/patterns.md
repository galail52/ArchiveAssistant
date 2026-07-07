# Architecture Patterns

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> Architecture should make future features easier to add without making current workflows harder to understand.

---

# Purpose

This document codifies the subsystem pattern that has emerged across ArchiveAssistant.

Use this pattern when adding new core capabilities such as export formats, archive health checks, smart filters, OCR, image relationships, duplicate detection, AI suggestions, or future indexing systems.

The goal is not ceremony.

The goal is a predictable place for each responsibility.

---

# Standard Subsystem Shape

New systems should usually follow this flow:

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

Not every subsystem needs every layer.

Small features can stay small.

When the feature grows, split responsibilities along this shape instead of creating one large class.

---

# Managers

Managers orchestrate core behavior.

They should:

- coordinate models, helpers, providers, and database access
- expose a small API for ReviewSession
- stay independent of Qt widgets and dialogs
- avoid presentation labels and UI formatting
- keep destructive behavior explicit

Managers should not become giant utility objects.

If a manager starts calculating unrelated groups of behavior, introduce helpers or providers.

Examples:

- `ExportManager` selects the exporter for an `ExportJob`.
- `HealthManager` gathers provider output and builds a `HealthReport`.
- `SmartFilterManager` applies structured filters to project records.
- `OCRManager` coordinates OCR queue planning and engine execution.
- `RelationshipManager` creates, removes, and queries image relationships.
- `SimilarityManager` coordinates image fingerprinting, comparison, and grouping.
- `AIManager` selects local AI providers and returns structured responses.

---

# Models

Models represent structured data.

They should be immutable or simple where practical.

Good models:

- are easy to construct in tests
- do not know about widgets
- avoid hidden database writes
- keep names explicit
- can be passed safely between core layers

Examples:

- `ExportJob`
- `ExportResult`
- `ExportRecord`
- `HealthReport`
- `SmartFilter`
- `OCRJob`
- `OCRResult`
- `Relationship`
- `RelationshipType`
- `ImageFingerprint`
- `SimilarityMatch`
- `SimilarityGroup`
- `AIRequest`
- `AIResponse`
- `AISettings`

---

# Helpers

Helpers should be pure functions where practical.

They are best for small pieces of reusable logic that do not need object state.

Good helpers:

- accept input values
- return output values
- do not read or write the database
- do not import Qt
- are easy to test directly

Examples:

- metadata parsing helpers such as `parse_people`
- health math helpers such as percentage and completeness calculations
- future normalization or validation helpers

---

# Providers

Providers contribute grouped metrics or capabilities to a larger system.

Use providers when one manager needs to assemble several independent slices of information.

Providers should:

- collect one coherent category of data
- be read-only unless their purpose explicitly requires writes
- return plain values or simple dictionaries
- avoid UI labels and formatting
- be independently testable

Examples:

- Review health provider: review totals and status counts.
- Metadata health provider: missing metadata and completeness.
- Confidence health provider: confidence distribution.

Future provider candidates:

- OCR health provider
- duplicate detection provider
- front/back pairing provider
- people indexing provider
- restoration queue provider

---

# ReviewSession

`ReviewSession` coordinates workflows between core systems and the UI.

It should:

- own the current project and current image context
- delegate specialized behavior to managers
- expose simple workflow methods for the UI
- avoid direct widget or dialog imports
- decide when state should be saved

Examples:

- export preview delegates to `ExportManager`
- collection health delegates to `HealthManager`
- smart filter actions delegate to `SmartFilterManager`
- OCR queue planning delegates to `OCRManager`
- relationship operations delegate to `RelationshipManager`

If UI code needs a behavior, prefer adding a clear ReviewSession method instead of letting the dialog call core managers directly.

---

# UI And Dialogs

UI dialogs should remain thin.

They should:

- gather user choices
- display results
- return values
- stay keyboard-friendly
- avoid database writes
- avoid business rules

Business logic belongs in core packages, not dialogs.

Examples:

- command palette actions call `MainWindow` methods
- `MainWindow` calls `ReviewSession`
- selection dialogs return ids or values
- ReviewSession decides what to do with those ids or values

---

# Database

The database stores durable state.

It should:

- persist working review state and metadata
- use focused tables for durable subsystems
- avoid UI concepts
- keep schema changes additive when practical
- expose structured rows through core models where useful

Do not embed unrelated state inside metadata fields.

Examples:

- metadata templates are separate from image metadata
- relationships use a dedicated relationships table
- export reads use `ExportRecord`
- OCR persistence is deferred until the product needs durable OCR results

---

# Command Palette

The Command Palette exposes keyboard-first workflows.

Use it for actions that are important but not frequent enough for direct shortcuts.

Good command palette actions:

- call existing workflow methods
- keep keyboard focus predictable
- avoid duplicating shortcut behavior
- make advanced features discoverable

Examples:

- Export Preview / Dry Run
- Collection Health
- Smart Filters
- AI Status
- Test AI Connection
- OCR Status
- Queue Current for OCR
- Run OCR on Current Image
- Run Queued OCR
- Image Similarity Scan
- View Similar Images
- Pair Front / Back

---

# Safety And Human Approval

ArchiveAssistant is an archival workbench.

Destructive or metadata-changing workflows must remain human-controlled.

Default to:

- dry run before write
- preview before export
- queue before processing
- suggestions before metadata updates
- explicit confirmation before destructive actions

AI, OCR, export, and relationship systems should never silently rewrite history.

The human remains the authority.

---

# Additive Development

Features should be additive whenever possible.

Prefer:

- new focused packages
- new managers
- new models
- new provider seams
- new command palette entries
- small database tables for durable subsystem state

Avoid:

- broad rewrites
- mixing UI and core rules
- growing `ReviewSession` into implementation details
- storing unrelated state in metadata
- adding dependencies before the product needs them

---

# Current Subsystem Examples

## Export

Export follows the manager/model pattern.

- `ExportManager` coordinates export jobs.
- `ExportJob` describes what to export.
- `ExportResult` reports what happened.
- `ExportRecord` gives exporters a stable read model.

JSON and CSV can write output today.

Image-writing exporters remain dry-run stubs until destructive metadata writing is intentionally implemented.

## Health

Health uses providers to avoid one large metrics object.

- `HealthManager` orchestrates providers.
- `HealthReport` is the final immutable report.
- Health providers collect grouped read-only metrics.

The UI formats the report.

Core health logic does not know about dialog labels.

## Smart Filters

Smart filters are structured query definitions.

- `SmartFilterManager` lists and applies filters.
- `SmartFilter` contains the id, name, description, and predicate.

Filters return matching records.

They do not modify images or metadata.

## OCR

OCR provides a non-destructive extraction service.

- `OCRManager` coordinates queue planning and OCR engine execution.
- OCR engines are isolated behind a small engine interface.
- `TesseractEngine` is the first supported engine.
- `OCRQueue` tracks pending and completed work in memory.
- `OCRJob` models an OCR request.
- `OCRResult` models OCR output, errors, warnings, and engine details.

Tesseract is optional. If it is not installed, OCR reports the unavailable engine state without crashing.

OCR does not write metadata automatically.

## AI

AI provides a local-provider foundation for future human-approved suggestions.

- `AIManager` selects providers and coordinates status checks, model listing, and test prompts.
- `AIProvider` isolates provider-specific HTTP behavior.
- `AIRequest` models prompt input.
- `AIResponse` models structured success or failure.
- `AISettings` models provider type, endpoint, default model, and enabled state.

Ollama and Open WebUI are the first provider adapters.

AI does not write metadata automatically.

## Relationships

Relationships are a general-purpose subsystem.

- `RelationshipManager` creates, removes, and queries relationships.
- `Relationship` models a connection between images.
- `RelationshipType` defines relationship categories.

Front/back pairing is the first implemented relationship type.

The subsystem is designed to support future relationships such as negative/print, original/restored, and master/derivative.

## Similarity

Similarity is a non-destructive foundation for finding visually related images.

- `SimilarityManager` coordinates scanning, matching, and grouping.
- `FingerprintEngine` creates deterministic local image fingerprints.
- `ImageFingerprint` models the fingerprint for one image.
- `SimilarityMatch` models one candidate relationship between images.
- `SimilarityGroup` models connected candidate matches.

Duplicate detection is the first consumer of similarity results.

Similarity results are currently in-memory scan results. They do not modify files, metadata, review flags, or relationships.

---

# Rule Of Thumb

When adding a feature, ask:

1. What model represents the data?
2. What manager owns the behavior?
3. Are pure helpers enough for part of the logic?
4. Does this need providers to avoid manager growth?
5. What ReviewSession method should the UI call?
6. What command palette action exposes it?
7. What durable state, if any, belongs in the database?
8. Where does human approval happen?

If those answers are clear, the feature probably fits ArchiveAssistant.
