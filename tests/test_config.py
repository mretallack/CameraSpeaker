from camera_speaker.config import load_config


def test_defaults():
    cfg = load_config({})
    assert cfg["host"] == "camera2"
    assert cfg["user"] == "root"
    assert cfg["port"] == 22
    assert cfg["volume"] == 60
    assert cfg["gain"] == 20


def test_cli_overrides():
    cfg = load_config({"host": "cam1", "volume": 80})
    assert cfg["host"] == "cam1"
    assert cfg["volume"] == 80


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("CAMERA_HOST", "envhost")
    cfg = load_config({})
    assert cfg["host"] == "envhost"


def test_cli_beats_env(monkeypatch):
    monkeypatch.setenv("CAMERA_HOST", "envhost")
    cfg = load_config({"host": "clihost"})
    assert cfg["host"] == "clihost"
