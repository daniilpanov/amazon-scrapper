from pathlib import Path
import ffmpeg


def concat_videos(sourcedir: str | Path):
    if isinstance(sourcedir, str):
        sourcedir = Path(sourcedir)
    # path iterator to grab input files in basepath, and create a posix filename list.
    # you can keep, modify, or drop the suffix filter.
    input_files = sorted([
        _ for _ in sourcedir.iterdir()
        if _.is_file()
    ])

    # set output filename
    outFile = sourcedir / 'concated.mp4'

    # create file object that will contain files for ffmpeg to concat
    # input_files_path = p('input_files.txt')
    input_files_path = sourcedir / 'input_files.txt'

    # iterate over sorted posix files in list, and dump to file in the required format
    with input_files_path.open('w') as f:
        for file in input_files:
            f.write('file \'{}\'\n'.format(file.name))

    # create the ffmpeg input with the format 'concat' and 'safe' set to 0
    ffInput = ffmpeg.input(input_files_path.as_posix(), format='concat', safe=0)

    # set output parameters
    params = {
        'c': 'copy'
    }

    # input stream -> output stream with output filename and expanded params
    ffOutput = ffInput.output(outFile.as_posix(), **params)

    # make ffmpeg quiet
    ffOutput = ffOutput.global_args('-loglevel', 'error')

    # something, something, run.
    try:
        ffOutput.run(overwrite_output=True)
        return outFile.as_posix()
    except ffmpeg.Error as e:
        print(e.stderr)
        return None
