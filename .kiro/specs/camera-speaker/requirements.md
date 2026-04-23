# CameraSpeaker — Requirements

## Overview

CameraSpeaker is a tool that allows a user to send audio files from their server to a thingino-based IP camera for playback through its speaker. The camera runs prudynt-t which exposes an audio output FIFO at `/run/prudynt/audio_out` and a `play` shell wrapper.

## Target Environment

- **Server**: Linux (x86-64), IP `10.0.0.78`
- **Camera**: Thingino firmware on Ingenic T23/T31 (MIPS), hostname `camera2`
- **Camera audio interface**: prudynt FIFO at `/run/prudynt/audio_out`, `play` command
- **Supported formats on camera**: WAV, PCM (s16le), AAC, Opus, MP3, FLAC (16kHz mono)
- **Connectivity**: SSH access to camera, NFS share at `/mnt/nfs_share` → `/mnt/nfs`

## User Stories

### US-1: Send and Play an Audio File

**As a** user  
**I want to** send an audio file from my server to the camera and have it play  
**So that** I can use the camera as a remote speaker

**Acceptance Criteria:**
- User provides a local audio file path
- The file is transferred to the camera and played through the speaker
- Supported input formats: WAV, MP3, Opus, FLAC, AAC, OGG
- Files not in a camera-compatible format are automatically converted before transfer

### US-2: Adjust Playback Volume

**As a** user  
**I want to** control the playback volume  
**So that** I can set an appropriate loudness level

**Acceptance Criteria:**
- User can specify volume (0–100) and/or gain (0–31) when sending audio
- Defaults are used if not specified (vol=60, gain=20)

### US-3: Play Pre-installed Sounds

**As a** user  
**I want to** play one of the camera's built-in sounds by name  
**So that** I can quickly trigger alerts or chimes without transferring a file

**Acceptance Criteria:**
- User can list available built-in sounds
- User can play a built-in sound by name (e.g. `chime_1`, `doorbell_2`)

### US-4: Text-to-Speech

**As a** user  
**I want to** send a text message to be spoken on the camera  
**So that** I can make announcements without pre-recording audio

**Acceptance Criteria:**
- User provides a text string
- The text is spoken through the camera speaker using the `tell` command

### US-5: Stop Playback

**As a** user  
**I want to** stop audio that is currently playing  
**So that** I can silence the camera immediately

**Acceptance Criteria:**
- A stop command immediately halts playback on the camera

### US-6: Loop Playback

**As a** user  
**I want to** loop an audio file a specified number of times  
**So that** I can repeat alerts or sounds

**Acceptance Criteria:**
- User can specify a loop count (1–N)
- The audio plays the specified number of times

## Functional Requirements

### FR-1: Audio Transfer

WHEN a user sends an audio file  
THE SYSTEM SHALL transfer the file to the camera via SCP to a temporary location (`/tmp/`)

### FR-2: Format Conversion

WHEN the audio file is not in a camera-compatible format (WAV, PCM, AAC, Opus, MP3, FLAC)  
THE SYSTEM SHALL convert it to Opus (16kHz mono) using ffmpeg before transfer

WHEN the audio file is already in a compatible format  
THE SYSTEM SHALL transfer it without conversion

### FR-3: Playback Trigger

WHEN the file has been transferred  
THE SYSTEM SHALL trigger playback via SSH using the camera's `play` command

### FR-4: Built-in Sound Playback

WHEN the user requests a built-in sound  
THE SYSTEM SHALL invoke `play /usr/share/sounds/<name>.opus` on the camera via SSH

### FR-5: TTS Playback

WHEN the user provides text for speech  
THE SYSTEM SHALL invoke `tell "<text>"` on the camera via SSH

### FR-6: Cleanup

WHEN playback of a transferred file completes  
THE SYSTEM SHALL remove the temporary file from the camera

## Non-Functional Requirements

### NFR-1: Simplicity

The tool SHALL be a Python CLI that can be run from the server with no dependencies beyond Python standard library, `paramiko` (SSH), and optionally `ffmpeg` (for conversion).

### NFR-2: Latency

Audio playback SHALL begin within 3 seconds of the user issuing the command for files under 1MB.

### NFR-3: Configuration

Camera connection details (hostname, user, port) SHALL be configurable via a config file or environment variables, with sensible defaults matching the current setup.

### NFR-4: Error Handling

WHEN the camera is unreachable  
THE SYSTEM SHALL report a clear error message and exit with a non-zero status code

WHEN ffmpeg is not installed and conversion is needed  
THE SYSTEM SHALL report that ffmpeg is required and exit with a non-zero status code
