# ArchiveAssistant Workflow

> **Mission Statement**
>
> ArchiveAssistant exists to help humans produce the highest-quality historical archive with the fewest possible keystrokes.
>
> This document describes the recommended archival workflow from a box of photographs to a permanent digital archive.

---

# Overview

ArchiveAssistant is one part of a larger archival pipeline.

Every stage has a specific responsibility.

```
Physical Archive

↓

Scanner

↓

Cropper

↓

ArchiveAssistant

↓

Metadata Export

↓

Immich

↓

Long-Term Preservation
```

The goal is to perform each task exactly once.

Avoid revisiting photographs whenever possible.

---

# Step 1 — Preparation

Organize photographs before scanning.

Recommended:

- Remove duplicates when obvious.
- Keep groups together.
- Preserve original ordering whenever possible.
- Keep envelopes and written notes.

Historical context is often more valuable than perfect organization.

---

# Step 2 — Scan Fronts

Scan every photograph front.

Goals:

- Maximum practical quality.
- Consistent orientation.
- Consistent file naming.
- No cropping.

Cropping is performed later.

Scanning should remain fast.

---

# Step 3 — Auto Crop

Run photographs through the cropper.

The cropper should:

- Detect photographs.
- Straighten images.
- Crop borders.
- Preserve originals.

The cropper prepares photographs.

It should never discard data.

---

# Step 4 — Review

Open the project in ArchiveAssistant.

Primary tasks:

- Rotate images.
- Mark favorites.
- Mark photographs with backs.
- Mark restoration candidates.
- Flag research items.
- Remove duplicates if appropriate.

This stage is intended to be almost entirely keyboard driven.

---

# Step 5 — Scan Backs

Scan the reverse side of photographs marked as having writing.

Backs should remain linked to their corresponding fronts.

Future OCR will extract handwritten information automatically when possible.

---

# Step 6 — Pair Fronts and Backs

Associate:

Front

↓

Back

The pair should remain together throughout the remainder of the workflow.

Future exports should preserve this relationship.

---

# Step 7 — Metadata

Add historical information.

Examples:

- People
- Location
- Event
- Date
- Keywords
- Notes

Metadata should describe the photograph.

Review flags describe the workflow.

These are intentionally separate.

---

# Step 8 — Restoration Queue

Photographs requiring restoration should be flagged.

ArchiveAssistant does not restore photographs.

Instead it prepares restoration work.

Possible future integrations:

- Topaz
- Photoshop
- ComfyUI
- Custom AI workflows

---

# Step 9 — Export

When review is complete:

Write metadata into:

- EXIF
- IPTC
- XMP
- XMP Sidecars

Optional exports:

- CSV
- JSON

The image should become self-describing.

---

# Step 10 — Import

Import completed photographs into Immich.

Immich becomes the permanent browsing experience.

Responsibilities move from:

ArchiveAssistant

↓

Immich

ArchiveAssistant remains the project workspace.

Immich becomes the archive.

---

# Future Workflow

Eventually the workflow may become:

```
Garage Boxes

↓

Scan

↓

Crop

↓

Review

↓

OCR

↓

AI Suggestions

↓

Metadata

↓

Restoration Queue

↓

Export

↓

Immich

↓

Family Archive
```

AI assists.

Humans approve.

---

# Guiding Principles

Every photograph should ideally be processed once.

Every piece of metadata should be entered once.

Every restoration should happen once.

Every export should happen once.

Avoid duplicate work whenever possible.

---

# Success

A successful project is not measured by:

- Number of photographs scanned.
- Number of AI features.
- Number of metadata fields.

It is measured by one question:

**Can someone understand these photographs fifty or one hundred years from now without asking the original owner?**

If the answer is yes, the archive has succeeded.