"""
ImageGeneratorUtility - Reusable Image Generation Utility
Provides a simple interface for generating images from text.
Supports multiple backends: Pollinations.AI (default) and Hugging Face Stable Diffusion
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse
import time

load_dotenv()


def generate_image_from_paragraph(paragraph, output_dir="generated_images", filename=None, width=1024, height=1024, timeout=60):
    """
    Generate an image from a text paragraph using Pollinations.AI.

    This is a reusable utility function that accepts a paragraph and returns the downloaded filename.
    No API key required - uses free Pollinations.AI service.

    Args:
        paragraph (str): Text paragraph/description to generate image from
        output_dir (str): Directory to save the generated image (default: "generated_images")
        filename (str): Optional custom filename without extension (default: auto-generated timestamp)
        width (int): Image width in pixels (default: 1024)
        height (int): Image height in pixels (default: 1024)
        timeout (int): Request timeout in seconds (default: 60)

    Returns:
        str: Full path to the downloaded image file, or None if generation failed

    Example:
        >>> image_path = generate_image_from_paragraph("A sunset over mountains")
        >>> print(image_path)
        'generated_images/generated_image_20260817_021500.png'
    """

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}"

    # Ensure filename doesn't have extension
    if filename.endswith('.png'):
        filename = filename[:-4]

    output_path = os.path.join(output_dir, f"{filename}.png")

    # URL encode the paragraph
    encoded_prompt = urllib.parse.quote(paragraph)

    # Build the Pollinations.AI image URL
    base_url = "https://image.pollinations.ai/prompt"
    image_url = f"{base_url}/{encoded_prompt}?width={width}&height={height}&nologo=true"

    try:
        # Make request to generate and download image
        response = requests.get(image_url, timeout=timeout)

        if response.status_code == 200:
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(response.content)

            return output_path
        else:
            print(f"Error generating image: HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"Request timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


def generate_image_huggingface(paragraph, output_dir="generated_images", filename=None, model="stabilityai/stable-diffusion-2-1", timeout=60):
    """
    Generate an image from a text paragraph using Hugging Face's Stable Diffusion API.

    Requires HF_API_TOKEN in environment variables.
    Use this method if Pollinations.AI doesn't work due to network/proxy issues.

    Args:
        paragraph (str): Text paragraph/description to generate image from
        output_dir (str): Directory to save the generated image (default: "generated_images")
        filename (str): Optional custom filename without extension (default: auto-generated timestamp)
        model (str): Hugging Face model ID. Options:
            - "stabilityai/stable-diffusion-2-1" (default, high quality)
            - "runwayml/stable-diffusion-v1-5" (faster)
            - "CompVis/stable-diffusion-v1-4" (original)
        timeout (int): Request timeout in seconds (default: 60)

    Returns:
        str: Full path to the downloaded image file, or None if generation failed

    Example:
        >>> image_path = generate_image_huggingface("A sunset over mountains")
        >>> print(image_path)
        'generated_images/generated_image_20260817_021500.png'
    """

    # Get API key from environment
    api_key = os.getenv('HF_API_TOKEN')
    if not api_key:
        print("Error: HF_API_TOKEN not found in environment variables")
        print("Get your free API key from: https://huggingface.co/settings/tokens")
        return None

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_image_{timestamp}"

    # Ensure filename doesn't have extension
    if filename.endswith('.png'):
        filename = filename[:-4]

    output_path = os.path.join(output_dir, f"{filename}.png")

    # Hugging Face API setup
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Prepare the request payload
    payload = {
        "inputs": paragraph,
        "options": {
            "wait_for_model": True
        }
    }

    try:
        # Make API request
        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)

        # Check if model is loading (503 status)
        if response.status_code == 503:
            print("Model is loading, waiting 20 seconds...")
            time.sleep(20)
            response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)

        # Check for successful response
        if response.status_code == 200:
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(response.content)

            return output_path
        else:
            print(f"Error generating image: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"Request timed out after {timeout} seconds")
        return None
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


def generate_image_from_article(article_content, headline="", output_dir="generated_images", filename=None, width=1024, height=1024, use_huggingface=False):
    """
    Generate an image from a news article by creating a concise visual prompt.

    Args:
        article_content (str): Full article content
        headline (str): Article headline for context (optional)
        output_dir (str): Directory to save the generated image
        filename (str): Optional custom filename without extension
        width (int): Image width in pixels (default: 1024)
        height (int): Image height in pixels (default: 1024)
        use_huggingface (bool): Use Hugging Face API instead of Pollinations (default: False)

    Returns:
        str: Full path to the downloaded image file, or None if generation failed

    Example:
        >>> # Using Pollinations (default)
        >>> image_path = generate_image_from_article(
        ...     article_content="The stock market reached new highs...",
        ...     headline="Stock Market Hits Record High",
        ...     filename="stock_market_news"
        ... )

        >>> # Using Hugging Face
        >>> image_path = generate_image_from_article(
        ...     article_content="...",
        ...     headline="...",
        ...     filename="news",
        ...     use_huggingface=True
        ... )
    """

    # Create a concise prompt from the article
    if headline:
        prompt = f"{headline}. {article_content[:200]}"
    else:
        prompt = article_content[:300]

    # Clean up the prompt (remove extra whitespace, newlines)
    prompt = " ".join(prompt.split())

    # Limit prompt length (Stable Diffusion works best with shorter prompts)
    if len(prompt) > 400:
        prompt = prompt[:400] + "..."

    # Choose backend
    if use_huggingface:
        return generate_image_huggingface(prompt, output_dir, filename)
    else:
        return generate_image_from_paragraph(prompt, output_dir, filename, width, height)


def generate_images_batch(paragraphs, output_dir="generated_images", delay=3):
    """
    Generate multiple images from a list of paragraphs with delays to avoid rate limiting.

    Args:
        paragraphs (list): List of text paragraphs to generate images from
        output_dir (str): Directory to save the generated images
        delay (int): Delay in seconds between requests (default: 3)

    Returns:
        list: List of tuples (paragraph, image_path) for successful generations

    Example:
        >>> paragraphs = ["A sunset", "A mountain", "A city"]
        >>> results = generate_images_batch(paragraphs, delay=5)
        >>> for para, path in results:
        ...     print(f"{para}: {path}")
    """

    results = []

    for idx, paragraph in enumerate(paragraphs, 1):
        print(f"\n[{idx}/{len(paragraphs)}] Generating image...")

        # Generate filename based on index
        filename = f"batch_image_{idx}"

        # Generate image
        image_path = generate_image_from_paragraph(paragraph, output_dir, filename)

        if image_path:
            results.append((paragraph, image_path))
            print(f"✅ Success: {image_path}")
        else:
            print(f"❌ Failed for: {paragraph[:50]}...")

        # Add delay between requests (except for last one)
        if idx < len(paragraphs):
            print(f"⏳ Waiting {delay} seconds...")
            time.sleep(delay)

    return results


if __name__ == "__main__":
    # Test the utility
    print("=" * 100)
    print("IMAGE GENERATOR UTILITY - TEST")
    print("=" * 100)

    # Test 1: Pollinations.AI (Default - No API Key Required)
    print("\n🖼️ Test 1: Pollinations.AI (Default) ---")
    test_paragraph = "A peaceful sunset over a calm ocean with sailboats"
    image_path = generate_image_from_paragraph(
        test_paragraph,
        filename="test_pollinations_sunset"
    )

    if image_path:
        print(f"✅ Image saved to: {image_path}")
    else:
        print("❌ Image generation failed")

    # Test 2: Article with Pollinations
    print("\n📰 Test 2: Article with Pollinations ---")
    test_headline = "Stock Market Reaches All-Time High"
    test_article = "Wall Street celebrated today as the stock market reached record highs..."

    image_path = generate_image_from_article(
        test_article,
        test_headline,
        filename="test_pollinations_stock",
        use_huggingface=False
    )

    if image_path:
        print(f"✅ Image saved to: {image_path}")
    else:
        print("❌ Image generation failed")

    # Test 3: Hugging Face Stable Diffusion (Requires HF_API_TOKEN)
    print("\n🖼️ Test 3: Hugging Face Stable Diffusion ---")
    print("Note: This requires HF_API_TOKEN in .env file")

    hf_paragraph = "A futuristic city skyline at night with neon lights"
    image_path = generate_image_huggingface(
        hf_paragraph,
        filename="test_huggingface_city"
    )

    if image_path:
        print(f"✅ Image saved to: {image_path}")
    else:
        print("❌ Image generation failed (check if HF_API_TOKEN is set)")

    # Test 4: Article with Hugging Face
    print("\n📰 Test 4: Article with Hugging Face ---")

    image_path = generate_image_from_article(
        test_article,
        test_headline,
        filename="test_huggingface_stock",
        use_huggingface=True
    )

    if image_path:
        print(f"✅ Image saved to: {image_path}")
    else:
        print("❌ Image generation failed")

    print("\n" + "=" * 100)
    print("✅ Utility test complete!")
    print("Both Pollinations.AI and Hugging Face methods are available.")
    print("Use Pollinations (default) for no-API-key usage.")
    print("Use Hugging Face if you have proxy issues or want higher quality.")
    print("=" * 100)