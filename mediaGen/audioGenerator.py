"""
audioGenerator - Audio Generation Interface
Provides a user-friendly interface for generating professional news voiceovers.

Uses OpenAI GPT-4o Mini TTS directly.

This file is self-contained and does NOT depend on:
    util.llmUtil.AudioGeneratorUtility

OpenAI Model:
    gpt-4o-mini-tts

Output:
    MP3

Environment variable required:
    OPENAI_API_KEY
"""

import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENERATED_AUDIOS_DIR = os.path.join(
    PROJECT_ROOT,
    "dumps",
    "generated_audios"
)

os.makedirs(GENERATED_AUDIOS_DIR, exist_ok=True)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY environment variable is not configured."
    )


# ============================================================
# OPENAI CLIENT
# ============================================================

client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# CONFIGURATION
# ============================================================

# OpenAI Mini TTS model
TTS_MODEL = "gpt-4o-mini-tts"

# Voice used for the news narration.
# "alloy" is a good neutral voice for news-style narration.
TTS_VOICE = "alloy"

# OpenAI TTS has an input limit per request.
# Keep some safety margin below the maximum.
MAX_CHARS_PER_REQUEST = 3800

# Number of retries if an API request temporarily fails.
MAX_RETRIES = 3

# Delay between retries.
RETRY_DELAY_SECONDS = 2


# ============================================================
# NEWS READER INSTRUCTIONS
# ============================================================

NEWS_READER_INSTRUCTIONS = """
Read the provided article as a professional television news reader.

Voice style:
- Professional
- Clear
- Neutral
- Authoritative
- Natural
- Engaging but not dramatic
- Suitable for a YouTube news channel

Delivery:
- Speak at a natural news-reading pace.
- Pronounce names, locations and organizations clearly.
- Use natural pauses between sentences and paragraphs.
- Give slightly more emphasis to important facts.
- Do not sound robotic.
- Do not add information that is not present in the article.
- Do not introduce yourself.
- Do not say "here is the news" unless that text is explicitly provided.
- Do not summarize or modify the article.
- Read the supplied text faithfully.
"""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _resolve_audio_path(output_path, default_name):
    """
    Return an audio path inside the project's generated_audios folder.
    """

    os.makedirs(GENERATED_AUDIOS_DIR, exist_ok=True)

    filename = output_path or default_name

    if not filename.lower().endswith(".mp3"):
        filename += ".mp3"

    return (
        filename
        if os.path.dirname(filename)
        else os.path.join(GENERATED_AUDIOS_DIR, filename)
    )


def _clean_text(text):
    """
    Clean input text before sending it to TTS.
    """

    if not text:
        return ""

    text = str(text)

    # Normalize whitespace while preserving paragraph breaks.
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n\n".join(lines).strip()


def _split_text_into_chunks(text, max_chars=MAX_CHARS_PER_REQUEST):
    """
    Split long article text into chunks suitable for the OpenAI TTS API.

    Attempts to split at paragraph/sentence boundaries rather than
    cutting sentences in the middle.
    """

    text = _clean_text(text)

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # If the paragraph itself fits, add it normally.
        if len(paragraph) <= max_chars:

            candidate = (
                paragraph
                if not current_chunk
                else current_chunk + "\n\n" + paragraph
            )

            if len(candidate) <= max_chars:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = paragraph

            continue

        # Paragraph itself is too long.
        # Split it by sentences.
        sentences = paragraph.replace("! ", "!|").replace(
            "? ", "?|"
        ).replace(". ", ".|").split("|")

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            if len(sentence) > max_chars:

                # Last-resort hard split for an exceptionally long sentence.
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                start = 0

                while start < len(sentence):
                    end = min(
                        start + max_chars,
                        len(sentence)
                    )

                    chunks.append(sentence[start:end])
                    start = end

                continue

            candidate = (
                sentence
                if not current_chunk
                else current_chunk + " " + sentence
            )

            if len(candidate) <= max_chars:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk)

                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _generate_tts_chunk(text, chunk_number=None, total_chunks=None):
    """
    Generate MP3 audio for a single text chunk.
    """

    if chunk_number and total_chunks:
        print(
            f"🎙️ Generating voiceover "
            f"chunk {chunk_number}/{total_chunks}..."
        )
    else:
        print("🎙️ Generating voiceover...")

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=TTS_VOICE,
                input=text,
                instructions=NEWS_READER_INSTRUCTIONS,
                response_format="mp3"
            )

            return response.read()

        except Exception as exc:

            print(
                f"⚠️ TTS generation attempt "
                f"{attempt}/{MAX_RETRIES} failed: {exc}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(
        "Unable to generate audio after "
        f"{MAX_RETRIES} attempts."
    )


