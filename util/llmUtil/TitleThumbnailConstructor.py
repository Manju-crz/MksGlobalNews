import os
import re
import base64
from pathlib import Path
from typing import Union, List, Dict

from openai import OpenAI


# ============================================================
# CONFIGURATION
# ============================================================

TEXT_MODEL = "gpt-5.6-luna"
IMAGE_MODEL = "gpt-image-2"

MAX_TITLE_LENGTH = 60

# Folder where generated thumbnails will be stored
THUMBNAIL_DIR = Path("generated_thumbnails")
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_openai_client() -> OpenAI:
    """
    Creates and returns an OpenAI client.

    Requires:
        OPENAI_API_KEY environment variable.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set."
        )

    return OpenAI(api_key=api_key)


# ============================================================
# HELPER: NORMALIZE INPUT
# ============================================================

def normalize_content(
    headings: Union[str, List[str], tuple]
) -> str:
    """
    Accepts either:

        "Single heading"

    OR:

        ["Heading 1", "Heading 2", "Heading 3"]

    Returns a single formatted text block.
    """

    if isinstance(headings, str):
        return headings.strip()

    if isinstance(headings, (list, tuple)):
        cleaned = []

        for item in headings:
            if item is None:
                continue

            item = str(item).strip()

            if item:
                cleaned.append(item)

        if not cleaned:
            raise ValueError("No valid headings/content were provided.")

        return "\n".join(
            f"- {item}"
            for item in cleaned
        )

    raise TypeError(
        "headings must be a string, list, or tuple."
    )


# ============================================================
# HELPER: CLEAN TITLE
# ============================================================

def clean_title(title: str) -> str:
    """
    Cleans an LLM-generated title.
    """

    if not title:
        return ""

    title = title.strip()

    # Remove surrounding quotes
    title = title.strip('"').strip("'").strip()

    # Remove accidental numbering such as:
    # 1. Title
    # 2) Title
    title = re.sub(
        r"^\s*\d+[\.\)]\s*",
        "",
        title
    )

    # Remove markdown formatting
    title = title.replace("**", "")
    title = title.replace("__", "")

    # Remove unnecessary newlines
    title = " ".join(title.split())

    return title.strip()


# ============================================================
# HELPER: ENSURE TITLE <= 60 CHARACTERS
# ============================================================

def enforce_title_length(title: str) -> str:
    """
    Ensures the final title is no longer than 60 characters.

    The LLM should normally already produce a <=60 character
    title, but this is a final safety check.
    """

    title = clean_title(title)

    if len(title) <= MAX_TITLE_LENGTH:
        return title

    # First attempt:
    # Cut at the last word before 60 chars.
    shortened = title[:MAX_TITLE_LENGTH]

    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0]

    return shortened.rstrip(".,:;-!? ")


# ============================================================
# GENERATE YOUTUBE TITLE
# ============================================================

def generate_youtube_title(
    client: OpenAI,
    content: str
) -> str:
    """
    Generates one highly clickable YouTube title.

    Requirements:
        - Maximum 60 characters
        - Catchy
        - Natural
        - Accurate to the supplied content
        - Suitable for YouTube
    """

    prompt = f"""
You are an expert YouTube title strategist.

Create ONE highly clickable YouTube video title based ONLY
on the information provided below.

TITLE REQUIREMENTS:

1. Maximum 60 characters INCLUDING spaces.
2. The title must be catchy and curiosity-driven.
3. It should encourage viewers to click.
4. It must accurately represent the content.
5. Do NOT use misleading clickbait.
6. Use strong, natural keywords when appropriate.
7. Make it sound like a professional human-created YouTube title.
8. Avoid generic titles.
9. Do not use quotation marks around the title.
10. Do not add numbering.
11. Return ONLY the title.
12. Before returning it, COUNT THE CHARACTERS.
13. The final title MUST be 60 characters or fewer.

CONTENT:

