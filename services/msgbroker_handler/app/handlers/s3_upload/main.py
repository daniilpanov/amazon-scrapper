import tempfile

from pymongo.errors import DuplicateKeyError

from . import controller
from .helpers import s3helper
from .parsers import m3u_parser as mp
from ..abstract_handler import AbstractHandler


class S3Upload(AbstractHandler):
    @classmethod
    def get_handlers(cls):
        return {"s3": {"handler": cls.load}}

    def _post_init(self):
        self._media_collection = self._db["amazon_data"]

    def load_video(self, asin, variant, mimetype, path, filename, prefix):
        if not s3helper.upload_file(path, filename, prefix):
            return False

        if asin:
            if mimetype == "m3u":
                mimetype = "video/mp4"
            try:
                self._media_collection.insert_one({
                    "asin": asin,
                    "media_url": "" + prefix + filename,
                    "mimetype": mimetype,
                    "variant": variant,
                })
            except DuplicateKeyError:
                pass

        return True

    def load(self):
        video_url = self._data["videoUrl"]
        asin = self._data.get("asin", None)
        variant = self._data.get("variant", 0)
        filename = self._data.get("filename", asin or "fileobj")
        mimetype = self._data.get("mimetype", filename.rsplit(".", maxsplit=1)[-1])
        prefix = self._data.get("prefix", "")

        self._logger.debug("Video url: " + video_url)
        if video_url.endswith(".mp4"):
            self._data["media_type"] = "mp4"
            self._logger.warning("Invalid media type. Auto converting. Task dump: " + str({
                "video_url": video_url,
                "asin": asin,
                "variant": variant,
                "mimetype": mimetype,
                "filename": filename,
                "prefix": prefix,
            }))
        self._logger.debug("Params: " + " ".join(map(str, (asin, variant, mimetype, filename, prefix))))

        with tempfile.TemporaryDirectory() as temp_dir:
            if self._data["media_type"] == "yt":
                # video uploads from YouTube
                res = controller.process_youtube(temp_dir, [video_url])
            elif self._data["media_type"] == "m3u":
                # it is a list of videos
                res = controller.process_usual(temp_dir, mp.parse_res_m3u(mp.parse_root_m3u(video_url)))
            else:
                # it is just a video
                res = controller.process_usual(temp_dir, [video_url])

        self.load_video(asin, variant, mimetype, res, filename, prefix)


handler = S3Upload
