from handymatt_media import video_analyser
from ..objects.video_data import VideoData

# PASTE HERE:
import concurrent.futures
import threading
import sys
from typing import List, Dict, Optional

def _get_video_hashes_multi(
    video_paths: List[str],
    existing_videos: Dict[str, VideoData],
    rehash_videos: bool = False,
    max_workers: int = 12  # Adjust based on your system's I/O capabilities
) -> Dict[str, str]:
    """Gets video hashes for a list of video paths and a dict of existing video data objects using multithreading."""

    hash_path_map: Dict[str, str] = {}
    hashing_failed, had_to_hash, collisions = [], [], []
    path_hash_map = {video_data.path: hash for hash, video_data in existing_videos.items()}

    def process_video(video_path: str, thread_id: int) -> Optional[str]:
        """Helper function to process a single video and return its hash."""
        # print(f"Thread {thread_id} is processing video: {video_path}")
        video_hash = path_hash_map.get(video_path)
        if video_hash is None or rehash_videos:
            try:
                had_to_hash.append(video_path)
                video_hash = video_analyser.getVideoHash_ffmpeg(video_path)
            except Exception as e:
                print(f"Error hashing video {video_path} in thread {thread_id}: {e}")
                return None
        return video_hash

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all video paths to the executor with a unique thread ID
            future_to_path_and_id = {
                executor.submit(process_video, path, idx): (path, idx)
                for idx, path in enumerate(video_paths)
            }

            try:
                for idx, future in enumerate(concurrent.futures.as_completed(future_to_path_and_id)):
                    video_path, thread_id = future_to_path_and_id[future]
                    print(f"\rgetting video hash ({idx+1}/{len(video_paths)})", end='')
                    try:
                        video_hash = future.result()
                        if video_hash is None:
                            hashing_failed.append(video_path)
                        else:
                            if video_hash in hash_path_map:
                                collisions.append(video_hash)
                            else:
                                hash_path_map[video_hash] = video_path
                    except Exception as e:
                        print(f"Error processing video {video_path} in thread {thread_id}: {e}")
                        hashing_failed.append(video_path)
            except KeyboardInterrupt:
                print("\nReceived Ctrl+C. Shutting down gracefully...")
                executor.shutdown(wait=False)  # Shutdown the executor immediately
                sys.exit(1)  # Exit the program with a non-zero status code

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    print()
    # Print hashing report
    print(f"Hashing failed for {len(hashing_failed)} videos.")
    print(f"Had to hash {len(had_to_hash)} videos.")
    print(f"Found {len(collisions)} hash collisions.")
    return hash_path_map