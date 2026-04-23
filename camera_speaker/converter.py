import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

COMPATIBLE_EXTS = {".wav", ".pcm", ".aac", ".opus", ".mp3", ".flac"}


def needs_conversion(file_path: str) -> bool:
    return Path(file_path).suffix.lower() not in COMPATIBLE_EXTS


def convert_to_opus(input_path: str) -> str:
    """Convert audio to Opus 16kHz mono. Returns path to temp file."""
    if not shutil.which("ffmpeg"):
        ext = Path(input_path).suffix
        print(
            f"Error: ffmpeg is required to convert {ext} files. Install with: apt install ffmpeg",
            file=sys.stderr,
        )
        sys.exit(1)

    tmp = tempfile.NamedTemporaryFile(suffix=".opus", delete=False)
    tmp.close()
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-c:a", "libopus", tmp.name,
        ],
        capture_output=True,
        check=True,
    )
    return tmp.name
