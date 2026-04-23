# CameraSpeaker

Send audio files to [thingino](https://thingino.com/) IP cameras for playback through their speaker.

## Features

- **Play audio files** — Send WAV, MP3, Opus, FLAC, AAC to the camera
- **Text-to-speech** — Speak text with attention chimes via thingino TTS
- **Built-in sounds** — Play the camera's pre-installed sound effects
- **Python API** — Use from your own scripts and automations
- **Auto-conversion** — Unsupported formats are converted via ffmpeg

## Installation

```bash
pip install -e .
```

Optionally install `ffmpeg` for automatic format conversion:
```bash
apt install ffmpeg
```

## CLI Usage

```bash
# Play an audio file
camera-speaker play alert.mp3 -v 80

# Text-to-speech (with attention chimes)
camera-speaker say "Hello world"

# Play a built-in sound
camera-speaker sound chime_1

# List built-in sounds
camera-speaker sounds

# Stop playback
camera-speaker stop
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host`, `-H` | Camera hostname | `camera2` |
| `--user`, `-u` | SSH user | `root` |
| `--port`, `-p` | SSH port | `22` |
| `--volume`, `-v` | Volume 0–100 | `60` |
| `--gain`, `-g` | Gain 0–31 | `20` |

## Python API

```python
from camera_speaker import say

# Basic usage
say("Hello world")

# With options
say("Intruder alert", host="mycamera", volume=100, gain=31)

# No chimes
say("Quiet message", chimes=0)

# Repeat the message
say("Important announcement", repeat=3)
```

## Configuration

Settings are resolved in order (highest priority first):

1. CLI arguments / function parameters
2. Environment variables (`CAMERA_HOST`, `CAMERA_USER`, `CAMERA_PORT`)
3. Config file (`~/.config/camera-speaker/config.ini`)
4. Defaults

### Config file example

```ini
[camera]
host = mycamera
user = root
port = 22
```

## Requirements

- Python 3.13+
- [paramiko](https://www.paramiko.org/) (SSH transport)
- SSH key-based access to the camera
- [thingino](https://thingino.com/) firmware on the camera
- Optional: `ffmpeg` for audio format conversion

## License

MIT
