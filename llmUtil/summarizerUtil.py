import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Huggingging Face imports
try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: huggingface_hub not installed. Install with: pip install huggingface_hub")


# Google Gemini imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Install with: pip install google-generativeai")


# Ollama imports (uses requests - no special package needed)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not installed. Install with: pip install requests")


def summarize_article_with_groq(article_text, api_key=None, model="llama-3.3-70b-versatile"):
    """
    Summarize an article using Groq's LLM models.

    Args:
        article_text (str): The article text to summarize
        api_key (str): Groq API key (optional, reads from environment if not provided)
        model (str): Model name to use (default: "llama-3.3-70b-versatile")

    Returns:
        str: Summarized article text

    Available Models:
        - llama-3.3-70b-versatile (Recommended - Fast, powerful)
        - llama-3.1-70b-versatile
        - mixtral-8x7b-32768
        - gemma2-9b-it

    Examples:
        # With API key from environment
        summary = summarize_article_with_groq("Long article text here...")

        # With explicit API key
        summary = summarize_article_with_groq("Long article text...", api_key="your_api_key")

        # With different model
        summary = summarize_article_with_groq("Article...", model="mixtral-8x7b-32768")
    """

    try:
        # Initialize Groq client
        if api_key is None:
            # Try to get API key from environment variable
            api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            print("Error: GROQ_API_KEY not found. Please set it as an environment variable or pass it as a parameter.")
            return None

        client = Groq(api_key=api_key)

        # Create the prompt for summarization
        prompt = f"""Please summarize the following article in a concise and clear manner.
Focus on the main points and key information.

Article:
{article_text}

Summary:"""

        print(f"Sending request to Groq API (Model: {model})...")

        # Call the Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        # Extract the summary from the response
        summary = chat_completion.choices[0].message.content

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Groq API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_with_custom_instructions(article_text, custom_instruction, api_key=None, model="llama-3.3-70b-versatile"):
    """
    Summarize an article with custom instructions using Groq's LLM models.

    Args:
        article_text (str): The article text to summarize
        custom_instruction (str): Custom instructions for summarization
        api_key (str): Groq API key (optional)
        model (str): Model name to use (default: "llama-3.3-70b-versatile")

    Returns:
        str: Summarized article text

    Examples:
        # 3 bullet points
        summary = summarize_with_custom_instructions(
            "Article text...",
            "Summarize in 3 bullet points"
        )

        # One sentence
        summary = summarize_with_custom_instructions(
            "Article text...",
            "Summarize in ONE sentence only"
        )

        # Custom format
        summary = summarize_with_custom_instructions(
            "Article text...",
            "Summarize as a tweet (max 280 characters)"
        )
    """

    try:
        # Initialize Groq client
        if api_key is None:
            api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            print("Error: GROQ_API_KEY not found.")
            return None

        client = Groq(api_key=api_key)

        # Create the prompt with custom instructions
        prompt = f"""{custom_instruction}

Article:
{article_text}

Summary:"""

        print(f"Sending request to Groq API with custom instructions (Model: {model})...")

        # Call the Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        # Extract the summary
        summary = chat_completion.choices[0].message.content

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Groq API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_article_with_huggingface(article_text, api_key=None, model="meta-llama/Llama-3.2-3B-Instruct", max_tokens=500):
    """
    Summarize an article using Hugging Face Inference API (100% FREE - No daily limits!).

    Args:
        article_text (str): The article text to summarize
        api_key (str): Hugging Face API token (optional, reads from HF_API_TOKEN env var if not provided)
        model (str): Model name to use (default: "meta-llama/Llama-3.2-3B-Instruct")
        max_tokens (int): Maximum tokens for summary (default: 500)

    Returns:
        str: Summarized article text

    Available FREE Models:
        - meta-llama/Llama-3.2-3B-Instruct (Recommended - Fast, good quality)
        - meta-llama/Llama-3.2-1B-Instruct (Faster, smaller)
        - mistralai/Mistral-7B-Instruct-v0.3 (High quality)
        - google/gemma-2-2b-it (Fast, efficient)
        - Qwen/Qwen2.5-7B-Instruct (Good balance)

    Examples:
        # With API key from environment
        summary = summarize_article_with_huggingface("Long article text here...")

        # With explicit API key
        summary = summarize_article_with_huggingface("Article...", api_key="hf_xxx")

        # With different model
        summary = summarize_article_with_huggingface(
            "Article...",
            model="mistralai/Mistral-7B-Instruct-v0.3"
        )

    Setup:
        1. Install: pip install huggingface_hub
        2. Get free token: https://huggingface.co/settings/tokens
        3. Set in .env: HF_API_TOKEN=your_token_here
    """

    try:
        if not HF_AVAILABLE:
            print("Error: huggingface_hub not installed. Install with: pip install huggingface_hub")
            return None

        # Initialize Hugging Face client
        if api_key is None:
            # Try to get API key from environment variable
            api_key = os.environ.get("HF_API_TOKEN")

        if not api_key:
            print("Error: HF_API_TOKEN not found. Please set it as an environment variable or pass it as a parameter.")
            print("Get your free token at: https://huggingface.co/settings/tokens")
            return None

        client = InferenceClient(token=api_key)

        # Create the messages for chat completion
        messages = [
            {
                "role": "user",
                "content": f"Please summarize the following article in a concise and clear manner. Focus on the main points and key information.\n\nArticle:\n{article_text}\n\nSummary:"
            }
        ]

        print(f"Sending request to Hugging Face API (Model: {model})...")

        # Call the Hugging Face Inference API using chat completion
        response = client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=0.9,
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content.strip()

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Hugging Face API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_with_huggingface_custom(article_text, custom_instruction, api_key=None, model="meta-llama/Llama-3.2-3B-Instruct", max_tokens=500):
    """
    Summarize an article with custom instructions using Hugging Face Inference API.

    Args:
        article_text (str): The article text to summarize
        custom_instruction (str): Custom instructions for summarization
        api_key (str): Hugging Face API token (optional)
        model (str): Model name to use
        max_tokens (int): Maximum tokens for summary

    Returns:
        str: Summarized article text

    Examples:
        # 3 bullet points
        summary = summarize_with_huggingface_custom(
            "Article text...",
            "Summarize in 3 bullet points"
        )

        # One sentence
        summary = summarize_with_huggingface_custom(
            "Article text...",
            "Summarize in ONE sentence only"
        )
    """

    try:
        if not HF_AVAILABLE:
            print("Error: huggingface_hub not installed.")
            return None

        # Initialize Hugging Face client
        if api_key is None:
            api_key = os.environ.get("HF_API_TOKEN")

        if not api_key:
            print("Error: HF_API_TOKEN not found.")
            return None

        client = InferenceClient(token=api_key)

        # Create the messages for chat completion with custom instructions
        messages = [
            {
                "role": "user",
                "content": f"{custom_instruction}\n\nArticle:\n{article_text}\n\nSummary:"
            }
        ]

        print(f"Sending request to Hugging Face API with custom instructions (Model: {model})...")

        # Call the Hugging Face Inference API using chat completion
        response = client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.5,
            top_p=0.9,
        )

        # Extract the summary
        summary = response.choices[0].message.content.strip()

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Hugging Face API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_article_with_gemini(article_text, api_key=None, model="gemini-1.5-flash", max_tokens=500):
    """
    Summarize an article using Google Gemini API (FREE - 1M tokens/day!).

    Args:
        article_text (str): The article text to summarize
        api_key (str): Google Gemini API key (optional, reads from GEMINI_API_KEY env var if not provided)
        model (str): Model name to use (default: "gemini-1.5-flash")
        max_tokens (int): Maximum tokens for summary (default: 500)

    Returns:
        str: Summarized article text

    Available FREE Models:
        - gemini-1.5-flash (Recommended - Fast, efficient, FREE)
        - gemini-1.5-pro (More powerful, slower, FREE)
        - gemini-1.0-pro (Older version, FREE)

    FREE Tier Limits:
        - 15 requests per minute
        - 1,500 requests per day
        - 1 million tokens per day

    Examples:
        # With API key from environment
        summary = summarize_article_with_gemini("Long article text here...")

        # With explicit API key
        summary = summarize_article_with_gemini("Article...", api_key="AIza...")

        # With different model
        summary = summarize_article_with_gemini("Article...", model="gemini-1.5-pro")

    Setup:
        1. Get free API key: https://makersuite.google.com/app/apikey
        2. Install: pip install google-generativeai
        3. Set in .env: GEMINI_API_KEY=your_key_here
    """

    try:
        if not GEMINI_AVAILABLE:
            print("Error: google-generativeai not installed. Install with: pip install google-generativeai")
            return None

        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print("Error: GEMINI_API_KEY not found. Please set it as an environment variable or pass it as a parameter.")
            print("Get your free API key at: https://makersuite.google.com/app/apikey")
            return None

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Create the model
        gemini_model = genai.GenerativeModel(model)

        # Create the prompt for summarization
        prompt = f"""Please summarize the following article in a concise and clear manner. Focus on the main points and key information.

Article:
{article_text}

Summary:"""

        print(f"Sending request to Google Gemini API (Model: {model})...")

        # Generate the summary
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.5,
                top_p=0.9,
            )
        )

        # Extract the summary
        summary = response.text.strip()

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Google Gemini API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_with_gemini_custom(article_text, custom_instruction, api_key=None, model="gemini-1.5-flash", max_tokens=500):
    """
    Summarize an article with custom instructions using Google Gemini API.

    Args:
        article_text (str): The article text to summarize
        custom_instruction (str): Custom instructions for summarization
        api_key (str): Google Gemini API key (optional)
        model (str): Model name to use
        max_tokens (int): Maximum tokens for summary

    Returns:
        str: Summarized article text

    Examples:
        # 3 bullet points
        summary = summarize_with_gemini_custom(
            "Article text...",
            "Summarize in 3 bullet points"
        )

        # One sentence
        summary = summarize_with_gemini_custom(
            "Article text...",
            "Summarize in ONE sentence only"
        )
    """

    try:
        if not GEMINI_AVAILABLE:
            print("Error: google-generativeai not installed.")
            return None

        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            print("Error: GEMINI_API_KEY not found.")
            return None

        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Create the model
        gemini_model = genai.GenerativeModel(model)

        # Create the prompt with custom instructions
        prompt = f"""{custom_instruction}

Article:
{article_text}

Summary:"""

        print(f"Sending request to Google Gemini API with custom instructions (Model: {model})...")

        # Generate the summary
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.5,
                top_p=0.9,
            )
        )

        # Extract the summary
        summary = response.text.strip()

        print("Summary generated successfully!")
        return summary

    except Exception as e:
        print(f"Error calling Google Gemini API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def summarize_article_with_ollama(article_text, model="llama3.2", ollama_url="http://localhost:11434"):
    """
    Summarize an article using Ollama (100% FREE - Runs locally, unlimited!).

    Args:
        article_text (str): The article text to summarize
        model (str): Ollama model to use (default: "llama3.2")
        ollama_url (str): Ollama server URL (default: "http://localhost:11434")

    Returns:
        str: Summarized article text

    Available FREE Models (download with 'ollama pull <model>'):
        - llama3.2 (Recommended - Fast, good quality, 2GB)
        - llama3.1 (Larger, more powerful, 4.7GB)
        - mistral (Fast and efficient, 4.1GB)
        - gemma2 (Google's model, 5.4GB)
        - qwen2.5 (Good for summarization, 4.7GB)

    Examples:
        # Basic usage
        summary = summarize_article_with_ollama("Long article text here...")

        # With different model
        summary = summarize_article_with_ollama("Article...", model="mistral")

    Setup:
        1. Download Ollama: https://ollama.com/
        2. Install Ollama (runs automatically in background)
        3. Download model: ollama pull llama3.2
        4. That's it! No API key needed.
    """

    try:
        if not REQUESTS_AVAILABLE:
            print("Error: requests not installed. Install with: pip install requests")
            return None

        # Create the prompt for summarization
        prompt = f"""Please summarize the following article in a concise and clear manner. Focus on the main points and key information.

Article:
{article_text}

Summary:"""

        print(f"Sending request to Ollama (Model: {model})...")

        # Call the Ollama API
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "num_predict": 500  # Max tokens for summary
                }
            },
            timeout=120  # 2 minute timeout
        )

        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', '').strip()

            print("Summary generated successfully!")
            return summary

        else:
            print(f"Error: Ollama returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Make sure Ollama is running.")
        print("Download and install Ollama from: https://ollama.com/")
        print("Then download a model: ollama pull llama3.2")
        return None

    except Exception as e:
        print(f"Error calling Ollama API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def batch_summarize_articles(articles_dict, api_key=None, model="llama-3.3-70b-versatile"):
    """
    Summarize multiple articles in batch.

    Args:
        articles_dict (dict): Dictionary with article IDs as keys and article text as values
            Example: {"1": "Article 1 text...", "2": "Article 2 text..."}
        api_key (str): Groq API key (optional)
        model (str): Model name to use

    Returns:
        dict: Dictionary with article IDs as keys and summaries as values

    Examples:
        articles = {
            "1": "Long article 1...",
            "2": "Long article 2...",
            "3": "Long article 3..."
        }

        summaries = batch_summarize_articles(articles)
        # Returns: {"1": "Summary 1...", "2": "Summary 2...", "3": "Summary 3..."}
    """

    summaries = {}
    total = len(articles_dict)

    print(f"\n=== Batch Summarization Started ===")
    print(f"Total articles to summarize: {total}\n")

    for idx, (article_id, article_text) in enumerate(articles_dict.items(), 1):
        print(f"Processing article {idx}/{total} (ID: {article_id})...")

        summary = summarize_article_with_groq(article_text, api_key=api_key, model=model)

        if summary:
            summaries[article_id] = summary
            print(f"✓ Article {article_id} summarized successfully\n")
        else:
            summaries[article_id] = None
            print(f"✗ Failed to summarize article {article_id}\n")

    print(f"=== Batch Summarization Complete ===")
    print(f"Successfully summarized: {sum(1 for s in summaries.values() if s is not None)}/{total}")

    return summaries