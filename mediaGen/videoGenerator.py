import os
import shutil
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_VIDEOS_DIR = PROJECT_ROOT / "dumps" / "generated_videos"
GENERATED_IMAGES_DIR = PROJECT_ROOT / "dumps" / "generated_images"
GENERATED_AUDIOS_DIR = PROJECT_ROOT / "dumps" / "generated_audios"


def _resolve_media_path(media_path, media_directory):
    """Resolve a bare media filename inside its project output directory."""
    path = Path(media_path)
    if not path.parent.parts or path.parent == Path("."):
        path = media_directory / path.name
    return path.resolve()


def create_video(
    images,
    audio,
    text=None,
    output="output.mp4",
    resolution="1920x1080",
    fps=30,
    text_position="bottom-center",
    text_size=24,
    transition_duration=0.5,
):
    """
    Create an MP4 video from one or more images and an audio file.

    Parameters
    ----------
    images : list[str] | str
        One image path or a list of image paths.

    audio : str
        Path to the audio file.

    text : str | None
        Optional text to display throughout the video.

    output : str
        Path of the final MP4 file.

    resolution : str
        Video resolution. Default: 1920x1080.

    fps : int
        Frames per second. Default: 30.

    text_position : str
        One of:
            "bottom-right"
            "bottom-left"
            "bottom-center"
            "top-right"
            "top-left"
            "center"

    text_size : int
        Font size of the overlay text.

    transition_duration : float
        Fade transition duration in seconds.

    Returns
    -------
    str
        Path to the generated video.
    """

    # ---------------------------------------------------------
    # 1. Validate FFmpeg
    # ---------------------------------------------------------

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if ffmpeg is None:
        raise RuntimeError(
            "FFmpeg was not found. Please install FFmpeg and add it to PATH."
        )

    if ffprobe is None:
        raise RuntimeError(
            "FFprobe was not found. Please install FFmpeg and add it to PATH."
        )

    # ---------------------------------------------------------
    # 2. Normalize image input
    # ---------------------------------------------------------

    if isinstance(images, (str, Path)):
        images = [str(images)]

    if not images:
        raise ValueError("At least one image is required.")

    images = [str(_resolve_media_path(image, GENERATED_IMAGES_DIR)) for image in images]

    # ---------------------------------------------------------
    # 3. Validate files
    # ---------------------------------------------------------

    for image in images:
        if not os.path.isfile(image):
            raise FileNotFoundError(f"Image not found: {image}")

    audio = str(_resolve_media_path(audio, GENERATED_AUDIOS_DIR))

    if not os.path.isfile(audio):
        raise FileNotFoundError(f"Audio file not found: {audio}")

    # ---------------------------------------------------------
    # 4. Validate text position
    # ---------------------------------------------------------

    valid_positions = {
        "bottom-right",
        "bottom-left",
        "bottom-center",
        "top-right",
        "top-left",
        "center",
    }

    if text_position not in valid_positions:
        raise ValueError(
            f"Invalid text_position. Choose one of: "
            f"{', '.join(sorted(valid_positions))}"
        )

    # ---------------------------------------------------------
    # 5. Get audio duration
    # ---------------------------------------------------------

    probe_command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        audio,
    ]

    result = subprocess.run(
        probe_command,
        capture_output=True,
        text=True,
        check=True,
    )

    try:
        audio_duration = float(result.stdout.strip())
    except ValueError:
        raise RuntimeError("Could not determine audio duration.")

    if audio_duration <= 0:
        raise RuntimeError("Audio duration is invalid.")

    # ---------------------------------------------------------
    # 6. Resolve output path
    # ---------------------------------------------------------

    output_path = Path(output)
    if not output_path.parent.parts or output_path.parent == Path("."):
        output_path = GENERATED_VIDEOS_DIR / output_path.name

    output = str(output_path.resolve())

    output_directory = os.path.dirname(output)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    # ---------------------------------------------------------
    # 7. Create temporary working directory
    # ---------------------------------------------------------

    with tempfile.TemporaryDirectory(prefix="video_generator_") as temp_dir:

        # -----------------------------------------------------
        # 8. Determine image duration
        # -----------------------------------------------------

        image_count = len(images)

        # Divide audio equally between images.
        image_duration = audio_duration / image_count

        # Make sure transition doesn't consume the entire image.
        actual_transition = min(
            transition_duration,
            max(0.0, image_duration / 2)
        )

        # -----------------------------------------------------
        # 9. Copy images into temporary directory
        # -----------------------------------------------------

        prepared_images = []

        for index, image in enumerate(images):

            extension = Path(image).suffix.lower()

            if not extension:
                extension = ".jpg"

            destination = os.path.join(
                temp_dir,
                f"image_{index:04d}{extension}"
            )

            shutil.copy2(image, destination)

            prepared_images.append(destination)

        # -----------------------------------------------------
        # 10. Create concat file
        # -----------------------------------------------------

        concat_file = os.path.join(temp_dir, "images.txt")

        with open(concat_file, "w", encoding="utf-8") as f:

            for image in prepared_images:

                # FFmpeg concat demuxer requires escaped paths.
                escaped_path = image.replace("\\", "/").replace("'", "'\\''")

                f.write(f"file '{escaped_path}'\n")
                f.write(f"duration {image_duration:.6f}\n")

            # Repeat the last image so concat duration is correct.
            if prepared_images:

                last_image = prepared_images[-1]
                escaped_last = (
                    last_image
                    .replace("\\", "/")
                    .replace("'", "'\\''")
                )

                f.write(f"file '{escaped_last}'\n")

        # -----------------------------------------------------
        # 11. Build video filter
        # -----------------------------------------------------

        width, height = resolution.split("x")

        video_filter = (
            f"scale={width}:{height}:"
            f"force_original_aspect_ratio=increase,"
            f"crop={width}:{height},"
            f"setsar=1,"
            f"fps={fps},"
            f"format=yuv420p"
        )

        # -----------------------------------------------------
        # 12. Add text overlay if requested
        # -----------------------------------------------------

        if text is not None and str(text).strip():

            # Escape characters that have special meaning
            # inside FFmpeg's drawtext filter.
            safe_text = str(text)

            safe_text = safe_text.replace("\\", r"\\")
            safe_text = safe_text.replace(":", r"\:")
            safe_text = safe_text.replace("'", r"\'")
            safe_text = safe_text.replace("%", r"\%")

            # Try to locate a common Windows font.
            font_candidates = [
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\segoeui.ttf",
                r"C:\Windows\Fonts\calibri.ttf",
            ]

            font_file = None

            for candidate in font_candidates:
                if os.path.isfile(candidate):
                    font_file = candidate
                    break

            # Position
            if text_position == "bottom-right":
                x_position = "w-text_w-30"
                y_position = "h-text_h-25"

            elif text_position == "bottom-left":
                x_position = "30"
                y_position = "h-text_h-25"

            elif text_position == "bottom-center":
                x_position = "(w-text_w)/2"
                y_position = "h-text_h-25"

            elif text_position == "top-right":
                x_position = "w-text_w-30"
                y_position = "25"

            elif text_position == "top-left":
                x_position = "30"
                y_position = "25"

            else:
                x_position = "(w-text_w)/2"
                y_position = "(h-text_h)/2"

            # Build drawtext filter.
            if font_file:

                safe_font = (
                    font_file
                    .replace("\\", "/")
                    .replace(":", r"\:")
                )

                drawtext = (
                    f"drawtext="
                    f"fontfile='{safe_font}':"
                    f"text='{safe_text}':"
                    f"fontsize={text_size}:"
                    f"fontcolor=white:"
                    f"borderw=2:"
                    f"bordercolor=black@0.65:"
                    f"x={x_position}:"
                    f"y={y_position}"
                )

            else:

                drawtext = (
                    f"drawtext="
                    f"text='{safe_text}':"
                    f"fontsize={text_size}:"
                    f"fontcolor=white:"
                    f"borderw=2:"
                    f"bordercolor=black@0.65:"
                    f"x={x_position}:"
                    f"y={y_position}"
                )

            video_filter += "," + drawtext

        # -----------------------------------------------------
        # 13. Build FFmpeg command
        # -----------------------------------------------------

        command = [
            ffmpeg,

            "-y",

            # Image sequence
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file,

            # Audio
            "-i",
            audio,

            # Video filter
            "-vf",
            video_filter,

            # Duration
            "-t",
            str(audio_duration),

            # Video encoding
            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "20",

            "-pix_fmt",
            "yuv420p",

            # Audio encoding
            "-c:a",
            "aac",

            "-b:a",
            "192k",

            # Audio duration controls output
            "-shortest",

            # Metadata
            "-movflags",
            "+faststart",

            output,
        ]

        # -----------------------------------------------------
        # 14. Execute FFmpeg
        # -----------------------------------------------------

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if process.returncode != 0:

            raise RuntimeError(
                "FFmpeg failed while generating the video.\n\n"
                + process.stderr
            )

    # ---------------------------------------------------------
    # 15. Verify output
    # ---------------------------------------------------------

    if not os.path.isfile(output):
        raise RuntimeError(
            "Video generation completed, but the output file "
            "was not created."
        )

    return output


# -------------------------------------------------------------
# Optional direct test
# -------------------------------------------------------------

if __name__ == "__main__":

    video = create_video(
        images=[
            "2026_09_14_01_06_5.png",
            "2026_09_14_01_06_6.png",
            "2026_09_14_01_06_7.png",
        ],
        audio="2026_09_14_01_06_1.mp3",
        text="News Source : BBC, CBC",
        output="output2.mp4",
    )

    print("Video generated successfully:")
    print(video)