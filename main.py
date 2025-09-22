import platform
from pathlib import Path

from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os, glob
from global_def import *
from utils.gen_thumbnails import gen_webp_from_video_threading

# === 這裡改成你要顯示的資料夾路徑 ===
if platform.machine() == "x86_64":
    TARGET_FOLDER = "/home/venom/Videos/.thumbnails"
    MEDIA_FOLDER = "/home/venom/Videos"
else:
    TARGET_FOLDER = "/root/Videos/.thumbnails"
    MEDIA_FOLDER = "/root/Videos"

ALLOWED_EXTS  = {".mp4", ".jpg", ".png"}
MAX_CONTENT_LENGTH = 512 * 1024 * 1024   # 512MB（可自行調整）


app = Flask(__name__)
app.config["TARGET_FOLDER"] = TARGET_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = "change-me"   # 若使用 flash() 需要

def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTS

@app.route("/")
def index():
    if request.method == "POST":
        # 支援多檔上傳
        files = request.files.getlist("file")
        if not files:
            flash("沒有選擇任何檔案")
            return redirect(url_for("index"))

        saved = 0
        for f in files:
            if not f or not f.filename:
                continue
            if not allowed_file(f.filename):
                flash(f"副檔名不允許：{f.filename}")
                continue
            filename = secure_filename(f.filename)
            save_path = TARGET_FOLDER / filename
            f.save(save_path)
            saved += 1

        if saved:
            flash(f"成功上傳 {saved} 檔")
        return redirect(url_for("index"))

    # 取得目錄內的所有檔案清單（只列出檔案）
    file_list = [
        f for f in os.listdir(TARGET_FOLDER)
        if os.path.isfile(os.path.join(TARGET_FOLDER, f))
    ]
    return render_template("index.html", files=file_list, max_size=MAX_CONTENT_LENGTH)

@app.route("/download/<filename>")
def download_file(filename):
    # 直接提供下載
    return send_from_directory(TARGET_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    log.debug("Starting server...")
    log.debug("platform.machine() : {}".format(platform.machine()))
    mp4_files = glob.glob(os.path.join(MEDIA_FOLDER, "*.mp4"))
    jpg_files = glob.glob(os.path.join(MEDIA_FOLDER, "*.jpg"))

    files = [os.path.basename(f) for f in mp4_files + jpg_files]
    log.debug(files)
    for f in files:
        gen_webp_from_video_threading(MEDIA_FOLDER, f)
    # host=0.0.0.0 讓同網段其他設備也可訪問
    app.run(debug=True, host="0.0.0.0", port=5000)
