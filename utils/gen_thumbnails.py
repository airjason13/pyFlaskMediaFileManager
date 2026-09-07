import hashlib
import os
import threading

import ffmpy
from global_def import *
from media_configs.media_path_configs import MediaFileFolder, ThumbnailFileFolder
from media_configs.thumbnail_configs import still_image_loop_cnt, preview_period, preview_start_time


def gen_webp_from_video(file_folder, video_path, prefix=""):
    # 設定錯誤計數與門檻
    error_count = 0
    error_count_threshold = 3

    # 使用 pathlib 讓檔名與副檔名解析更安全
    p_video = Path(video_path)
    video_extension = p_video.suffix.lower().strip('.')

    # 若未從外部傳入 prefix，則保留原代碼的預設邏輯：取所在資料夾名稱作為 prefix
    if not prefix:
        prefix = f"{Path(file_folder).name}_"

    # 組合新檔名：利用 stem 取代原有的 replace('.mp4', '.webp')，確保所有圖片或影片格式皆可正確轉換為 .webp
    new_file_name = f"{prefix}{p_video.stem}.webp"

    # 確保路徑組合正確
    thumbnail_path = os.path.join(THUMBNAILS_URI_PATH, new_file_name)

    log.debug(f"file_folder: {file_folder}")
    log.debug(f"video_path: {video_path}")
    log.info(f"thumbnail_path: {thumbnail_path}")

    # 確保縮圖目錄存在
    thumbnail_folder_path = os.path.expanduser("~" + MediaFileFolder) + ThumbnailFileFolder
    try:
        if not os.path.exists(thumbnail_folder_path):
            os.makedirs(thumbnail_folder_path)
    except OSError:
        log.error(f"Could not create thumbnail folder {thumbnail_folder_path}")

    # 嘗試產生縮圖，失敗最多重試 3 次
    while True:
        try:
            if not os.path.isfile(thumbnail_path):
                scale_param = f'scale={THUMBNAIL_WIDTH}:{THUMBNAIL_WIDTH}'
                global_opts = '-hide_banner -loglevel error'

                # 根據副檔名判斷是圖片還是影片，給予不同的 ffmpeg 參數
                if video_extension in ["jpeg", "jpg", "png"]:
                    ff = ffmpy.FFmpeg(
                        global_options=global_opts,
                        inputs={str(video_path): ['-loop', str(still_image_loop_cnt), '-t', str(preview_period)]},
                        outputs={str(thumbnail_path): ['-vf', scale_param, '-frames:v', '1']}
                    )
                else:
                    ff = ffmpy.FFmpeg(
                        global_options=global_opts,
                        inputs={str(video_path): ['-ss', str(preview_start_time), '-t', str(preview_period)]},
                        outputs={str(thumbnail_path): ['-vf', scale_param]}
                    )
                log.debug("%s", ff.cmd)
                ff.run()
        except Exception as e:
            log.debug("Exception %s", e)
            # 發生錯誤時刪除可能損壞的檔案[cite: 3]
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            error_count += 1
            if error_count > error_count_threshold:
                log.debug("source file : %s might be fault", video_path)
                break
            continue
        break

    return str(thumbnail_path)


def gen_webp_from_video_threading(file_folder, video, prefix=""):
    # 將 prefix 參數也加入 threading 的 args 中
    threads = [threading.Thread(target=gen_webp_from_video, args=(file_folder, video, prefix))]
    threads[0].start()


def gen_webp_from_video_dep(file_folder, video_path):
    # use hashlib md5 to generate preview file name
    error_count = 0
    error_count_threshold = 3
    filename = os.path.basename(video_path)
    video_name = filename.split(".")[0]
    video_extension = filename.split(".")[1]
    # log.debug("video_extension = %s", video_extension)
    # preview_file_name = hashlib.md5(video_name.encode('utf-8')).hexdigest()
    preview_file_name = video_name
    # thumbnail_path = video_path.replace(".mp4", ".webp")
    log.debug(f"file_folder: {file_folder}")
    log.debug(f"video_path: {video_path}")
    file_name_prefix = str(file_folder).split("/")[-1]
    new_file_name = f"{file_name_prefix}_{filename.replace('.mp4', '.webp')}"
    #new_file_name = f"{video_name}.webp"
    thumbnail_path = THUMBNAILS_URI_PATH + new_file_name
    log.info(f"{thumbnail_path}")
    # video_path = file_folder + "/" + video
    # log.debug("video_path = %s", video_path)
    # log.debug("thumbnail_path = %s", thumbnail_path)
    thunbnail_folder_path = os.path.expanduser("~" + MediaFileFolder) + ThumbnailFileFolder
    try:
        if not os.path.exists(thunbnail_folder_path):
            os.makedirs(thunbnail_folder_path)
    except OSError:
        log.error("Could not create thumbnail folder " + thunbnail_folder_path)
    while True:
        try:
            if os.path.isfile(thumbnail_path) is False:
                scale_param = f'scale={THUMBNAIL_WIDTH}:{THUMBNAIL_WIDTH}'
                global_opts = '-hide_banner -loglevel error'
                if video_extension in ["jpeg", "jpg", "png"]:
                    # log.debug("still image")
                    ff = ffmpy.FFmpeg(
                        global_options=global_opts,
                        inputs={video_path: ['-loop', str(still_image_loop_cnt), '-t', str(preview_period)]},
                        outputs={thumbnail_path: ['-vf', scale_param, '-frames:v', '1']}
                    )
                else:
                    ff = ffmpy.FFmpeg(
                        global_options=global_opts,
                        inputs={video_path: ['-ss', str(preview_start_time), '-t', str(preview_period)]},
                        outputs={thumbnail_path: ['-vf', scale_param]}
                    )
                log.debug("%s", ff.cmd)
                ff.run()
        except Exception as e:
            log.debug("Excception %s", e)
            os.remove(thumbnail_path)
            error_count += 1
            if error_count > error_count_threshold:
                log.debug("source file : %s might be fault", video_path)
                break
            continue
        break
    # log.debug("%s generated good", thumbnail_path)
    return thumbnail_path


def gen_webp_from_video_threading_dep(file_folder, video):
    threads = [threading.Thread(target=gen_webp_from_video, args=(file_folder, video,))]
    threads[0].start()