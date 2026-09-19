"""
picsGenerator - Image Generation Interface

Generates images from complete text descriptions/articles using
OpenAI GPT-Image-1 Mini.

Final output:
    1536 x 864 pixels
    16:9 aspect ratio
    PNG format

The existing public functions/classes are preserved so that other
parts of the project do not need to be changed.
"""

import os
import sys
import base64
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


# ============================================================
# PROJECT PATHS
# ============================================================

# Add parent directory to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENERATED_IMAGES_DIR = os.path.join(
    PROJECT_ROOT,
    "dumps",
    "generated_images"
)

sys.path.insert(0, PROJECT_ROOT)

load_dotenv()


# ============================================================
# OPENAI CONFIGURATION
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables.\n"
        "Please add the following to your .env file:\n\n"
        "OPENAI_API_KEY=your_api_key_here"
    )


# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# IMAGE CONFIGURATION
# ============================================================

# OpenAI GPT-Image-1 Mini currently supports 1536x1024 as a
# landscape generation size.
OPENAI_GENERATION_SIZE = "1536x1024"

# Final image required for your YouTube videos.
# 1536 / 864 = 16 / 9
FINAL_WIDTH = 1536
FINAL_HEIGHT = 864

OPENAI_MODEL = "gpt-image-1-mini"

# Cheapest generation quality.
IMAGE_QUALITY = "low"


# ============================================================
# INTERNAL HELPER FUNCTIONS
# ============================================================

def _create_output_path(output_dir, filename):
    """
    Create the final PNG output path.

    Args:
        output_dir (str): Directory where image will be saved.
        filename (str): Filename with or without .png.

    Returns:
        str: Complete output path.
    """

    os.makedirs(output_dir, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}"

    if filename.lower().endswith(".png"):
        filename = filename[:-4]

    return os.path.join(output_dir, f"{filename}.png")


def _crop_to_16_9(image):
    """
    Center-crop an image to exactly 16:9.

    GPT-Image-1 Mini generates at 1536x1024.
    This function converts that 3:2 image into:

        1536 x 864

    which is exactly 16:9.

    Args:
        image (PIL.Image.Image): Generated image.

    Returns:
        PIL.Image.Image: Cropped 16:9 image.
    """

    original_width, original_height = image.size

    target_ratio = FINAL_WIDTH / FINAL_HEIGHT
    original_ratio = original_width / original_height

    # If already 16:9, simply resize if required.
    if abs(original_ratio - target_ratio) < 0.001:

        if image.size != (FINAL_WIDTH, FINAL_HEIGHT):
            image = image.resize(
                (FINAL_WIDTH, FINAL_HEIGHT),
                Image.Resampling.LANCZOS
            )

        return image

    # For 1536x1024:
    #
    # width = 1536
    # target height = 1536 / (16/9)
    #              = 864
    #
    # Therefore, crop 80 pixels from top and bottom.

    target_height = int(original_width / target_ratio)

    if target_height <= original_height:

        top = (original_height - target_height) // 2
        bottom = top + target_height

        image = image.crop(
            (
                0,
                top,
                original_width,
                bottom
            )
        )

    else:

        target_width = int(original_height * target_ratio)

        left = (original_width - target_width) // 2
        right = left + target_width

        image = image.crop(
            (
                left,
                0,
                right,
                original_height
            )
        )

    # Ensure exact final dimensions.
    image = image.resize(
        (FINAL_WIDTH, FINAL_HEIGHT),
        Image.Resampling.LANCZOS
    )

    return image


