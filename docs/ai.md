# Local AI Configuration

ArchiveAssistant can validate a local AI connection for status and testing.

AI is not connected to metadata workflows yet.

AI tests do not modify metadata, OCR records, relationships, review state, or image files.

---

# Configuration

ArchiveAssistant reads AI settings from environment variables.

| Variable | Purpose | Example |
|----------|---------|---------|
| `ARCHIVEASSISTANT_AI_PROVIDER` | Provider adapter | `ollama` or `open_webui` |
| `ARCHIVEASSISTANT_AI_ENDPOINT` | Provider base URL | `http://localhost:11434` |
| `ARCHIVEASSISTANT_AI_MODEL` | Default model for test prompts | `llama3.1` |
| `ARCHIVEASSISTANT_AI_ENABLED` | Enable or disable AI checks | `1` or `0` |

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

# Da-Server-AI Placeholder

For a future Da-Server-AI setup, point ArchiveAssistant at the local service endpoint exposed by that server.

Example placeholder:

```powershell
$env:ARCHIVEASSISTANT_AI_PROVIDER = "ollama"
$env:ARCHIVEASSISTANT_AI_ENDPOINT = "http://da-server-ai.local:11434"
$env:ARCHIVEASSISTANT_AI_MODEL = "family-history"
```

Do not hardcode the server address in the application.

Keep endpoint configuration outside the repository so the same checkout can run on different machines.

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
