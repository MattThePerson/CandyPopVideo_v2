"""

"""
import argparse
import os
from handymatt_media.media_generator import generateVideoTeaser


def main(args: argparse.Namespace):
    """  """
    print("Generating video teaser")
    os.makedirs(args.mediadir, exist_ok=True)
    clip_amount = int( ( 584/119 + (11/5355)*float(args.duration_sec) ) * 2 )
    if args.type == "small":
        try:
            _ = generateVideoTeaser(
                args.path,
                args.mediadir,
                args.filestem,
                abs_amount_mode=True,
                n=clip_amount,
                clip_len=1.3,
                skip=2,
                small_resolution=True,
                end_perc=98,
            )
        except Exception as e:
            print("[ERROR] generateTeasersSmall:\n", e)
    
    else:
        try:
            _ = generateVideoTeaser(
                args.path,
                args.mediadir,
                args.filestem,
                abs_amount_mode=True,
                n=clip_amount,
                clip_len=1.65,
                skip=1,
                small_resolution=False,
                end_perc=98,
            )
        except Exception as e:
            print("[ERROR] generateTeasersSmall:\n", e)
        





if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', type=str)
    parser.add_argument('-mediadir', type=str)
    parser.add_argument('-duration_sec', type=float)
    parser.add_argument('-filestem', type=str)
    parser.add_argument('-type', type=str) # small/large
    
    args = parser.parse_args()
    
    main(args)
    