def _generate_openai_image(
    text_prompt,
    output_dir=GENERATED_IMAGES_DIR,
    filename=None
):
    """
    Generate an image using OpenAI GPT-Image-1 Mini.

    The complete supplied text is sent to the model as the prompt.
    The generated image is then cropped to exactly 16:9.

    Args:
        text_prompt (str): Complete text prompt/article.
        output_dir (str): Output directory.
        filename (str): Output filename without extension.

    Returns:
        str: Path to the generated PNG file, or None if generation fails.
    """

    if not text_prompt or not isinstance(text_prompt, str):
        raise ValueError("text_prompt must be a non-empty string")

    os.makedirs(output_dir, exist_ok=True)

    output_path = _create_output_path(
        output_dir,
        filename
    )

    print("\n🎨 Generating image from text prompt...")
    print(
        f"📄 Prompt: "
        f"{text_prompt[:150]}"
        f"{'...' if len(text_prompt) > 150 else ''}"
    )

    print(f"🤖 Model: {OPENAI_MODEL}")
    print(f"📐 Generation size: {OPENAI_GENERATION_SIZE}")
    print(f"🎬 Final size: {FINAL_WIDTH}x{FINAL_HEIGHT} (16:9)")
    print(f"⚙️ Quality: {IMAGE_QUALITY}")
    print("⏳ Generating image...")

    try:

        # ========================================================
        # OPENAI IMAGE GENERATION
        # ========================================================

        result = client.images.generate(
            model=OPENAI_MODEL,
            prompt=text_prompt,
            size=OPENAI_GENERATION_SIZE,
            quality=IMAGE_QUALITY,
            output_format="png",
            n=1
        )

        if not result.data:
            print("❌ OpenAI returned no image data.")
            return None

        image_base64 = result.data[0].b64_json

        if not image_base64:
            print("❌ OpenAI returned empty image data.")
            return None

        # ========================================================
        # DECODE IMAGE
        # ========================================================

        image_bytes = base64.b64decode(image_base64)

        temporary_path = output_path.replace(
            ".png",
            "_original.png"
        )

        with open(temporary_path, "wb") as image_file:
            image_file.write(image_bytes)

        print(
            f"✅ OpenAI image generated: "
            f"{OPENAI_GENERATION_SIZE}"
        )

        # ========================================================
        # OPEN IMAGE WITH PILLOW
        # ========================================================

        image = Image.open(temporary_path)

        print(
            f"📐 Original image dimensions: "
            f"{image.width}x{image.height}"
        )

        # ========================================================
        # CONVERT TO EXACT 16:9
        # ========================================================

        image_16_9 = _crop_to_16_9(image)

        # Ensure RGB/RGBA compatibility for PNG.
        if image_16_9.mode not in ("RGB", "RGBA"):
            image_16_9 = image_16_9.convert("RGB")

        image_16_9.save(
            output_path,
            format="PNG"
        )

        # ========================================================
        # REMOVE TEMPORARY ORIGINAL IMAGE
        # ========================================================

        try:
            os.remove(temporary_path)
        except OSError:
            pass

        print(
            f"✅ Final 16:9 image generated successfully!"
        )

        print(
            f"📐 Final dimensions: "
            f"{image_16_9.width}x{image_16_9.height}"
        )

        print(
            f"💾 Saved to: {output_path}"
        )

        return output_path

    except Exception as e:

        print(
            f"❌ Error generating image with OpenAI: {str(e)}"
        )

        return None


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def generate_image_for_article(article_paragraph, file_name):
    """
    Generate a PNG image for an article paragraph.

    The complete article text is passed directly to GPT-Image-1 Mini.

    Args:
        article_paragraph (str):
            Complete article text used as the image prompt.

        file_name (str):
            Output filename with or without .png extension.

    Returns:
        str:
            Path to the generated PNG image,
            or None if generation failed.
    """

    if not article_paragraph or not isinstance(article_paragraph, str):
        raise ValueError(
            "article_paragraph must be a non-empty string"
        )

    if not file_name or not isinstance(file_name, str):
        raise ValueError(
            "file_name must be a non-empty string"
        )

    os.makedirs(
        GENERATED_IMAGES_DIR,
        exist_ok=True
    )

    filename = file_name

    if filename.lower().endswith(".png"):
        filename = filename[:-4]

    return _generate_openai_image(
        article_paragraph,
        output_dir=GENERATED_IMAGES_DIR,
        filename=filename
    )


# ============================================================
# COMPATIBILITY CLASS
# ============================================================

class PollinationsImageGenerator:
    """
    Compatibility wrapper.

    The old project used Pollinations.AI.

    The class name is intentionally preserved so that existing
    code calling PollinationsImageGenerator() does not break.

    Internally, it now uses OpenAI GPT-Image-1 Mini.
    """

    def __init__(self):
        """Initialize the image generator."""
        pass

    def generate_image_from_text(
        self,
        text_prompt,
        output_dir=GENERATED_IMAGES_DIR,
        filename=None,
        width=1536,
        height=864
    ):
        """
        Generate an image from a complete text description.

        The width/height arguments are retained for compatibility
        with the previous implementation.

        Final output is always exactly 1536x864 (16:9).

        Args:
            text_prompt (str):
                Complete text description.

            output_dir (str):
                Directory where image is saved.

            filename (str):
                Optional filename.

            width (int):
                Retained for compatibility.

            height (int):
                Retained for compatibility.

        Returns:
            str:
                Path to generated image, or None.
        """

        print(
            "\n🎨 Generating image from text prompt..."
        )

        print(
            f"📄 Prompt: "
            f"{text_prompt[:150]}"
            f"{'...' if len(text_prompt) > 150 else ''}"
        )

        print(
            f"🤖 Service: OpenAI GPT-Image-1 Mini"
        )

        print(
            "📺 Output: 1536x864 (16:9)"
        )

        image_path = _generate_openai_image(
            text_prompt,
            output_dir,
            filename
        )

        if image_path:

            print(
                "✅ Image generated successfully!"
            )

            print(
                f"💾 Saved to: {image_path}"
            )

        else:

            print(
                "❌ Image generation failed"
            )

        return image_path

    def generate_image_from_article(
        self,
        article_content,
        headline="",
        output_dir=GENERATED_IMAGES_DIR,
        filename=None
    ):
        """
        Generate an image from a complete article.

        Unlike the previous implementation, this function DOES NOT
        truncate the article.

        The complete article is passed to GPT-Image-1 Mini.

        Args:
            article_content (str):
                Full article content.

            headline (str):
                Optional article headline.

            output_dir (str):
                Directory where image is saved.

            filename (str):
                Optional filename.

        Returns:
            str:
                Path to generated image, or None.
        """

        if not article_content or not isinstance(
            article_content,
            str
        ):
            raise ValueError(
                "article_content must be a non-empty string"
            )

        print(
            "\n📰 Generating image for article..."
        )

        if headline:

            print(
                f"📌 Headline: {headline}"
            )

            # Include the headline together with the complete
            # article content.
            prompt = (
                f"Headline:\n{headline}\n\n"
                f"Article:\n{article_content}"
            )

        else:

            prompt = article_content

        return _generate_openai_image(
            prompt,
            output_dir,
            filename
        )