def _combine_mp3_chunks(audio_chunks, output_path):
    """
    Combine MP3 byte streams into a single MP3 file.

    MP3 streams can be concatenated directly. This avoids requiring
    ffmpeg/pydub for normal TTS output.
    """

    if not audio_chunks:
        raise ValueError("No audio chunks were generated.")

    with open(output_path, "wb") as output_file:

        for chunk in audio_chunks:
            output_file.write(chunk)

    return output_path


# ============================================================
# CORE AUDIO GENERATION
# ============================================================

def generate_audio_from_text(
    text,
    output_path,
    language="en",
    slow=False
):
    """
    Generate an MP3 voiceover from text using OpenAI GPT-4o Mini TTS.

    Args:
        text (str):
            Text to convert to speech.

        output_path (str):
            Output MP3 path.

        language (str):
            Kept for backward compatibility with the previous
            AudioGeneratorUtility implementation.

        slow (bool):
            Kept for backward compatibility.
            GPT-4o Mini TTS controls delivery through instructions.

    Returns:
        str:
            Path to generated MP3.
    """

    text = _clean_text(text)

    if not text:
        raise ValueError(
            "Text supplied for audio generation is empty."
        )

    output_path = _resolve_audio_path(
        output_path,
        f"generated_audio_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    )

    chunks = _split_text_into_chunks(text)

    print(
        f"📝 Text length: {len(text):,} characters"
    )

    print(
        f"🔹 Number of TTS chunks: {len(chunks)}"
    )

    print(
        f"🤖 Model: {TTS_MODEL}"
    )

    print(
        f"🎤 Voice: {TTS_VOICE}"
    )

    audio_chunks = []

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"   Chunk {index}: "
            f"{len(chunk):,} characters"
        )

        audio_data = _generate_tts_chunk(
            chunk,
            index,
            len(chunks)
        )

        audio_chunks.append(audio_data)

    _combine_mp3_chunks(
        audio_chunks,
        output_path
    )

    print(
        f"✅ Audio generated successfully:"
        f"\n   {output_path}"
    )

    return output_path


# ============================================================
# ARTICLE AUDIO GENERATION
# ============================================================

