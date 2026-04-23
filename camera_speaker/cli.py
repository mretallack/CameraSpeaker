import argparse
import os
import sys
import uuid
from pathlib import Path

from camera_speaker.config import load_config
from camera_speaker.converter import convert_to_opus, needs_conversion
from camera_speaker.transport import Transport


def main():
    parser = argparse.ArgumentParser(prog="camera-speaker", description="Send audio to thingino cameras")
    parser.add_argument("--host", "-H")
    parser.add_argument("--user", "-u")
    parser.add_argument("--port", "-p", type=int)
    parser.add_argument("--volume", "-v", type=int)
    parser.add_argument("--gain", "-g", type=int)

    sub = parser.add_subparsers(dest="command", required=True)

    p_play = sub.add_parser("play", help="Play an audio file")
    p_play.add_argument("file")
    p_play.add_argument("--loop", "-l", type=int, default=1)

    p_say = sub.add_parser("say", help="Text-to-speech")
    p_say.add_argument("text")

    p_sound = sub.add_parser("sound", help="Play a built-in sound")
    p_sound.add_argument("name")

    sub.add_parser("sounds", help="List built-in sounds")
    sub.add_parser("stop", help="Stop playback")

    args = parser.parse_args()
    cfg = load_config({
        "host": args.host, "user": args.user, "port": args.port,
        "volume": args.volume, "gain": args.gain,
    })

    t = Transport(cfg["host"], cfg["user"], cfg["port"])
    try:
        {"play": cmd_play, "say": cmd_say, "sound": cmd_sound,
         "sounds": cmd_sounds, "stop": cmd_stop}[args.command](t, cfg, args)
    finally:
        t.close()


def cmd_play(t: Transport, cfg: dict, args):
    local = args.file
    if not Path(local).exists():
        print(f"Error: File not found: {local}", file=sys.stderr)
        sys.exit(1)

    converted = None
    if needs_conversion(local):
        local = convert_to_opus(local)
        converted = local

    ext = Path(local).suffix
    remote = f"/tmp/cs_{uuid.uuid4().hex[:8]}{ext}"

    try:
        t.scp_upload(local, remote)
        play_cmd = f"play -v {cfg['volume']} -g {cfg['gain']} {remote}"
        for _ in range(args.loop):
            out, err = t.ssh_exec(play_cmd)
            if err.strip():
                print(err, file=sys.stderr)
        t.ssh_exec(f"rm -f {remote}")
    finally:
        if converted:
            os.unlink(converted)


def cmd_say(t: Transport, cfg: dict, args):
    from camera_speaker.api import say
    try:
        say(args.text, host=cfg["host"], volume=cfg["volume"], gain=cfg["gain"])
    except RuntimeError as e:
        print(e, file=sys.stderr)


def cmd_sound(t: Transport, cfg: dict, args):
    out, err = t.ssh_exec(f"play -v {cfg['volume']} -g {cfg['gain']} /usr/share/sounds/{args.name}.opus")
    if err.strip():
        print(err, file=sys.stderr)


def cmd_sounds(t: Transport, cfg: dict, args):
    out, err = t.ssh_exec("ls /usr/share/sounds/*.opus 2>/dev/null")
    if not out.strip():
        print("No built-in sounds found.")
        return
    for line in out.strip().splitlines():
        name = Path(line).stem
        print(name)


def cmd_stop(t: Transport, cfg: dict, args):
    t.ssh_exec("killall play 2>/dev/null; killall aplay 2>/dev/null")
