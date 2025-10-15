import platform
from pathlib import Path

import utils.log_utils
from version import *

LOG_FILE_PREFIX = "flaskmediafilemanager.log"

log = utils.log_utils.logging_init(__file__, LOG_FILE_PREFIX)


# === 根資料夾（變更成你要的 /home/venom/Videos） ===
'''if platform.machine() == "x86_64":
    MEDIA_FOLDER = Path("/home/venom/Videos")
else:
    MEDIA_FOLDER = Path("/root/MediaFiles")'''

if platform.machine() == 'x86_64':
    MEDIAFILE_URI_PATH = "/home/venom/Videos/"
    SNAPSHOTS_URI_PATH = "/home/venom/Videos/Snapshots/"
    RECORDINGS_URI_PATH = "/home/venom/Videos/Recordings/"
    MEDIA_URI_PATH = "/home/venom/Videos/Media/"
    THUMBNAILS_URI_PATH = "/home/venom/Videos/thumbnails/"
    PLAYLISTS_URI_PATH = "/home/venom/Videos/playlists/"
else:
    MEDIAFILE_URI_PATH = "/root/MediaFiles/"
    SNAPSHOTS_URI_PATH = "/root/MediaFiles/Snapshots/"
    RECORDINGS_URI_PATH = "/root/MediaFiles/Recordings/"
    MEDIA_URI_PATH = "/root/MediaFiles/Media/"
    THUMBNAILS_URI_PATH = "/root/MediaFiles/thumbnails/"
    PLAYLISTS_URI_PATH = "/root/MediaFiles/Playlists/"

THUMBNAIL_WIDTH = 160
THUMBNAIL_HEIGHT = 120