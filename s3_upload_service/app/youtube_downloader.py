from pytube import YouTube


def download_video(url, temp_dir, filename, *, filters: dict | None = None, order_by: str | None = None, order_asc: bool | None = None, resolution=None, last=False):
    yt = YouTube(url)
    yt_streams = yt.streams
    # Initialize QueryBuilder
    if filters:
        yt_streams = yt_streams.filter(**filters)
    if order_asc is not None:
        yt_streams = (yt_streams.desc, yt_streams.asc)[order_asc]()
    if order_by:
        yt_streams = yt_streams.order_by(order_by)
    # Get final result
    if resolution:
        yt_streams = yt_streams.get_by_resolution(resolution)
    elif last:
        yt_streams = yt_streams.last()
    else:
        yt_streams = yt_streams.first()
    return yt_streams.download(temp_dir, filename)
