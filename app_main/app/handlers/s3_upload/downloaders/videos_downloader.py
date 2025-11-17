import os

import requests


def download_video(url, temp_dir):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_path = os.path.join(temp_dir, os.path.basename(url))
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Video loading error [{url}]: {e}")
        return None
