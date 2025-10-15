from pathlib import Path
from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for, abort
from werkzeug.utils import secure_filename
import platform
import os, glob
from global_def import *
from utils.file_utils import list_all_media
from utils.gen_thumbnails import gen_webp_from_video_threading



# TARGET_FOLDER 不再指向 .thumbnails，而用 MEDIA_FOLDER 作為根目錄
TARGET_FOLDER = MEDIAFILE_URI_PATH

ALLOWED_EXTS  = {".mp4", ".jpg", ".png"}
MAX_CONTENT_LENGTH = 512 * 1024 * 1024   # 512MB（可自行調整）

app = Flask(__name__)
app.config["TARGET_FOLDER"] = str(TARGET_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SECRET_KEY"] = "change-me"

def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTS

# ---------- 路徑安全檢查輔助 ----------
ROOT = Path(MEDIAFILE_URI_PATH).resolve()

def safe_join_and_resolve(subpath: str) -> Path:
    # 把 subpath join 至 ROOT，並 resolve，然後檢查仍在 ROOT 之下
    candidate = (ROOT / subpath).resolve()
    if not str(candidate).startswith(str(ROOT)):
        raise ValueError("Outside of permitted folder")
    return candidate

# ---------- 瀏覽（支援根目錄與子目錄） ----------
@app.route("/", defaults={"req_path": ""})
@app.route("/browse/", defaults={"req_path": ""})
@app.route("/browse/<path:req_path>")
def browse(req_path):
    try:
        abs_path = safe_join_and_resolve(req_path)
    except ValueError:
        return abort(404)

    # 如果是檔案 → 轉為下載
    if abs_path.is_file():
        rel = abs_path.relative_to(ROOT)
        return send_from_directory(str(ROOT), str(rel), as_attachment=True)

    # 否則列目錄內容
    entries = []
    for entry in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        entries.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "size": entry.stat().st_size if entry.is_file() else None
        })

    # 計算相對路徑（顯示於模板，空字串代表根）
    rel_current = "" if abs_path == ROOT else str(abs_path.relative_to(ROOT))

    return render_template("index.html", entries=entries, current=rel_current)

# ---------- 下載（指定子路徑） ----------
@app.route("/download/<path:filepath>")
def download_file(filepath):
    try:
        abs_path = safe_join_and_resolve(filepath)
    except ValueError:
        return abort(404)
    if not abs_path.is_file():
        return abort(404)
    rel = abs_path.relative_to(ROOT)
    return send_from_directory(str(ROOT), str(rel), as_attachment=True)

# ---------- 上傳（可以上傳到當前目錄，這裡示範上傳到根 MEDIA_FOLDER） ----------
@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("file")
    if not files:
        flash("沒有選擇任何檔案")
        return redirect(url_for("browse", req_path=""))

    saved = 0
    for f in files:
        if not f or not f.filename:
            continue
        if not allowed_file(f.filename):
            flash(f"副檔名不允許：{f.filename}")
            continue
        safe_name = secure_filename(f.filename)
        # 上傳到根（或可改為當前資料夾）
        save_path = ROOT / safe_name
        f.save(str(save_path))
        saved += 1

    if saved:
        flash(f"成功上傳 {saved} 檔")
    return redirect(url_for("browse", req_path=""))




if __name__ == "__main__":
    log.debug(f"Welcome to {Version}")

    media_file_supported_ext = [".mp4", ".jpg", ".png", ".jpeg"]
    media_dirs = [SNAPSHOTS_URI_PATH, RECORDINGS_URI_PATH, MEDIA_URI_PATH]

    # 只列檔名
    all_files = list_all_media(media_dirs, media_file_supported_ext, full_path=True)


    log.debug(f"Total files: {all_files}")
    for f in all_files:
        gen_webp_from_video_threading(str(MEDIAFILE_URI_PATH), f)
    app.run(debug=True, host="0.0.0.0", port=5000)