def generate_audio_from_article(
    article_content,
    headline="",
    output_path=None,
    language="en",
    max_length=None,
    slow=False
):
    """
    Generate professional news-style audio from an article.

    This function maintains the same interface as the previous
    AudioGeneratorUtility implementation.
    """

    if not article_content:
        raise ValueError(
            "article_content must not be empty."
        )

    article_content = _clean_text(article_content)

    if headline:
        headline = _clean_text(headline)

        # Put headline first so the news reader reads it naturally.
        article_content = (
            f"{headline}\n\n{article_content}"
        )

    if max_length and max_length > 0:
        article_content = article_content[:max_length]

    if not output_path:
        output_path = os.path.join(
            GENERATED_AUDIOS_DIR,
            f"article_audio_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

    return generate_audio_from_text(
        article_content,
        output_path,
        language,
        slow
    )


# ============================================================
# NEWS BULLETIN GENERATION
# ============================================================

def generate_news_bulletin(
    articles,
    output_path=None,
    language="en",
    intro_text="Here are today's top stories.",
    outro_text="That's all for now. Thank you for listening."
):
    """
    Generate a complete news bulletin from multiple articles.

    Args:
        articles:
            List of tuples:
                (headline, content)

        output_path:
            Output MP3 path.

        language:
            Language.

        intro_text:
            Opening text.

        outro_text:
            Closing text.

    Returns:
        str:
            Path to generated MP3.
    """

    if not articles:
        raise ValueError(
            "articles must contain at least one article."
        )

    bulletin_parts = []

    if intro_text:
        bulletin_parts.append(
            _clean_text(intro_text)
        )

    for index, article in enumerate(articles, start=1):

        if isinstance(article, (tuple, list)):

            if len(article) >= 2:
                headline = article[0]
                content = article[1]

                if headline:
                    bulletin_parts.append(
                        _clean_text(headline)
                    )

                if content:
                    bulletin_parts.append(
                        _clean_text(content)
                    )

            elif len(article) == 1:
                bulletin_parts.append(
                    _clean_text(article[0])
                )

        elif isinstance(article, str):

            bulletin_parts.append(
                _clean_text(article)
            )

    if outro_text:
        bulletin_parts.append(
            _clean_text(outro_text)
        )

    complete_bulletin = "\n\n".join(
        part
        for part in bulletin_parts
        if part
    )

    if not output_path:
        output_path = os.path.join(
            GENERATED_AUDIOS_DIR,
            f"news_bulletin_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

    return generate_audio_from_text(
        complete_bulletin,
        output_path,
        language,
        False
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def generate_audio_for_article(
    article_paragraph,
    file_name
):
    """
    Generate an MP3 voiceover for an article paragraph.

    Args:
        article_paragraph:
            Complete article text.

        file_name:
            Output filename without .mp3 extension.

    Returns:
        str:
            Path to generated MP3.
    """

    if not article_paragraph or not isinstance(
        article_paragraph,
        str
    ):
        raise ValueError(
            "article_paragraph must be a non-empty string"
        )

    if not file_name or not isinstance(
        file_name,
        str
    ):
        raise ValueError(
            "file_name must be a non-empty string"
        )

    output_path = _resolve_audio_path(
        file_name,
        "article_audio.mp3"
    )

    return generate_audio_from_article(
        article_paragraph,
        output_path=output_path
    )


# ============================================================
# AUDIO GENERATOR CLASS
# ============================================================

class AudioGenerator:
    """
    Wrapper class for professional audio/voiceover generation.

    Uses OpenAI GPT-4o Mini TTS directly.
    """

    def __init__(self, language="en"):
        """
        Initialize the Audio Generator.

        Args:
            language (str):
                Default language for audio generation.
        """

        self.language = language

    def generate_from_text(
        self,
        text,
        output_path=None,
        slow=False
    ):
        """
        Generate audio from text.

        Args:
            text:
                Text to convert to speech.

            output_path:
                Path to save audio file.

            slow:
                Kept for backward compatibility.
        """

        print(
            "\n🎤 Generating professional voiceover..."
        )

        print(
            f"📄 Text: "
            f"{text[:100]}"
            f"{'...' if len(text) > 100 else ''}"
        )

        print(
            f"🌐 Language: {self.language}"
        )

        output_path = _resolve_audio_path(
            output_path,
            f"generated_audio_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

        audio_path = generate_audio_from_text(
            text,
            output_path,
            self.language,
            slow
        )

        return audio_path

    def generate_from_article(
        self,
        article_content,
        headline="",
        output_path=None,
        max_length=None,
        slow=False
    ):
        """
        Generate professional news-style audio from an article.

        Args:
            article_content:
                Full article content.

            headline:
                Article headline.

            output_path:
                Path to save audio file.

            max_length:
                Maximum text length to read.

            slow:
                Kept for backward compatibility.
        """

        print(
            "\n📰 Generating audio from article..."
        )

        if headline:
            print(
                f"📌 Headline: {headline}"
            )

        output_path = _resolve_audio_path(
            output_path,
            f"article_audio_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
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

    def generate_bulletin(
        self,
        articles,
        output_path=None,
        intro_text="Here are today's top stories.",
        outro_text="That's all for now. Thank you for listening."
    ):
        """
        Generate a complete news bulletin from multiple articles.

        Args:
            articles:
                List of tuples:
                (headline, content)

            output_path:
                Path to save bulletin audio.

            intro_text:
                Opening text.

            outro_text:
                Closing text.
        """

        print(
            "\n📻 Generating news bulletin..."
        )

        print(
            f"📰 Number of stories: "
            f"{len(articles)}"
        )

        output_path = _resolve_audio_path(
            output_path,
            f"news_bulletin_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

        bulletin_path = generate_news_bulletin(
            articles,
            output_path,
            self.language,
            intro_text,
            outro_text
        )

        return bulletin_path


# ============================================================
# DIRECT EXECUTION / TEST
# ============================================================

if __name__ == "__main__":

    example_article = (
        "The Kennedy Center board voted to add President "
        "Donald Trump's name to the facade of the performing "
        "arts venue."
    )

    audio_path = generate_audio_for_article(
        example_article,
        "kennedy_center_political_audio"
    )

    print(
        f"\n🎧 Generated audio:"
        f"\n{audio_path}"
    )