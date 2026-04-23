"""Camera Speaker integration for Home Assistant."""

import logging

import paramiko
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "camera_speaker"
TTS_URL = "https://thingino.com/say2"

SAY_SCHEMA = vol.Schema(
    {
        vol.Required("message"): cv.string,
        vol.Optional("host"): cv.string,
        vol.Optional("volume"): vol.All(int, vol.Range(min=0, max=100)),
        vol.Optional("gain"): vol.All(int, vol.Range(min=0, max=31)),
        vol.Optional("chimes"): vol.All(int, vol.Range(min=0, max=10)),
        vol.Optional("repeat"): vol.All(int, vol.Range(min=1, max=10)),
    }
)

SOUND_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Optional("host"): cv.string,
        vol.Optional("volume"): vol.All(int, vol.Range(min=0, max=100)),
        vol.Optional("gain"): vol.All(int, vol.Range(min=0, max=31)),
    }
)


def _ssh_exec(host: str, user: str, port: int, command: str) -> str:
    """Execute a command on the camera via SSH."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=user)
        _, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err.strip():
            _LOGGER.warning("Camera stderr: %s", err.strip())
        return out
    finally:
        client.close()


def _get_conf(hass: HomeAssistant) -> dict:
    """Get config from the first config entry."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return {}
    return dict(entries[0].data)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Camera Speaker integration."""

    async def _run_ssh(host, user, port, command):
        return await hass.async_add_executor_job(_ssh_exec, host, user, port, command)

    async def handle_say(call: ServiceCall) -> None:
        """Handle the say service call."""
        conf = _get_conf(hass)
        if not conf:
            _LOGGER.error("Camera Speaker not configured")
            return
        host = call.data.get("host", conf["host"])
        user = conf["user"]
        port = conf["port"]
        volume = call.data.get("volume", conf["volume"])
        gain = call.data.get("gain", conf["gain"])
        chimes = call.data.get("chimes", conf["chimes"])
        repeat = call.data.get("repeat", conf["repeat"])
        text = call.data["message"].replace("'", "'\\''")
        vol_flags = f"-v {volume} -g {gain}"
        tmp = "/tmp/cs_tts.opus"

        parts = []
        if chimes > 0:
            parts.append(
                f"play {vol_flags} -l {chimes} -d {conf['chime_delay']} "
                f"/usr/share/sounds/chime_1.opus"
            )
            parts.append("sleep 2")

        parts.append(
            f"curl --silent --get --url {TTS_URL} " f"--data-urlencode q='{text}' -o {tmp}"
        )

        for i in range(repeat):
            if i > 0:
                parts.append("sleep 0.5")
            parts.append(f"play {vol_flags} {tmp}")

        parts.append(f"rm -f {tmp}")

        _LOGGER.info("Camera Speaker say: '%s' on %s", call.data["message"], host)
        await _run_ssh(host, user, port, " && ".join(parts))

    async def handle_sound(call: ServiceCall) -> None:
        """Handle the sound service call."""
        conf = _get_conf(hass)
        if not conf:
            _LOGGER.error("Camera Speaker not configured")
            return
        host = call.data.get("host", conf["host"])
        volume = call.data.get("volume", conf["volume"])
        gain = call.data.get("gain", conf["gain"])
        name = call.data["name"]
        vol_flags = f"-v {volume} -g {gain}"

        _LOGGER.info("Camera Speaker sound: '%s' on %s", name, host)
        await _run_ssh(
            host,
            conf["user"],
            conf["port"],
            f"play {vol_flags} /usr/share/sounds/{name}.opus",
        )

    async def handle_stop(call: ServiceCall) -> None:
        """Handle the stop service call."""
        conf = _get_conf(hass)
        if not conf:
            _LOGGER.error("Camera Speaker not configured")
            return
        host = call.data.get("host", conf["host"])
        _LOGGER.info("Camera Speaker stop on %s", host)
        await _run_ssh(
            host,
            conf["user"],
            conf["port"],
            "killall play 2>/dev/null; killall aplay 2>/dev/null",
        )

    hass.services.async_register(DOMAIN, "say", handle_say, schema=SAY_SCHEMA)
    hass.services.async_register(DOMAIN, "sound", handle_sound, schema=SOUND_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        "stop",
        handle_stop,
        schema=vol.Schema({vol.Optional("host"): cv.string}),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Camera Speaker from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
