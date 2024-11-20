import shutil
import tempfile

import m3u_parser as mp
import videos_downloader as vd
import youtube_downloader as yd
import videos_merger as vm


def process_usual(urls, func):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for url in urls:
            file_path = vd.download_video(url, temp_dir)
            if file_path is None:
                return None
            file_paths.append(file_path)
        if len(file_paths) > 1:
            return func(vm.concat_videos(temp_dir))
        elif len(file_paths):
            return func(file_paths[0])


def process_youtube(urls, func):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for i, url in enumerate(urls):
            file_path = yd.download_video(url, temp_dir, 'uploaded-' + str(i) + '.mp4')
            if file_path is None:
                return None
            file_paths.append(file_path)
        return func(vm.concat_videos(temp_dir))


if __name__ == '__main__':
    print(process_usual(mp.parse_res_m3u(mp.parse_root_m3u(
        'https://m.media-amazon.com/images/S/vse-vms-transcoding-artifact-us-east-1-prod/a255c915-38c0-4702-acd5-29a1a0946d06/default.jobtemplate.hls.m3u8',
    )), lambda fp: shutil.copy(fp, './')))
