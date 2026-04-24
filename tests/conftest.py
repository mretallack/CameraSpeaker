import importlib

collect_ignore_glob = []

if not importlib.util.find_spec("homeassistant"):
    collect_ignore_glob.append("test_ha_*.py")
