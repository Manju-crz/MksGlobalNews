"""
PicsPicker - Image Generation Interface
Provides a user-friendly interface for generating images from text descriptions.
Uses ImageGeneratorUtility for the core functionality.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llmUtil.ImageGeneratorUtility import (
    generate_image_from_paragraph,
    generate_image_from_article,
    generate_images_batch
)

load_dotenv()


class PollinationsImageGenerator:
    """
    Wrapper class for Pollinations.AI image generation with user-friendly output.
    Uses ImageGeneratorUtility for core functionality.
    """

    def __init__(self):
        """Initialize the Pollinations Image Generator."""
        pass

    def generate_image_from_text(self, text_prompt, output_dir="generated_images", filename=None, width=1024, height=1024):
        """
        Generate an image from a text description.

        Args:
            text_prompt (str): Text description/paragraph to generate image from
            output_dir (str): Directory to save the generated image
            filename (str): Optional custom filename (without extension)
            width (int): Image width (default: 1024)
            height (int): Image height (default: 1024)

        Returns:
            str: Path to the saved image file, or None if generation failed
        """
        print(f"\n🎨 Generating image from text prompt...")
        print(f"📄 Prompt: {text_prompt[:100]}{'...' if len(text_prompt) > 100 else ''}")
        print(f"🤖 Service: Pollinations.AI (Free, No API Key Required)")
        print("⏳ Generating image...")

        # Use the utility function
        image_path = generate_image_from_paragraph(text_prompt, output_dir, filename, width, height)

        if image_path:
            print(f"✅ Image generated successfully!")
            print(f"💾 Saved to: {image_path}")
        else:
            print(f"❌ Image generation failed")

        return image_path

    def generate_image_from_article(self, article_content, headline="", output_dir="generated_images", filename=None):
        """
        Generate an image from an article.

        Args:
            article_content (str): Full article content
            headline (str): Article headline for context
            output_dir (str): Directory to save the generated image
            filename (str): Optional custom filename

        Returns:
            str: Path to the saved image file, or None if generation failed
        """
        print(f"\n📰 Generating image for article...")
        if headline:
            print(f"📌 Headline: {headline}")

        # Use the utility function
        image_path = generate_image_from_article(article_content, headline, output_dir, filename)

        if image_path:
            print(f"✅ Image generated successfully!")
            print(f"💾 Saved to: {image_path}")
        else:
            print(f"❌ Image generation failed")

        return image_path


class ImageGenerator:
    """
    Generates images from text descriptions using Hugging Face's Stable Diffusion models.
    Supports multiple open-source models for image generation.
    """

    def __init__(self, model="stabilityai/stable-diffusion-2-1"):
        """
        Initialize the ImageGenerator with a specific model.

        Args:
            model (str): Hugging Face model ID. Options:
                - "stabilityai/stable-diffusion-2-1" (default, high quality)
                - "runwayml/stable-diffusion-v1-5" (faster)
                - "CompVis/stable-diffusion-v1-4" (original)
        """
        self.api_key = os.getenv('HF_API_TOKEN')
        if not self.api_key:
            raise ValueError("HF_API_TOKEN not found in environment variables. "
                             "Get your free API key from: https://huggingface.co/settings/tokens")

        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_image_from_text(self, text_prompt, output_dir="generated_images", filename=None):
        """
        Generate an image from a text description.

        Args:
            text_prompt (str): Text description/paragraph to generate image from
            output_dir (str): Directory to save the generated image
            filename (str): Optional custom filename (without extension)

        Returns:
            str: Path to the saved image file, or None if generation failed
        """
        print(f"\n🎨 Generating image from text prompt...")
        print(f"📄 Prompt: {text_prompt[:100]}{'...' if len(text_prompt) > 100 else ''}")
        print(f"🤖 Model: {self.model}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}"

        output_path = os.path.join(output_dir, f"{filename}.png")

        # Prepare the request payload
        payload = {
            "inputs": text_prompt,
            "options": {
                "wait_for_model": True
            }
        }

        try:
            # Make API request
            print("⏳ Sending request to Hugging Face API...")
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)

            # Check if model is loading (503 status)
            if response.status_code == 503:
                print("⏳ Model is loading, waiting 20 seconds...")
                time.sleep(20)
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)

            # Check for successful response
            if response.status_code == 200:
                # Save the image
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                print(f"✅ Image generated successfully!")
                print(f"💾 Saved to: {output_path}")
                return output_path
            else:
                print(f"❌ Error generating image: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("❌ Request timed out. The model might be busy. Try again later.")
            return None
        except Exception as e:
            print(f"❌ Error generating image: {str(e)}")
            return None

    def generate_image_from_article(self, article_content, headline="", output_dir="generated_images", filename=None):
        """
        Generate an image from an article by creating a concise visual prompt.

        Args:
            article_content (str): Full article content
            headline (str): Article headline for context
            output_dir (str): Directory to save the generated image
            filename (str): Optional custom filename

        Returns:
            str: Path to the saved image file, or None if generation failed
        """
        # Create a concise prompt from the article
        # Take first 200 chars of article or use headline
        if headline:
            prompt = f"{headline}. {article_content[:200]}"
        else:
            prompt = article_content[:300]

        # Clean up the prompt (remove extra whitespace, newlines)
        prompt = " ".join(prompt.split())

        # Limit prompt length (Stable Diffusion works best with shorter prompts)
        if len(prompt) > 400:
            prompt = prompt[:400] + "..."

        print(f"\n📰 Generating image for article...")
        if headline:
            print(f"📌 Headline: {headline}")

        return self.generate_image_from_text(prompt, output_dir, filename)


def generate_image_for_paragraph(paragraph, output_dir="generated_images", filename=None, use_pollinations=True):
    """
    Convenience function to generate an image from a text paragraph.

    Args:
        paragraph (str): Text paragraph to generate image from
        output_dir (str): Directory to save the generated image
        filename (str): Optional custom filename
        use_pollinations (bool): Use Pollinations.AI (no API key) or Hugging Face (requires API key)

    Returns:
        str: Path to the saved image file, or None if generation failed
    """
    if use_pollinations:
        generator = PollinationsImageGenerator()
    else:
        generator = ImageGenerator()
    return generator.generate_image_from_text(paragraph, output_dir, filename)


if __name__ == "__main__":
    # Example usage with current affairs topics
    print("="*100)
    print("IMAGE GENERATOR - PICSPICKER (Using Pollinations.AI)")
    print("Current Affairs & News Examples")
    print("="*100)

    generator = PollinationsImageGenerator()

    # Example 1: Political News
    print("\n--- Example 1: Political News ---")
    political_headline = "Kennedy Center board votes to add Trump's name to the facade of the performing arts building"
    political_article = """
