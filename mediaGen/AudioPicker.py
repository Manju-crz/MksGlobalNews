"""
AudioPicker - Audio Generation Interface
Provides a user-friendly interface for generating professional voiceovers from text.
Uses AudioGeneratorUtility for the core functionality.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmUtil.AudioGeneratorUtility import (
    generate_audio_from_text,
    generate_audio_from_article,
    generate_audio_batch,
    generate_news_bulletin
)

load_dotenv()


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

        audio_path = generate_audio_from_article(
            article_content,
            headline,
            output_path,
            self.language,
            max_length,
            slow
        )

        return audio_path

    def generate_bulletin(self, articles, output_path="news_bulletin.mp3",
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

        bulletin_path = generate_news_bulletin(
            articles,
            output_path,
            self.language,
            intro_text,
            outro_text
        )

        return bulletin_path


if __name__ == "__main__":
    # Example usage with current affairs topics
    print("="*100)
    print("AUDIO GENERATOR - AUDIOPICKER (Using gTTS)")
    print("Professional News Reader Voiceover - Current Affairs Examples")
    print("="*100)

    generator = AudioGenerator(language='en')

    # Example 1: Political News
    print("\n--- Example 1: Political News Audio ---")
    political_headline = "Kennedy Center board votes to add Trump's name to the facade of the performing arts building"
    political_article = """
WASHINGTON (AP) — The Kennedy Center board voted on Thursday to add President Donald Trump's
name to the facade of the performing arts venue. The moves set up a test of U.S. District
Judge Christopher Cooper, who ruled in May that letters affixed to the building were added
illegally. During Trump's second term, the Kennedy Center has become an unlikely metaphor
of presidential power.
"""

    audio_path = generator.generate_from_article(
        political_article,
        political_headline,
        output_path="kennedy_center_political_audio.mp3"
    )

    if audio_path:
        print(f"🎧 Play the audio: {audio_path}")

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)

    # Example 2: Sports News
    print("\n--- Example 2: Sports News Audio ---")
    sports_headline = "WNBA condemns 'bad-faith' efforts to fuel transgender player debate"
    sports_article = """
The WNBA has issued a strong statement condemning what it calls 'bad-faith' efforts to
create controversy around transgender athletes in women's basketball. The league emphasized
its commitment to inclusivity while maintaining competitive integrity. Critics have slammed
ex-NBA players' push to enter WNBA draft, calling it a publicity stunt.
"""

    audio_path = generator.generate_from_article(
        sports_article,
        sports_headline,
        output_path="wnba_sports_news_audio.mp3"
    )

    if audio_path:
        print(f"🎧 Play the audio: {audio_path}")

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)

    # Example 3: Technology News
    print("\n--- Example 3: Technology News Audio ---")
    tech_text = "Artificial intelligence continues to revolutionize industries worldwide. "
    tech_text += "New breakthroughs in machine learning are enabling computers to perform tasks that were once thought impossible. "
    tech_text += "From healthcare diagnostics to autonomous vehicles, AI is transforming the way we live and work."

    audio_path = generator.generate_from_text(
        tech_text,
        output_path="ai_technology_news_audio.mp3"
    )

    if audio_path:
        print(f"🎧 Play the audio: {audio_path}")

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)

    # Example 4: News Bulletin (Multiple Stories)
    print("\n--- Example 4: News Bulletin (Multiple Stories) ---")

    bulletin_articles = [
        (political_headline, political_article),
        (sports_headline, sports_article),
        ("Technology Update", tech_text),
    ]

    bulletin_path = generator.generate_bulletin(
        bulletin_articles,
        output_path="daily_news_bulletin.mp3",
        intro_text="Good evening. Here are today's top stories from around the world.",
        outro_text="That concludes our news bulletin. Stay informed, stay safe. Good night."
    )

    if bulletin_path:
        print(f"🎧 Play the bulletin: {bulletin_path}")

    print("\n" + "="*100)
    print("✅ Audio generation examples complete!")
    print("Check the generated .mp3 files and play them to hear the professional voiceover!")
    print("="*100)
    print("\n💡 Tips:")
    print("    - Use headphones for best audio quality")
    print("    - Audio files are in MP3 format, playable on any device")
    print("    - Adjust volume for comfortable listening")
    print("="*100)