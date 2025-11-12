from pathlib import Path
from tempfile import TemporaryDirectory

import ffmpeg

def concat_videos(temp_dir_name: str, input_files: list[str]):
    temp_dir = Path(temp_dir_name)
    # path iterator to grab input files in basepath, and create a posix filename list.
    # you can keep, modify, or drop the suffix filter.
    print("OK123", input_files)

    # set output filename
    out_file = temp_dir / "concated.mp4"
    # create file object that will contain files for ffmpeg to concat
    input_files_path = temp_dir / "input_files.txt"

    # iterate over sorted posix files in list, and dump to file in the required format
    with input_files_path.open("w") as f:
        for file in input_files:
            f.write("file {}\n".format(file))

    # create the ffmpeg input with the format "concat" and "safe" set to 0
    ff_input = ffmpeg.input(input_files_path.as_posix(), format="concat", safe=0)
    # input stream -> output stream with output filename and expanded params
    ff_output = ff_input.output(out_file.as_posix(), c="copy")
    # make ffmpeg quiet
    ff_output = ff_output.global_args("-loglevel", "error")

    try:
        ff_output.run(overwrite_output=True)
        return out_file.as_posix()
    except ffmpeg.Error as e:
        print(e.stderr)
        return None
