import requests


def parse_root_m3u(url: str):
    res = requests.get(url)
    res.raise_for_status()
    content = res.text
    files = [l for l in content.splitlines() if l.startswith("default.")]
    max_res = 0
    needle_url = None
    for file in files:
        resolution = file[23:-5]
        if resolution.isdigit():
            resolution = int(resolution)
        else:
            parts = file.split(".")
            for part in parts:
                if part.startswith("hls"):
                    resolution = part[3:]
                    if resolution.isdigit():
                        resolution = int(resolution)
                    else:
                        resolution = None
                    break
        if resolution and resolution > max_res:
            max_res = resolution
            needle_url = file
    if not needle_url:
        return None
    return url.rsplit("/", 1)[0] + "/" + needle_url


def parse_res_m3u(url: str):
    res = requests.get(url)
    res.raise_for_status()
    content = res.text
    base_url = url.rsplit("/", 1)[0] + "/"
    urls = [(base_url + l) for l in content.splitlines() if l.startswith("default.")]
    return urls
