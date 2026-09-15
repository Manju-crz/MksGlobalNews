from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips


def merge_videos(video_files, output_file):
    """
    Merge multiple MP4 video files into a single MP4 file.

    The videos are concatenated in exactly the order provided
    in the video_files list.

    Parameters
    ----------
    video_files : list[str]
        List of MP4 video file paths in the desired order.

    output_file : str
        Complete path of the final merged MP4 file.

    Example
    -------
    merge_videos(
        [
            "video1.mp4",
            "video2.mp4",
            "video3.mp4"
        ],
        "final_video.mp4"
    )
    """

    if not video_files:
        raise ValueError("No video files were provided.")

    if len(video_files) < 2:
        raise ValueError("At least two video files are required for merging.")

    video_paths = [Path(video_file) for video_file in video_files]
    output_path = Path(output_file)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    for video_path in video_paths:
        if not video_path.is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

    clips = []
    final_clip = None

    try:
        # Load videos in the exact order supplied by the user
        for video_path in video_paths:
            print(f"Loading: {video_path}")

            clip = VideoFileClip(str(video_path))
            clips.append(clip)

        print("\nMerging videos...")

        # Concatenate videos in the specified order
        final_clip = concatenate_videoclips(
            clips,
            method="compose"
        )

        print(f"Writing final video: {output_path}")

        # Export the final MP4
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac"
        )

        print("\nVideo merging completed successfully!")
        print(f"Final video: {output_file}")

    finally:
        if final_clip is not None:
            final_clip.close()

        # Always close all source clips
        for clip in clips:
            clip.close()


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":

    merge_videos(
        [
            r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_videos\output.mp4",
            r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_videos\output2.mp4",
        ],
        r"C:\DATA\VS_Code_Notes\MksGlobalNews\dumps\generated_videos\final_video.mp4"
    )