{content}
"""

    response = client.responses.create(
        model=TEXT_MODEL,
        input=prompt
    )

    title = response.output_text.strip()

    title = clean_title(title)

    # Safety check
    title = enforce_title_length(title)

    if not title:
        raise RuntimeError(
            "LLM returned an empty YouTube title."
        )

    return title


# ============================================================
# GENERATE THUMBNAIL
# ============================================================

def generate_youtube_thumbnail(
    client: OpenAI,
    content: str,
    title: str,
    output_filepath: str
) -> str:
    """
    Generates a YouTube thumbnail using the same source content
    used for title generation.

    Args:
        client: OpenAI client
        content: Video content
        title: Video title
        output_filepath: Full path where the thumbnail should be saved (including filename)

    Returns:
        Full path of the generated thumbnail.
    """

    if not output_filepath:
        raise ValueError("output_filepath parameter is required")

    # Create the directory if it doesn't exist
    output_path = Path(output_filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    thumbnail_prompt = f"""
Create a highly engaging YouTube thumbnail for a news/current-affairs
video.

VIDEO TITLE:
{title}

VIDEO CONTENT:
{content}

THUMBNAIL REQUIREMENTS:

- YouTube thumbnail composition.
- Landscape 16:9 aspect ratio.
- Cinematic and visually dramatic.
- Strong visual hierarchy.
- Eye-catching and professional.
- High contrast.
- Main subject should be immediately understandable.
- Create curiosity without misleading the viewer.
- Use realistic photographic style when appropriate.
- Avoid clutter.
- Leave some clean visual space for YouTube UI.
- Do NOT reproduce the entire title as text.
- Prefer little or no text inside the generated image.
- Do NOT add logos, watermarks, channel names or fake news branding.
- The image should visually communicate the main story.
"""

    result = client.images.generate(
        model=IMAGE_MODEL,
        prompt=thumbnail_prompt,
        size="1536x864",
        quality="medium",
        output_format="png"
    )

    image_base64 = result.data[0].b64_json

    if not image_base64:
        raise RuntimeError(
            "Image generation returned no image data."
        )

    image_bytes = base64.b64decode(image_base64)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path.resolve())


# ============================================================
# MAIN REUSABLE METHOD
# ============================================================

def generate_youtube_assets(
    headings: Union[str, List[str], tuple],
    thumbnail_filepath: str = None
) -> Dict[str, str]:
    """
    Main reusable method.

    INPUT:
        headings:
            Either one string:

                "Canada's top general loses election..."

            OR multiple headings:

                [
                    "Canada's top general loses election",
                    "NATO Military Committee leadership changes",
                    "Major development inside NATO"
                ]

        thumbnail_filepath:
            Full path where the thumbnail should be saved (including filename).
            Required if you want to generate a thumbnail.

    OUTPUT:

        {
            "title": "...",
            "thumbnail_file": "..."
        }
    """

    # --------------------------------------------------------
    # 1. Normalize input
    # --------------------------------------------------------

    content = normalize_content(headings)

    # --------------------------------------------------------
    # 2. Create OpenAI client
    # --------------------------------------------------------

    client = get_openai_client()

    # --------------------------------------------------------
    # 3. Generate YouTube title
    # --------------------------------------------------------

    title = generate_youtube_title(
        client=client,
        content=content
    )

    # --------------------------------------------------------
    # 4. Generate thumbnail (if filepath provided)
    # --------------------------------------------------------

    thumbnail_file = None
    if thumbnail_filepath:
        thumbnail_file = generate_youtube_thumbnail(
            client=client,
            content=content,
            title=title,
            output_filepath=thumbnail_filepath
        )

    # --------------------------------------------------------
    # 5. Return both
    # --------------------------------------------------------

    return {
        "title": title,
        "thumbnail_file": thumbnail_file
    }


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":

    headings = [
        "Canada's top general loses election to become head of key NATO Military Committee",
        "Canada's military chief was defeated in the NATO leadership race",
        "The election creates a major change in NATO military leadership"
    ]

    result = generate_youtube_assets(headings)

    print("\n" + "=" * 80)
    print("GENERATED YOUTUBE ASSETS")
    print("=" * 80)

    print(f"Title          : {result['title']}")
    print(f"Title Length   : {len(result['title'])}")
    print(f"Thumbnail File : {result['thumbnail_file']}")

    print("=" * 80)