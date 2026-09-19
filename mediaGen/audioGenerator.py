"""
audioGenerator - Audio Generation Interface
Provides a user-friendly interface for generating professional voiceovers from text.
Uses AudioGeneratorUtility for the core functionality.
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_AUDIOS_DIR = os.path.join(PROJECT_ROOT, "dumps", "generated_audios")
sys.path.insert(0, PROJECT_ROOT)

from util.llmUtil.AudioGeneratorUtility import (
    generate_audio_from_text,
    generate_audio_from_article,
    generate_news_bulletin
)

load_dotenv()


def _resolve_audio_path(output_path, default_name):
    """Return an audio path inside the project's generated_audios folder."""
    os.makedirs(GENERATED_AUDIOS_DIR, exist_ok=True)
    filename = output_path or default_name
    if not filename.lower().endswith(".mp3"):
        filename += ".mp3"
    return filename if os.path.dirname(filename) else os.path.join(GENERATED_AUDIOS_DIR, filename)


def generate_audio_for_article(article_paragraph, file_name):
    """Generate an MP3 voiceover for an article paragraph.

    Args:
        article_paragraph (str): Complete article text to convert to speech.
        file_name (str): Output filename without the ``.mp3`` extension.

    Returns:
        str: Path to the generated MP3 file, or None if generation failed.
    """
    if not article_paragraph or not isinstance(article_paragraph, str):
        raise ValueError("article_paragraph must be a non-empty string")
    if not file_name or not isinstance(file_name, str):
        raise ValueError("file_name must be a non-empty string")

    output_path = _resolve_audio_path(file_name, "article_audio.mp3")
    return generate_audio_from_article(article_paragraph, output_path=output_path)


class AudioGenerator:
    """
    Wrapper class for professional audio/voiceover generation with user-friendly output.
    Uses AudioGeneratorUtility for core functionality.
    """

    def __init__(self, language='en'):
        """
        Initialize the Audio Generator.

        Args:
            language (str): Default language for audio generation (default: 'en')
        """
        self.language = language

    def generate_from_text(self, text, output_path=None, slow=False):
        """
        Generate audio from text.

        Args:
            text (str): Text to convert to speech
            output_path (str): Path to save audio file
            slow (bool): Use slower speech for clarity

        Returns:
            str: Path to the saved audio file, or None if failed
        """

        print(f"\n🎤 Generating professional voiceover...")
        print(f"📄 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"🌐 Language: {self.language}")

        output_path = _resolve_audio_path(
            output_path,
            f"generated_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )
        audio_path = generate_audio_from_text(text, output_path, self.language, slow)

        return audio_path

    def generate_from_article(self, article_content, headline="", output_path=None, max_length=None, slow=False):
        """
        Generate professional news-style audio from an article.

        Args:
            article_content (str): Full article content
            headline (str): Article headline
            output_path (str): Path to save audio file
            max_length (int): Maximum text length to read
            slow (bool): Use slower speech

        Returns:
            str: Path to the saved audio file, or None if failed
        """

        print(f"\n📰 Generating audio from article...")
        if headline:
            print(f"📌 Headline: {headline}")

        output_path = _resolve_audio_path(
            output_path,
            f"article_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )
        audio_path = generate_audio_from_article(
            article_content,
            headline,
            output_path,
            self.language,
            max_length,
            slow
        )

        return audio_path

    def generate_bulletin(self, articles, output_path=None,
                          intro_text="Here are today's top stories.",
                          outro_text="That's all for now. Thank you for listening."):
        """
        Generate a complete news bulletin from multiple articles.

        Args:
            articles (list): List of tuples (headline, content)
            output_path (str): Path to save bulletin audio
            intro_text (str): Opening text
            outro_text (str): Closing text

        Returns:
            str: Path to the saved bulletin audio file, or None if failed
        """

        print(f"\n📻 Generating news bulletin...")
        print(f"📰 Number of stories: {len(articles)}")

        output_path = _resolve_audio_path(
            output_path,
            f"news_bulletin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )
        bulletin_path = generate_news_bulletin(
            articles,
            output_path,
            self.language,
            intro_text,
            outro_text
        )

        return bulletin_path


if __name__ == "__main__":
    example_article = (
        "The Kennedy Center board voted to add President Donald Trump's name "
        "to the facade of the performing arts venue."
    )
    audio_path = generate_audio_for_article(
        example_article,
        "kennedy_center_political_audio"
    )
    print(f"Generated audio: {audio_path}")