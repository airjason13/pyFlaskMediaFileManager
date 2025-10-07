import platform
from pathlib import Path

import utils.log_utils
from version import *

LOG_FILE_PREFIX = "flaskmediafilemanager.log"

log = utils.log_utils.logging_init(__file__, LOG_FILE_PREFIX)


# === 根資料夾（變更成你要的 /home/venom/Videos） ===
if platform.machine() == "x86_64":
    MEDIA_FOLDER = Path("/home/venom/Videos")
else:
    MEDIA_FOLDER = Path("/root/MediaFiles")