# ============================================================
# SECOND COMPATIBILITY CLASS
# ============================================================

class ImageGenerator:
    """
    Compatibility wrapper for the previous Hugging Face
    Stable Diffusion implementation.

    The class name and public methods are preserved.

    Internally, OpenAI GPT-Image-1 Mini is now used.
    """

    def __init__(
        self,
        model=OPENAI_MODEL
    ):
        """
        Initialize the OpenAI image generator.

        Args:
            model (str):
                OpenAI image model name.

                Default:
                    gpt-image-1-mini
        """

        self.model = model

    def generate_image_from_text(
        self,
        text_prompt,
        output_dir=GENERATED_IMAGES_DIR,
        filename=None
    ):
        """
        Generate an image from a complete text description.

        Args:
            text_prompt (str):
                Complete text description.

            output_dir (str):
                Directory where image is saved.

            filename (str):
                Optional filename.

        Returns:
            str:
                Path to generated image, or None.
        """

        print(
            "\n🎨 Generating image from text prompt..."
        )

        print(
            f"📄 Prompt: "
            f"{text_prompt[:150]}"
            f"{'...' if len(text_prompt) > 150 else ''}"
        )

        print(
            f"🤖 Model: {self.model}"
        )

        return _generate_openai_image(
            text_prompt,
            output_dir,
            filename
        )

    def generate_image_from_article(
        self,
        article_content,
        headline="",
        output_dir=GENERATED_IMAGES_DIR,
        filename=None
    ):
        """
        Generate an image from the complete article.

        The complete article is passed to the image model without
        truncation.

        Args:
            article_content (str):
                Full article content.

            headline (str):
                Optional headline.

            output_dir (str):
                Directory where image is saved.

            filename (str):
                Optional filename.

        Returns:
            str:
                Path to generated image, or None.
        """

        if not article_content or not isinstance(
            article_content,
            str
        ):
            raise ValueError(
                "article_content must be a non-empty string"
            )

        if headline:

            prompt = (
                f"Headline:\n{headline}\n\n"
                f"Article:\n{article_content}"
            )

        else:

            prompt = article_content

        print(
            "\n📰 Generating image for article..."
        )

        if headline:

            print(
                f"📌 Headline: {headline}"
            )

        return self.generate_image_from_text(
            prompt,
            output_dir,
            filename
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def generate_image_for_paragraph(
    paragraph,
    output_dir=GENERATED_IMAGES_DIR,
    filename=None,
    use_pollinations=True
):
    """
    Generate an image from a complete text paragraph.

    The existing function signature is preserved for compatibility.

    The use_pollinations parameter is retained but is no longer used.
    OpenAI GPT-Image-1 Mini is always used.

    Args:
        paragraph (str):
            Complete text paragraph.

        output_dir (str):
            Directory where image is saved.

        filename (str):
            Optional filename.

        use_pollinations (bool):
            Retained for compatibility.

    Returns:
        str:
            Path to generated image, or None.
    """

    if not paragraph or not isinstance(
        paragraph,
        str
    ):
        raise ValueError(
            "paragraph must be a non-empty string"
        )

    return _generate_openai_image(
        paragraph,
        output_dir,
        filename
    )


# ============================================================
# TEST / DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    example_article = (
        "The Kennedy Center board voted to add President Donald Trump's "
        "name to the facade of the performing arts venue."
    )

    image_path = generate_image_for_article(
        example_article,
        "kennedy_center_political"
    )

    print(
        f"\nGenerated image: {image_path}"
    )

