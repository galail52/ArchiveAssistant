# Local AI Configuration

ArchiveAssistant can validate a local AI connection for status and testing.

AI suggestions are available through an advisory client but are not automatically applied to metadata workflows.

AI tests do not modify metadata, OCR records, relationships, review state, or image files.

---

# Configuration

ArchiveAssistant reads AI settings from environment variables.

| Variable | Purpose | Example |
|----------|---------|---------|
| `ARCHIVEASSISTANT_AI_PROVIDER` | Provider adapter | `ollama`, `open_webui`, or `companyos` |
| `ARCHIVEASSISTANT_AI_ENDPOINT` | Provider base URL | `http://localhost:11434` |
| `ARCHIVEASSISTANT_AI_MODEL` | Default model for test prompts | `llama3.1` |
| `ARCHIVEASSISTANT_AI_ENABLED` | Enable or disable AI checks | `1` or `0` |
| `ARCHIVEASSISTANT_AI_TOKEN_FILE` | Local bearer-token file for CompanyOS | `C:\ArchiveAssistant\secrets\archiveassistant_token` |

If no settings are provided, ArchiveAssistant defaults to:

```text
ARCHIVEASSISTANT_AI_PROVIDER=ollama
ARCHIVEASSISTANT_AI_ENDPOINT=http://localhost:11434
ARCHIVEASSISTANT_AI_MODEL=
ARCHIVEASSISTANT_AI_ENABLED=1
```

---

# Ollama Example

```powershell
$env:ARCHIVEASSISTANT_AI_PROVIDER = "ollama"
$env:ARCHIVEASSISTANT_AI_ENDPOINT = "http://localhost:11434"
$env:ARCHIVEASSISTANT_AI_MODEL = "llama3.1"
```

Use the Command Palette:

- `AI Status`
- `Test AI Connection`
- `AI Test Prompt`

---

# Open WebUI Example

```powershell
$env:ARCHIVEASSISTANT_AI_PROVIDER = "open_webui"
$env:ARCHIVEASSISTANT_AI_ENDPOINT = "http://localhost:3000"
$env:ARCHIVEASSISTANT_AI_MODEL = "llama3.1"
```

Open WebUI deployments can vary. If your instance uses authentication or a different API path, keep AI disabled until an explicit authenticated adapter is added.

---

# Da-Server-AI / CompanyOS

CompanyOS exposes a dedicated advisory-only ArchiveAssistant API through the verified bridge.

Example:

```powershell
$env:ARCHIVEASSISTANT_AI_PROVIDER = "companyos"
$env:ARCHIVEASSISTANT_AI_ENDPOINT = "http://192.168.0.68:8766"
$env:ARCHIVEASSISTANT_AI_TOKEN_FILE = "C:\ArchiveAssistant\secrets\archiveassistant_token"
$env:ARCHIVEASSISTANT_AI_ENABLED = "1"
```

Do not hardcode the server address in the application.

Keep endpoint configuration outside the repository so the same checkout can run on different machines.

The CompanyOS provider supports `ocr_cleanup`, `back_interpretation`, `metadata_suggestion`, `description_draft`, `keyword_suggestion`, `consistency_check`, and `research_questions`. Results are structured suggestions with evidence and uncertainty. The provider has no API for saving, applying, deleting, merging, renaming, or approving archive records.

---

# Safety

AI validation is read-only.

The current AI commands only answer:

- which provider is configured
- which endpoint is configured
- whether the provider is reachable
- which models are available
- whether a simple test prompt returns a structured response

ArchiveAssistant does not automatically apply AI text to metadata.

Human approval remains required for any future AI-assisted metadata workflow.

---

# AI OCR Cleanup Review

After OCR has been run on an image, use the Command Palette action:

```text
Clean Latest OCR with AI
```

ArchiveAssistant sends only the latest OCR text to the configured advisory provider. The review dialog shows the original OCR beside the suggested cleanup, along with confidence, uncertainty, corrections, and warnings.

The cleanup is advisory only. ArchiveAssistant does not replace the OCR source text or save metadata automatically. The archivist may copy the cleaned transcription and decide whether or where to use it.
