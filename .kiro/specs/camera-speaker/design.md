# CameraSpeaker — Design

## Architecture

CameraSpeaker is a single Python CLI tool (`camera-speaker`) that runs on the server and communicates with the camera over SSH. There is no daemon or server component — it's a direct command-line tool.

```
┌─────────────────────────┐          SSH/SCP           ┌──────────────────────────┐
│       Server             │ ──────────────────────────▶│       Camera (camera2)   │
│                          │                            │                          │
│  camera-speaker CLI      │   1. SCP file to /tmp/     │  /tmp/audio_xxx.opus     │
│  ┌──────────────────┐    │   2. SSH: play /tmp/...    │         │                │
│  │ Config loader     │    │   3. SSH: rm /tmp/...     │         ▼                │
│  │ Audio converter   │    │                            │  play → FIFO →  Speaker  │
│  │ SSH transport     │    │                            │  /run/prudynt/audio_out  │
│  │ Command builder   │    │                            │                          │
│  └──────────────────┘    │                            └──────────────────────────┘
│                          │
│  Optional: ffmpeg        │
│  (format conversion)     │
└─────────────────────────┘
```

## Components

### 1. CLI Interface (`cli.py`)

Entry point using `argparse`. Subcommands:

| Command | Description | Example |
|---------|-------------|---------|
| `play <file>` | Send and play an audio file | `camera-speaker play alert.mp3 -v 80` |
| `say <text>` | Text-to-speech | `camera-speaker say "Hello world"` |
| `sound <name>` | Play built-in sound | `camera-speaker sound chime_1` |
| `sounds` | List built-in sounds | `camera-speaker sounds` |
| `stop` | Stop current playback | `camera-speaker stop` |

Global options:
- `--host` / `-H` — Camera hostname (default: `camera2`)
- `--user` / `-u` — SSH user (default: `root`)
- `--port` / `-p` — SSH port (default: `22`)
- `--volume` / `-v` — Volume 0–100 (default: 60)
- `--gain` / `-g` — Gain 0–31 (default: 20)

### 2. SSH Transport (`transport.py`)

Handles all camera communication using `paramiko`:

- **`scp_upload(local_path, remote_path)`** — Transfer file to camera
- **`ssh_exec(command)`** — Execute command on camera, return stdout/stderr
- **`ssh_exec_detached(command)`** — Execute without waiting (for playback)

Connection is established once per invocation and reused.

### 3. Audio Converter (`converter.py`)

Handles format detection and conversion:

- **`needs_conversion(file_path)`** — Check if file needs conversion based on extension
- **`convert_to_opus(input_path)`** — Convert to Opus 16kHz mono via ffmpeg, returns temp file path

Compatible extensions (no conversion needed): `.wav`, `.pcm`, `.aac`, `.opus`, `.mp3`, `.flac`

### 4. Config (`config.py`)

Loads configuration with this priority:
1. CLI arguments (highest)
2. Environment variables (`CAMERA_HOST`, `CAMERA_USER`, `CAMERA_PORT`)
3. Config file (`~/.config/camera-speaker/config.ini`)
4. Defaults (lowest)

## Sequence Diagrams

### Play Audio File

```
User                CLI              Converter         Transport          Camera
 │                   │                  │                  │                 │
 │ play alert.mp3    │                  │                  │                 │
 │──────────────────▶│                  │                  │                 │
 │                   │ needs_conversion?│                  │                 │
 │                   │─────────────────▶│                  │                 │
 │                   │   No (.mp3 ok)   │                  │                 │
 │                   │◀─────────────────│                  │                 │
 │                   │                  │                  │                 │
 │                   │ scp_upload(file, /tmp/cs_xxx.mp3)   │                 │
 │                   │────────────────────────────────────▶│                 │
 │                   │                  │                  │  SCP transfer   │
 │                   │                  │                  │────────────────▶│
 │                   │                  │                  │                 │
 │                   │ ssh_exec("play -v 80 /tmp/cs_xxx.mp3 && rm /tmp/..") │
 │                   │────────────────────────────────────▶│                 │
 │                   │                  │                  │  play + cleanup │
 │                   │                  │                  │────────────────▶│
 │                   │                  │                  │                 │
 │  Done             │                  │                  │                 │
 │◀──────────────────│                  │                  │                 │
```

### Text-to-Speech

```
User                CLI              Transport          Camera
 │                   │                  │                 │
 │ say "Hello"       │                  │                 │
 │──────────────────▶│                  │                 │
 │                   │ ssh_exec('tell "Hello"')           │
 │                   │─────────────────▶│                 │
 │                   │                  │  tell "Hello"   │
 │                   │                  │────────────────▶│
 │  Done             │                  │                 │
 │◀──────────────────│                  │                 │
```

## File Layout

```
CameraSpeaker/
├── camera_speaker/
│   ├── __init__.py
│   ├── cli.py           # Argparse CLI entry point
│   ├── transport.py     # SSH/SCP communication
│   ├── converter.py     # Audio format detection & conversion
│   └── config.py        # Configuration loading
├── tests/
│   ├── test_converter.py
│   └── test_config.py
├── pyproject.toml
├── README.md
├── .gitignore
└── .kiro/
    └── specs/
        └── camera-speaker/
            ├── requirements.md
            ├── design.md
            └── tasks.md
```

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Camera unreachable | Print "Error: Cannot connect to {host}: {reason}" and exit 1 |
| SSH auth failure | Print "Error: SSH authentication failed for {user}@{host}" and exit 1 |
| ffmpeg not found | Print "Error: ffmpeg is required to convert {ext} files. Install with: apt install ffmpeg" and exit 1 |
| File not found | Print "Error: File not found: {path}" and exit 1 |
| Playback fails | Print stderr from camera and exit 1 |

## Dependencies

- **Python 3.13** (system Python)
- **paramiko** — SSH/SCP transport
- **ffmpeg** — Optional, only needed for converting non-compatible formats (system package)

## Security Considerations

- SSH key-based auth assumed (standard for embedded camera access)
- Temporary files on camera use unique names to avoid collisions
- Temp files are cleaned up after playback
- No secrets stored in the project — SSH keys are in `~/.ssh/`
