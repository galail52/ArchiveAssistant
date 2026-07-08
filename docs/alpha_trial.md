# Alpha Trial Guide

ArchiveAssistant is ready for a real-world alpha trial on a contained family photo collection.

The goal is to observe the workflow, not to perfect it during the trial.

Do not fix issues while running the trial. Log them first, then review the patterns afterward.

---

# Trial Size

Use a project with 500-1000 photos.

Choose a set that includes:

- clear fronts
- scanned backs
- duplicates or near-duplicates
- images needing research
- images needing restoration
- missing or uncertain metadata
- a few intentionally awkward filenames or ordering cases

Avoid using the only copy of irreplaceable originals.

ArchiveAssistant is designed to avoid modifying source image files, but alpha trials should still use backed-up working copies.

---

# Before Starting

1. Confirm the photo folder is backed up.
2. Launch ArchiveAssistant with the project interpreter.
3. Open the trial project.
4. Do a quick navigation pass through the first 20-30 images.
5. Confirm metadata editing opens, saves, and cancels as expected.
6. Confirm the Command Palette opens.
7. Confirm export preview is a dry run unless you explicitly choose a writing export.

---

# What To Record

For each issue, record:

- photo filename or image number
- what you were trying to do
- what happened
- what you expected
- shortcut or command used
- whether the issue blocked work
- whether it happened once or repeatedly
- approximate project size

Also record positive observations:

- workflows that felt fast
- shortcuts that felt natural
- places where ArchiveAssistant prevented a mistake
- places where the interface stayed out of the way

---

# Issue Categories

Use these categories when logging notes:

- Workflow
- Keyboard
- UI
- Metadata
- Relationships
- Dual Session
- OCR
- Similarity
- Export
- Performance
- Bug
- Feature Request

---

# Suggested Trial Flow

1. Review 100 photos using only navigation and review flags.
2. Add metadata to 50 photos.
3. Copy and paste metadata across a small related group.
4. Save and apply at least one metadata template.
5. Pair at least 20 front/back images.
6. Use Dual Session Review for a front/back matching pass.
7. Run Collection Health.
8. Run Smart Filters for missing metadata and review queues.
9. Run OCR status and a small OCR test if Tesseract is available.
10. Run Image Similarity Scan.
11. Run Export Preview / Dry Run.

Stop and log any issue that makes the next step confusing, slow, or risky.

---

# After The Trial

Review the log before changing code.

Look for:

- repeated friction
- missing keyboard paths
- unclear status wording
- slow operations
- metadata mistakes
- pairing mistakes
- cases where the app felt unsafe

Group issues by category and fix the highest-impact workflow problems first.

Do not turn every observation into a feature. Prefer small changes that improve speed, safety, and confidence.
