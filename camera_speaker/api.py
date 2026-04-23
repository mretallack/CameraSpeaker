from camera_speaker.config import load_config
from camera_speaker.transport import Transport


def say(
    text: str,
    host: str = None,
    volume: int = None,
    gain: int = None,
    chimes: int = 3,
    chime_delay: int = 200,
    repeat: int = 2,
):
    """Play attention chimes then speak text on camera.

    Args:
        text: Text to speak.
        host: Camera hostname (default from config).
        volume: Volume 0-100 (default from config).
        gain: Gain 0-31 (default from config).
        chimes: Number of chime beeps before speech.
        chime_delay: Milliseconds between chimes.
        repeat: How many times to play the speech.
    """
    cfg = load_config({"host": host, "volume": volume, "gain": gain})
    t = Transport(cfg["host"], cfg["user"], cfg["port"])
    try:
        vol = f"-v {cfg['volume']} -g {cfg['gain']}"
        text_escaped = text.replace("'", "'\\''")
        tmp = "/tmp/cs_tts.opus"

        parts = []
        if chimes > 0:
            parts.append(f"play {vol} -l {chimes} -d {chime_delay} /usr/share/sounds/chime_1.opus")
            parts.append("sleep 2")

        parts.append(
            f"curl --silent --get --url https://thingino.com/say2 "
            f"--data-urlencode q='{text_escaped}' -o {tmp}"
        )

        for i in range(repeat):
            if i > 0:
                parts.append("sleep 0.5")
            parts.append(f"play {vol} {tmp}")

        parts.append(f"rm -f {tmp}")

        out, err = t.ssh_exec(" && ".join(parts))
        if err.strip():
            raise RuntimeError(err.strip())
    finally:
        t.close()
