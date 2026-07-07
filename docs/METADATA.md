# Metadata Philosophy

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> Metadata is the most valuable part of a historical archive.

---

# Purpose

A scanned photograph is only an image.

Metadata transforms that image into history.

Without metadata:

- people become anonymous
- places become forgotten
- events lose context
- family history disappears

ArchiveAssistant exists to preserve that context.

---

# Working Metadata

ArchiveAssistant stores metadata in its database while work is in progress.

The database is the project's working copy.

It is intentionally separate from the image files during review.

Benefits include:

- Fast editing
- Easy corrections
- Undo support
- Flexible workflows
- Safe experimentation

The database is not the final archive.

---

# Final Metadata

Once review is complete, metadata should be written into the photographs whenever possible.

Supported export targets include:

- EXIF
- IPTC
- XMP
- XMP Sidecars

The image should carry its own history.

ArchiveAssistant prepares the metadata.

The image ultimately owns it.

---

# Metadata Fields

Current metadata includes:

- People
- Event
- Location
- Date Taken
- Keywords
- Notes
- Note Author
- Confidence

Future fields may be added as archival needs evolve.

---

# Metadata Power Tools

ArchiveAssistant supports reusable metadata templates for repeated contexts such as events, locations, or family groups.

Templates are stored separately from image metadata and can be managed from the Command Palette:

- Save Current Metadata as Template
- Apply Metadata Template
- Rename Metadata Template
- Delete Metadata Template

Templates currently include People, Event, Location, Date Taken, Keywords, Notes, Note Author, and Confidence.

Recent values for People, Event, Location, and Keywords are remembered per project in the database. Metadata entry uses those recent values for local, case-insensitive auto-complete.

The metadata clipboard has two modes:

- `C` / `P` copy and paste all metadata fields.
- Command Palette actions can copy and paste only selected fields.

---

# Review Flags

Review flags describe the condition of the photograph.

Current review flags:

- Favorite
- Has Back
- Needs Restore
- Needs Research
- Delete

Review flags are workflow tools.

They are not historical metadata.

---

# Confidence

Confidence represents how certain the archivist is about the information.

Example:

★★★★★

Known with high confidence.

Example:

★★☆☆☆

Likely correct.

Needs verification.

Example:

★☆☆☆☆

Best available guess.

Should be treated cautiously.

Confidence allows uncertain historical information to be preserved without presenting it as fact.

---

# Unknown vs Blank

Blank means:

"I have not researched this."

Unknown means:

"I researched this and the answer is unknown."

These are different historical states.

ArchiveAssistant should preserve that distinction whenever practical.

---

# Notes

Notes exist for information that does not fit neatly into structured fields.

Examples:

- Family stories
- Handwritten captions
- Research observations
- Conflicting information
- Future research ideas

Notes should never replace structured metadata when structured data is available.

---

# Keywords

Keywords improve future searching.

Keywords should describe:

- activities
- objects
- locations
- organizations
- themes

Avoid duplicating information already stored elsewhere.

Example:

Person belongs in People.

Do not repeat the same name as a keyword.

---

# Dates

Historical archives frequently contain incomplete dates.

ArchiveAssistant intentionally supports partial dates.

Examples:

```
1958

1958-07

1958-07-15
```

Unknown dates should remain unknown rather than guessed.

Historical accuracy is more important than completeness.

---

# Locations

Locations should represent where the photograph was taken whenever known.

When exact locations are unavailable:

General locations are preferable to incorrect locations.

Example:

```
Murray, Utah
```

is preferable to

```
Unknown
```

if the city is known.

---

# People

People should represent individuals visible within the photograph.

Names should remain consistent throughout the archive.

People are entered as comma-separated free text.

Example:

```
John Smith, Mary Smith, Bill
```

ArchiveAssistant parses that text into individual people for summaries, health reporting, autocomplete, and export support without requiring manual tag creation.

Future versions may support:

- autocomplete
- person database
- face suggestions
- relationship mapping

---

# Events

Events describe why the photograph exists.

Examples:

- Wedding
- Family Reunion
- Graduation
- Christmas
- Vacation

Events often provide more historical context than dates alone.

---

# AI Assistance

AI should assist metadata creation.

Examples:

- OCR handwritten notes
- Detect faces
- Suggest locations
- Suggest dates
- Describe scenes
- Detect duplicates

AI suggestions must always require human approval.

Historical accuracy remains a human responsibility.

Current OCR foundation:

- OCR jobs can be queued from the Command Palette.
- OCR status is available from the Command Palette.
- No OCR engine is integrated yet.
- OCR does not modify metadata automatically.
- Future OCR text must require human approval before it is used as metadata.

---

# Export Philosophy

ArchiveAssistant should support multiple export formats.

The export layer should remain independent from metadata entry.

Adding a new exporter should never require changing the metadata model.

Current export foundation:

- JSON export writes a project metadata file.
- CSV export writes a project metadata spreadsheet-friendly file.
- XMP sidecar, EXIF, and IPTC exporters are dry-run stubs only.
- Export preview is available from the Command Palette.

Export warnings currently flag missing People, Date, Location, Delete, and Needs Research.

Image-writing exports must remain human-controlled and non-destructive until explicitly implemented.

---

# Long-Term Preservation

Metadata should outlive software.

The ultimate goal is that future software can understand the photographs without requiring ArchiveAssistant.

ArchiveAssistant prepares metadata.

It does not own history.

---

# Guiding Principle

Every metadata field should answer one question:

"What information would someone 100 years from now wish had been recorded?"

If the answer is "yes," it probably belongs in the archive.
