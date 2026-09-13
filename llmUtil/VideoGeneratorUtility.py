"""
VideoGeneratorUtility - Reusable Video Generation with Voice Over
Generates videos from text/articles with AI-generated voiceovers.
Uses free, open-source tools - no API keys required.
"""

import os
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, CompositeAudioClip
from datetime import datetime
import tempfile
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Import our image generator
from llmUtil.ImageGeneratorUtility import generate_image_from_paragraph


def generate_voiceover(text, output_path=None, language='en', slow=False):
    """
    Generate voiceover audio from text using Google Text-to-Speech (gTTS).

    Free, unlimited, no API key required.

    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save audio file (default: auto-generated)
        language (str): Language code (default: 'en' for English)
                        Options: 'en', 'es', 'fr', 'de', 'it', 'pt', 'hi', 'ar', etc.
        slow (bool): Speak slowly (default: False)

    Returns:
        str: Path to the generated audio file (.mp3)

    Example:
        >>> audio_path = generate_voiceover("Hello world, this is a test")
        >>> print(audio_path)
        'temp_audio_20260817_023800.mp3'
    """

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"temp_audio_{timestamp}.mp3"

    try:
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(output_path)

        return output_path

    except Exception as e:
        print(f"Error generating voiceover: {str(e)}")
        return None


def create_text_image(text, width=1920, height=1080, bg_color=(30, 30, 30), text_color=(255, 255, 255)):
    """
    Create a simple image with text overlay.

    Args:
        text (str): Text to display
        width (int): Image width (default: 1920)
        height (int): Image height (default: 1080)
        bg_color (tuple): Background RGB color (default: dark gray)
        text_color (tuple): Text RGB color (default: white)

    Returns:
        str: Path to the generated image
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"temp_text_image_{timestamp}.png"

    # Create image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Wrap text
    wrapped_text = textwrap.fill(text, width=60)

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), wrapped_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw text
    draw.text((x, y), wrapped_text, fill=text_color)

    # Save image
    img.save(output_path)
    return output_path


def generate_video_from_text(
    text,
    output_path=None,
    image_prompt=None,
    duration=None,
    language='en',
    width=1920,
    height=1080,
    fps=24
):
    """
    Generate a video with voiceover from text.

    Creates a video with:
    - AI-generated background image (or text overlay)
    - Voiceover narration of the text

    Args:
        text (str): Text content for voiceover
        output_path (str): Path to save video file (default: auto-generated .mp4)
        image_prompt (str): Optional custom prompt for background image
                           If None, uses the text itself or creates a text overlay
        duration (float): Video duration in seconds (default: auto from audio)
        language (str): Voiceover language (default: 'en')
        width (int): Video width (default: 1920)
        height (int): Video height (default: 1080)
        fps (int): Frames per second (default: 24)

    Returns:
        str: Path to the generated video file, or None if failed

    Example:
        >>> video_path = generate_video_from_text(
        ...     "Breaking news: Scientists discover new planet",
        ...     image_prompt="Space exploration, distant planet, stars"
        ... )
    """

    print("\n🎬 Generating video with voiceover...")
    print(f"📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"generated_video_{timestamp}.mp4"

    temp_files = []

    try:
        # Step 1: Generate voiceover
        print("🔊 Generating voiceover...")
        audio_path = generate_voiceover(text, language=language)

        if not audio_path:
            print("❌ Failed to generate voiceover")
            return None

        temp_files.append(audio_path)
        print(f"✅ Voiceover created: {audio_path}")

        # Step 2: Generate or create background image
        print("🎨 Creating background image...")

        if image_prompt:
            # Generate AI image
            image_path = generate_image_from_paragraph(
                image_prompt,
                output_dir="temp_images",
                width=width,
                height=height
            )
        else:
            # Create simple text image
            image_path = create_text_image(text[:200], width, height)
            temp_files.append(image_path)

        if not image_path:
            print("❌ Failed to create background image")
            return None

        print(f"✅ Background image created: {image_path}")

        # Step 3: Load audio to get duration
        audio_clip = AudioFileClip(audio_path)
        video_duration = duration if duration else audio_clip.duration

        # Step 4: Create video from image
        print("🎞️ Composing video...")
        image_clip = ImageClip(image_path, duration=video_duration)

        # Step 5: Combine image and audio
        video_clip = image_clip.set_audio(audio_clip)

        # Step 6: Write video file
        print(f"💾 Saving video to: {output_path}")
        video_clip.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

        # Cleanup
        audio_clip.close()
        video_clip.close()

        print(f"✅ Video generated successfully!")
        print(f"📁 Saved to: {output_path}")
        print(f"⏱️ Duration: {video_duration:.2f} seconds")

        return output_path

    except Exception as e:
        print(f"❌ Error generating video: {str(e)}")
        return None

    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


def generate_video_from_article(
    article_content,
    headline="",
    output_path=None,
    language='en',
    max_text_length=500
):
    """
    Generate a video from a news article with voiceover.

    Args:
        article_content (str): Full article content
        headline (str): Article headline (optional)
        output_path (str): Path to save video file
        language (str): Voiceover language (default: 'en')
        max_text_length (int): Maximum text length for voiceover (default: 500 chars)

    Returns:
        str: Path to the generated video file, or None if failed

    Example:
        >>> video_path = generate_video_from_article(
        ...     article_content="Scientists have discovered...",
        ...     headline="Major Scientific Discovery",
        ...     output_path="news_video.mp4"
        ... )
    """

    print(f"\n📰 Generating video from article...")

    if headline:
        print(f"📌 Headline: {headline}")

    # Create voiceover text
    if headline:
        voiceover_text = f"{headline}. {article_content[:max_text_length]}"
    else:
        voiceover_text = article_content[:max_text_length]

    # Create image prompt from headline/content
    if headline:
        image_prompt = f"{headline}. News article visual representation"
    else:
        image_prompt = article_content[:200]

    return generate_video_from_text(
        text=voiceover_text,
        output_path=output_path,
        image_prompt=image_prompt,
        language=language
    )


if __name__ == "__main__":
    # Test the utility
    print("=" * 100)
    print("VIDEO GENERATOR UTILITY - TEST")
    print("=" * 100)

    # Test 1: Simple text video
    print("\n🎬 Test 1: Simple Text Video ---")

    test_text = "Breaking news: Scientists have made a groundbreaking discovery in renewable energy technology."

    video_path = generate_video_from_text(
        test_text,
        image_prompt="Renewable energy, solar panels, wind turbines, futuristic technology",
        output_path="test_simple_video.mp4"
    )

    if video_path:
        print(f"\n✅ Test 1 Complete: {video_path}")
    else:
        print("\n❌ Test 1 Failed")

    # Test 2: Article video
    print("\n📰 Test 2: Article Video ---")

    test_headline = "Kennedy Center Controversy Continues"

    test_article = """
WASHINGTON (AP) — The Kennedy Center board voted on Thursday to add President Donald Trump's
name to the facade of the performing arts venue. The moves set up a test of U.S. District
Judge Christopher Cooper, who ruled in May that letters affixed to the building were added
illegally. During Trump's second term, the Kennedy Center has become an unlikely metaphor
of presidential power.
"""

    video_path = generate_video_from_article(
        test_article,
        test_headline,
        output_path="test_article_video.mp4"
    )

    if video_path:
        print(f"\n✅ Test 2 Complete: {video_path}")
    else:
        print("\n❌ Test 2 Failed")

    print("\n" + "=" * 100)
    print("✅ Video generation tests complete!")
    print("Check the generated .mp4 files in the current directory.")
    print("=" * 100)