WASHINGTON (AP) — The Kennedy Center board voted on Thursday to add President Donald Trump's
name to the facade of the performing arts venue. The moves set up a test of U.S. District
Judge Christopher Cooper, who ruled in May that letters affixed to the building were added
illegally. During Trump's second term, the Kennedy Center has become an unlikely metaphor
of presidential power.
"""

    image_path = generator.generate_image_from_article(
        political_article,
        political_headline,
        filename="kennedy_center_political"
    )

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds to avoid rate limiting...")
    time.sleep(3)

    # Example 2: Sports News
    print("\n--- Example 2: Sports News ---")
    sports_headline = "WNBA condemns 'bad-faith' efforts to fuel transgender player debate"
    sports_article = """
The WNBA has issued a strong statement condemning what it calls 'bad-faith' efforts to
create controversy around transgender athletes in women's basketball. The league emphasized
its commitment to inclusivity while maintaining competitive integrity. Critics have slammed
ex-NBA players' push to enter WNBA draft, calling it a publicity stunt.
"""

    image_path = generator.generate_image_from_article(
        sports_article,
        sports_headline,
        filename="wnba_sports_news"
    )

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds to avoid rate limiting...")
    time.sleep(3)

    # Example 3: Technology & Business
    print("\n--- Example 3: Technology & Business News ---")
    tech_prompt = "Artificial intelligence data center, modern technology infrastructure, digital innovation, futuristic computing"
    image_path = generator.generate_image_from_text(
        tech_prompt,
        filename="ai_technology_news"
    )

    # Wait to avoid rate limiting
    print("\n⏳ Waiting 3 seconds to avoid rate limiting...")
    time.sleep(3)

    # Example 4: International Affairs
    print("\n--- Example 4: International Affairs ---")
    intl_headline = "Iran-backed Houthis clash with Yemeni forces and other Mideast developments"
    intl_article = """
Tensions escalated in the Middle East as Iran-backed Houthi forces engaged in clashes with
Yemeni government troops. The conflict represents the latest development in the ongoing
regional instability. International observers are monitoring the situation closely as it
could have broader implications for Middle Eastern geopolitics.
"""

    image_path = generator.generate_image_from_article(
        intl_article,
        intl_headline,
        filename="middle_east_conflict"
    )

    print("\n" + "="*100)
    print("✅ Image generation examples complete!")
    print("Check the 'generated_images' folder for your current affairs images!")