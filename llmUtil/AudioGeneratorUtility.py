"""
AudioGeneratorUtility - Reusable Audio/Voiceover Generation Utility
Generates professional voiceovers from text/articles like a news reader.
Uses free, open-source text-to-speech engines - no API keys required.
"""

import os
from gtts import gTTS
from datetime import datetime
import time


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_AUDIOS_DIR = os.path.join(PROJECT_ROOT, "dumps", "generated_audios")


def generate_audio_from_text(text, output_path=None, language='en', slow=False, speed=1.0):
    """
    Generate audio voiceover from text using Google Text-to-Speech (gTTS).

    Free, unlimited, no API key required.
    Reads text like a professional news reader.

    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save audio file (default: auto-generated .mp3)
        language (str): Language code (default: 'en' for English)
            Options: 'en', 'es', 'fr', 'de', 'it', 'pt', 'hi', 'ar', 'ja', 'ko', etc.
        slow (bool): Speak slowly for better clarity (default: False)
        speed (float): Playback speed multiplier (default: 1.0)
            Use 0.9 for slower, more professional news reading

    Returns:
        str: Path to the generated audio file (.mp3), or None if failed

    Example:
        >>> audio_path = generate_audio_from_text(
        ...     "Breaking news: Scientists discover new planet",
        ...     output_path="news_audio.mp3"
        ... )
        >>> print(audio_path)
        'news_audio.mp3'
    """

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(
            GENERATED_AUDIOS_DIR,
            f"generated_audio_{timestamp}.mp3",
        )

    # Ensure .mp3 extension
    if not output_path.endswith('.mp3'):
        output_path += '.mp3'

    try:
        print(f"\n🎙️ Generating voiceover...")
        print(f"📄 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"🌐 Language: {language}")
        print(f"⚙️ Speed: {'Slow' if slow else 'Normal'}")

        # Generate speech
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(output_path)

        print(f"✅ Audio generated successfully!")
        print(f"💾 Saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Error generating audio: {str(e)}")
        return None


def generate_audio_from_article(article_content, headline="", output_path=None,
                                language='en', max_length=None, slow=False):
    """
    Generate professional news-style voiceover from an article.

    Reads the article like a news anchor with proper pacing.

    Args:
        article_content (str): Full article content
        headline (str): Article headline (optional, will be read first)
        output_path (str): Path to save audio file (default: auto-generated)
        language (str): Language code (default: 'en')
        max_length (int): Maximum text length to read (default: None = full article)
        slow (bool): Use slower, clearer speech (default: False)

    Returns:
        str: Path to the generated audio file, or None if failed

    Example:
        >>> audio_path = generate_audio_from_article(
        ...     article_content="Scientists have discovered a new species...",
        ...     headline="Major Scientific Discovery",
        ...     output_path="science_news.mp3"
        ... )
    """

    print(f"\n📰 Generating audio from article...")

    if headline:
        print(f"📌 Headline: {headline}")

    # Prepare the text for voiceover
    if headline:
        # Add headline with a pause marker
        voiceover_text = f"{headline}. "

        # Add article content
        if max_length:
            remaining_length = max_length - len(headline) - 2
            voiceover_text += article_content[:remaining_length]
        else:
            voiceover_text += article_content
    else:
        if max_length:
            voiceover_text = article_content[:max_length]
        else:
            voiceover_text = article_content

    # Clean up the text
    voiceover_text = " ".join(voiceover_text.split())

    # Generate filename if not provided
    if output_path is None:
        if headline:
            # Create filename from headline
            safe_headline = "".join(
                c if c.isalnum() or c.isspace() else "_" for c in headline
            )
            safe_headline = "_".join(safe_headline.split()[:10])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{safe_headline}_{timestamp}.mp3"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"article_audio_{timestamp}.mp3"

    return generate_audio_from_text(voiceover_text, output_path, language, slow)


def generate_audio_batch(articles, output_dir=GENERATED_AUDIOS_DIR, language='en', delay=2):
    """
    Generate audio files for multiple articles.

    Args:
        articles (list): List of tuples (headline, content) or just content strings
        output_dir (str): Directory to save audio files
        language (str): Language code (default: 'en')
        delay (int): Delay in seconds between generations (default: 2)

    Returns:
        list: List of tuples (article_info, audio_path) for successful generations

    Example:
        >>> articles = [
        ...     ("Headline 1", "Article content 1..."),
        ...     ("Headline 2", "Article content 2..."),
        ... ]
        >>> results = generate_audio_batch(articles)
    """

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for idx, article in enumerate(articles, 1):
        print(f"\n[{idx}/{len(articles)}] Processing article...")

        # Parse article format
        if isinstance(article, tuple):
            headline, content = article
        else:
            headline = ""
            content = article

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"article_{idx}_{timestamp}.mp3"
        output_path = os.path.join(output_dir, filename)

        # Generate audio
        audio_path = generate_audio_from_article(
            content,
            headline,
            output_path,
            language
        )

        if audio_path:
            results.append((article, audio_path))
            print(f"✅ Success: {audio_path}")
        else:
            print(f"❌ Failed for article {idx}")

        # Add delay between requests (except for last one)
        if idx < len(articles):
            print(f"⏳ Waiting {delay} seconds...")
            time.sleep(delay)

    return results


def generate_news_bulletin(articles, output_path="news_bulletin.mp3", language='en',
                           intro_text="Here is today's top stories.",
                           outro_text="That's all for now. Thank you for listening."):
    """
    Generate a complete news bulletin from multiple articles.

    Combines multiple articles into a single audio file like a news broadcast.

    Args:
        articles (list): List of tuples (headline, content)
        output_path (str): Path to save the bulletin audio file
        language (str): Language code (default: 'en')
        intro_text (str): Opening text for the bulletin
        outro_text (str): Closing text for the bulletin

    Returns:
        str: Path to the generated bulletin audio file, or None if failed

    Example:
        >>> articles = [
        ...     ("Breaking News", "Scientists discover..."),
        ...     ("Sports Update", "Team wins championship..."),
        ... ]
        >>> bulletin_path = generate_news_bulletin(articles, "daily_news.mp3")
    """

    print(f"\n📰 Generating news bulletin...")
    print(f"📋 Number of stories: {len(articles)}")

    # Build the complete bulletin text
    bulletin_text = intro_text + " "

    for idx, article in enumerate(articles, 1):
        if isinstance(article, tuple):
            headline, content = article
            # Add story number, headline, and content
            bulletin_text += f"Story {idx}. {headline}. {content[:300]}. "
        else:
            bulletin_text += f"Story {idx}. {article[:300]}. "

    bulletin_text += outro_text

    # Generate the audio
    return generate_audio_from_text(bulletin_text, output_path, language, slow=False)


if __name__ == "__main__":
    # Test the utility
    print("=" * 100)
    print("AUDIO GENERATOR UTILITY - TEST")
    print("Professional News Reader Voiceover")
    print("=" * 100)

    # Test 1: Simple text to audio
    print("\n🎵 Test 1: Simple Text to Audio 🎵")
    test_text = "Scientists have made a groundbreaking discovery in renewable energy technology that could revolutionize the way we power our homes."

    audio_path = generate_audio_from_text(
        test_text,
        output_path="test_simple_audio.mp3"
    )

    if audio_path:
        print(f"\n✅ Test 1 Complete: {audio_path}")
    else:
        print("\n❌ Test 1 Failed")

    # Test 2: Article with headline
    print("\n📰 Test 2: Article with Headline 📰")
    test_headline = "Kennedy Center Controversy Continues"
    test_article = """
WASHINGTON (AP) – The Kennedy Center board voted on Thursday to add President Donald Trump's
name to the facade of the performing arts venue. The moves set up a test of U.S. District
Judge Christopher Cooper, who ruled in May that letters affixed to the building were added
illegally. During Trump's second term, the Kennedy Center has become an unlikely metaphor
of presidential power.
"""

    audio_path = generate_audio_from_article(
        test_article,
        test_headline,
        output_path="test_article_audio.mp3"
    )

    if audio_path:
        print(f"\n✅ Test 2 Complete: {audio_path}")
    else:
        print("\n❌ Test 2 Failed")

    # Test 3: News bulletin with multiple stories
    print("\n📰 Test 3: News Bulletin (Multiple Stories) 📰")
    test_articles = [
        ("Political News", "The Kennedy Center board voted to add Trump's name to the building facade."),
        ("Sports Update", "The WNBA has issued a statement condemning bad-faith efforts in the transgender player debate."),
        ("Technology", "Artificial intelligence continues to advance with new breakthroughs in machine learning."),
    ]

    bulletin_path = generate_news_bulletin(
        test_articles,
        output_path="test_news_bulletin.mp3"
    )

    if bulletin_path:
        print(f"\n✅ Test 3 Complete: {bulletin_path}")
    else:
        print("\n❌ Test 3 Failed")

    print("\n" + "=" * 100)
    print("✅ Audio generation tests complete!")
    print("Check the generated .mp3 files in the current directory.")
    print("Play them to hear the professional news reader voiceover!")
    print("=" * 100)