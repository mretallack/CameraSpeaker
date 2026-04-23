from camera_speaker.converter import needs_conversion


def test_compatible_formats_no_conversion():
    for ext in [".wav", ".pcm", ".aac", ".opus", ".mp3", ".flac"]:
        assert not needs_conversion(f"test{ext}")


def test_incompatible_formats_need_conversion():
    for ext in [".ogg", ".wma", ".m4a", ".amr"]:
        assert needs_conversion(f"test{ext}")


def test_case_insensitive():
    assert not needs_conversion("test.WAV")
    assert not needs_conversion("test.Mp3")
