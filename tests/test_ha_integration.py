"""Tests for Thingino Camera Speaker HA integration."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    MockPlatform,
    mock_config_flow,
    mock_integration,
    mock_platform,
)

import custom_components.thingino_camera_speaker as integration_module
import custom_components.thingino_camera_speaker.config_flow as config_flow_module

DOMAIN = "thingino_camera_speaker"

TEST_CONFIG = {
    "host": "camera1",
    "user": "root",
    "port": 22,
    "volume": 100,
    "gain": 31,
    "chimes": 3,
    "chime_delay": 200,
    "repeat": 2,
}


def _setup_integration(hass: HomeAssistant):
    """Register the integration with HA's loader."""
    mock_integration(
        hass,
        MockModule(
            DOMAIN,
            async_setup_entry=integration_module.async_setup_entry,
            async_unload_entry=integration_module.async_unload_entry,
        ),
    )
    mock_platform(hass, f"{DOMAIN}.config_flow", MockPlatform())


async def test_config_flow_user(hass: HomeAssistant):
    """Test the config flow shows form then creates entry."""
    _setup_integration(hass)
    with mock_config_flow(DOMAIN, config_flow_module.ThinginoCameraSpeakerConfigFlow):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=TEST_CONFIG
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "camera1"
        assert result["data"] == TEST_CONFIG


async def test_setup_entry_registers_services(hass: HomeAssistant):
    """Test that setting up an entry registers the services."""
    _setup_integration(hass)

    entry = MockConfigEntry(domain=DOMAIN, data=TEST_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.services.has_service(DOMAIN, "say")
    assert hass.services.has_service(DOMAIN, "sound")
    assert hass.services.has_service(DOMAIN, "stop")


async def test_say_service_calls_ssh(hass: HomeAssistant):
    """Test that the say service calls SSH with correct command."""
    _setup_integration(hass)

    entry = MockConfigEntry(domain=DOMAIN, data=TEST_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    with patch("custom_components.thingino_camera_speaker._ssh_exec", return_value="") as mock_ssh:
        await hass.services.async_call(DOMAIN, "say", {"message": "Hello"}, blocking=True)
        assert mock_ssh.called
        call_args = mock_ssh.call_args
        assert call_args[0][0] == "camera1"
        assert call_args[0][1] == "root"
        assert call_args[0][2] == 22
        assert "Hello" in call_args[0][3]
        assert "thingino.com/say2" in call_args[0][3]


async def test_unload_entry_removes_services(hass: HomeAssistant):
    """Test that unloading removes services."""
    _setup_integration(hass)

    entry = MockConfigEntry(domain=DOMAIN, data=TEST_CONFIG)
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert not hass.services.has_service(DOMAIN, "say")
    assert not hass.services.has_service(DOMAIN, "sound")
    assert not hass.services.has_service(DOMAIN, "stop")
