from .downloaders import videos_downloader as vd, youtube_downloader as yd
from .helpers import merge_video as mv


def _get_urls(func, urls, temp_dir):
    return list(filter(bool, [func(url, temp_dir) for url in urls]))


def process_usual(temp_dir, urls):
    file_paths = _get_urls(vd.download_video, urls, temp_dir)

    if len(file_paths) == 1:
        return file_paths[0]
    elif len(file_paths) > 1:
        return mv.concat_videos(temp_dir, file_paths)


def process_youtube(temp_dir, urls):
    return mv.concat_videos(temp_dir, _get_urls(yd.download_video, urls, temp_dir))

