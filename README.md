# CameraSpeaker

Send audio files to thingino IP cameras for playback through their speaker.

## Installation

```bash
pip install -e .
```

Optionally install `ffmpeg` for automatic format conversion:
```bash
apt install ffmpeg
```

## Usage

```bash
# Play an audio file
camera-speaker play alert.mp3 -v 80

# Text-to-speech
camera-speaker say "Hello world"

# Play a built-in sound
camera-speaker sound chime_1

# List built-in sounds
camera-speaker sounds

# Stop playback
camera-speaker stop
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host`, `-H` | Camera hostname | `camera2` |
| `--user`, `-u` | SSH user | `root` |
| `--port`, `-p` | SSH port | `22` |
| `--volume`, `-v` | Volume 0–100 | `60` |
| `--gain`, `-g` | Gain 0–31 | `20` |

## Configuration

Settings are resolved in order (highest priority first):

1. CLI arguments
2. Environment variables (`CAMERA_HOST`, `CAMERA_USER`, `CAMERA_PORT`)
3. Config file (`~/.config/camera-speaker/config.ini`)
4. Defaults
