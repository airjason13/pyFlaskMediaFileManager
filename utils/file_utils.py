from pathlib import Path


def list_all_media(base_paths, extensions=None, full_path=True):
    """
    遞迴列出多個資料夾下所有指定副檔名的檔案。

    :param base_paths: list[str]，要搜尋的多個資料夾路徑
    :param extensions: list[str]，要搜尋的副檔名，例如 ["mp4", "jpg", "png"]
    :param full_path: bool，是否回傳完整路徑（False 則只回傳檔名）
    :return: list[str]
    """
    if extensions is None:
        extensions = ["mp4"]
    if isinstance(base_paths, str):
        base_paths = [base_paths]  # 若傳單一路徑也能兼容

    # 正規化副檔名（移除.並轉小寫）
    extensions = [e.lower().lstrip(".") for e in extensions]
    result = []

    for base_path in base_paths:
        base = Path(base_path)
        if not base.exists():
            continue  # 路徑不存在就跳過
        for ext in extensions:
            for p in base.rglob(f"*.{ext}"):
                result.append(str(p) if full_path else p.name)

    return result
