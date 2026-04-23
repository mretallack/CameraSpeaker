"""Config flow for Camera Speaker."""

import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "camera_speaker"


class CameraSpeakerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Camera Speaker."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input["host"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Optional("user", default="root"): str,
                    vol.Optional("port", default=22): int,
                    vol.Optional("volume", default=100): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Optional("gain", default=31): vol.All(int, vol.Range(min=0, max=31)),
                    vol.Optional("chimes", default=3): vol.All(int, vol.Range(min=0, max=10)),
                    vol.Optional("chime_delay", default=200): int,
                    vol.Optional("repeat", default=2): vol.All(int, vol.Range(min=1, max=10)),
                }
            ),
        )
