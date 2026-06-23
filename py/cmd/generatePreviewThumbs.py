"""
Generates ML-selected preview poster thumbnails for a single video.

Calls handymatt_media.media_generator.extractPreviewThumbs which samples n_frames
frames from the video and selects the most visually representative ones.

Output is written to:
    <media-dir>/0x<hash>/previewthumbs/

Usage:
    python -m cmd.generatePreviewThumbs --video-path <path> --hash <hash> --media-dir <path>

Output (JSON to stdout):
    {"success": true, "paths": [...]}
    {"success": false, "error": "..."}
"""
import argparse
import json
import os
import sys


def media_dir_for_hash(media_dir: str, video_hash: str) -> str:
    return os.path.join(media_dir, f'0x{video_hash}')


def has_preview_thumbs(video_hash: str, media_dir: str) -> bool:
    folder = os.path.join(media_dir_for_hash(media_dir, video_hash), 'previewthumbs')
    if not os.path.isdir(folder):
        return False
    return len(os.listdir(folder)) >= 10


def main(video_path: str, video_hash: str, media_dir: str, amount: int, n_frames: int, redo: bool):
    from handymatt_media import media_generator

    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}

    if not redo and has_preview_thumbs(video_hash, media_dir):
        return {"success": True, "paths": [], "skipped": True}

    out_folder = os.path.join(media_dir_for_hash(media_dir, video_hash), 'previewthumbs')
    os.makedirs(out_folder, exist_ok=True)

    paths = media_generator.extractPreviewThumbs(
        video_path,
        out_folder,
        amount=amount,
        resolution=[360, 1080],
        n_frames=n_frames,
    )

    if not paths:
        return {"success": False, "error": "extractPreviewThumbs returned no paths"}

    return {"success": True, "paths": paths}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--video-path', required=True, help='Absolute path to the video file')
    parser.add_argument('--hash', required=True, help='Video hash')
    parser.add_argument('--media-dir', required=True, help='Preview media root directory')
    parser.add_argument('--amount', type=int, default=5, help='Number of preview images to extract')
    parser.add_argument('--n-frames', type=int, default=300, help='Frames to sample for selection')
    parser.add_argument('--redo', action='store_true', help='Regenerate even if thumbs already exist')
    args = parser.parse_args()

    try:
        result = main(args.video_path, args.hash, args.media_dir, args.amount, args.n_frames, args.redo)
        print(json.dumps(result))
        if not result.get('success'):
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
