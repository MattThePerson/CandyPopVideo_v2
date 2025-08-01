"""
Indented to be called by a subprocess to isolate any heavy imports

call with interpreter: "./.venv/Scripts/python.exe"

"""
import argparse
from handymatt_media.media_generator import generateVideoSpritesheet


def main(args: argparse.Namespace):
    """  """

    print('Generating video spritesheet ...')
    _ = generateVideoSpritesheet(
        args.path,
        args.mediadir,
        number_of_frames = args.num,
        height = args.height,
        filestem = args.filestem,
    )
    print("Done.")





if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', type=str)
    parser.add_argument('-mediadir', type=str)
    parser.add_argument('-num', type=int)
    parser.add_argument('-height', type=int)
    parser.add_argument('-filestem', type=str)
    
    args = parser.parse_args()
    
    main(args)
    