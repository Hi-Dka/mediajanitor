import configparser
import os

CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "/config/MediaJanitor.conf"
)
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Read qbittorrent config
QB_URL = config.get("qbittorrent", "BASE_URL", fallback="http://localhost:8080")
QB_USER = config.get("qbittorrent", "USER", fallback="admin")
QB_PASS = config.get("qbittorrent", "PASSWORD", fallback="admin")

# Read moviepilot config
MP_URL = config.get("moviepilot", "BASE_URL", fallback="http://localhost:3000")
MP_USER = config.get("moviepilot", "USER", fallback="admin")
MP_PASS = config.get("moviepilot", "PASSWORD", fallback="admin")
MP_TRANSFER_PAGE = config.getint("moviepilot", "TRANSFER_PAGE", fallback=1)
MP_TRANSFER_COUNT = config.getint("moviepilot", "TRANSFER_COUNT", fallback=50)
MP_DELETE_SRC = config.getboolean("moviepilot", "DELETE_SRC", fallback=True)
MP_DELETE_DEST = config.getboolean("moviepilot", "DELETE_DEST", fallback=True)

MEDIA_DIRS = [
    d.strip()
    for d in config.get("plex", "MEDIA_DIR", fallback="/media/plex").split(",")
    if d.strip()
]
