import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.filesystemUtil import JsonUtil, FileUtils
from util.llmUtil.summarizerUtil import summarize_article_with_groq


# ============================================================
# CONFIGURATION
# ============================================================

# Groq model to use for summarization
GROQ_MODEL = "llama-3.3-70b-versatile"


# ============================================================
# TRANSFORM NEWS DATA
# ============================================================

def transform_news_data(input_json_file, output_json_file=None):
    """
    Transform news data from source-grouped format to flat numbered format.

    Converts from:

    {
        "bbc": {
            "bbc_card_1": {
                "headline": "...",
                "description": "...",
                "article_content": "...",
                ...
            }
        },
        "guardian": {
            ...
        }
    }

    To:

    {
        "1": {
            "headline": "...",
            "article_content": "...",
            "source": "bbc"
        },
        "2": {
            "headline": "...",
            "article_content": "...",
            "source": "guardian"
        }
    }

    Args:
        input_json_file (str): Path to input JSON file
        output_json_file (str): Path to output JSON file

    Returns:
        dict: Transformed news data
    """

    try:
        print(f"Reading JSON file: {input_json_file}")

        original_data = JsonUtil.read_json_content(input_json_file)

        if not original_data:
            print("Failed to read JSON file or file is empty.")
            return None

        transformed_data = {}
        counter = 1

        for source_name, articles in original_data.items():

            print(
                f"Processing source: {source_name} "
                f"({len(articles)} articles)"
            )

            for article_key, article_data in articles.items():

                transformed_article = {
                    "headline": article_data.get("headline", ""),
                    "article_content": article_data.get(
                        "article_content", ""
                    ),
                    "source": source_name
                }

                transformed_data[str(counter)] = transformed_article

                counter += 1

        print("\nTransformation complete!")
        print(f"Total articles: {counter - 1}")

        if output_json_file is None:
            output_json_file = input_json_file

        print(f"Saving transformed data to: {output_json_file}")

        FileUtils.create_file(
            output_json_file,
            transformed_data
        )

        return transformed_data

    except Exception as e:

        print(
            f"Error transforming news data: {str(e)}"
        )

        import traceback
        traceback.print_exc()

        return None


# ============================================================
# GET ARTICLE BY NUMBER
# ============================================================

def get_article_by_number(json_file, article_number):
    """
    Get a specific article by number.

    Args:
        json_file (str): Path to JSON file
        article_number (int or str): Article number

    Returns:
        dict: Article data or None
    """

    try:

        data = JsonUtil.read_json_content(json_file)

        if not data:
            return None

        article = data.get(str(article_number))

        if article:

            print(
                f"Article {article_number} found "
                f"from source: {article.get('source')}"
            )

            return article

        print(
            f"Article {article_number} not found."
        )

        return None

    except Exception as e:

        print(
            f"Error getting article: {str(e)}"
        )

        return None


# ============================================================
# GET ARTICLES BY SOURCE
# ============================================================

def get_articles_by_source(json_file, source_name):
    """
    Get all articles from a specific source.

    Args:
        json_file (str): Path to JSON file
        source_name (str): Source name

    Returns:
        dict: Articles belonging to source
    """

    try:

        data = JsonUtil.read_json_content(json_file)

        if not data:
            return {}

        filtered_articles = {
            key: article
            for key, article in data.items()
            if article.get("source") == source_name
        }

        print(
            f"Found {len(filtered_articles)} articles "
            f"from {source_name}"
        )

        return filtered_articles

    except Exception as e:

        print(
            f"Error filtering articles: {str(e)}"
        )

        return {}


# ============================================================
# COUNT ARTICLES BY SOURCE
# ============================================================

def count_articles_by_source(json_file):
    """
    Count articles grouped by source.

    Args:
        json_file (str): Path to JSON file

    Returns:
        dict: Source names and article counts
    """

    try:

        data = JsonUtil.read_json_content(json_file)

        if not data:
            return {}

        counts = {}

        for article in data.values():

            source = article.get(
                "source",
                "unknown"
            )

            counts[source] = counts.get(
                source,
                0
            ) + 1

        print("\nArticle counts by source:")

        for source, count in counts.items():

            print(
                f"  {source}: {count} articles"
            )

        return counts

    except Exception as e:

        print(
            f"Error counting articles: {str(e)}"
        )

        return {}


# ============================================================
# SUMMARIZE ALL ARTICLES USING GROQ
# ============================================================

def summarize_all_articles(
    json_file_path,
    model=GROQ_MODEL,
    api_key=None
):
    """
    Summarize all articles using Groq.

    The generated summary is added to each article
    under the "summary" key.

    Args:
        json_file_path (str):
            Path to transformed JSON file.

        model (str):
            Groq model to use.

        api_key (str):
            Optional Groq API key.
            If not provided, summarizeUtil.py will
            read GROQ_API_KEY from environment.

    Returns:
        dict: Updated JSON data
    """

    try:

        print("\n" + "=" * 80)
        print("ARTICLE SUMMARIZATION STARTED")
        print("=" * 80)

        print(
            f"\nGroq Model: {model}"
        )

        # ----------------------------------------------------
        # Read JSON
        # ----------------------------------------------------

        print(
            f"\nReading JSON file: {json_file_path}"
        )

        data = JsonUtil.read_json_content(
            json_file_path
        )

        if not data:

            print(
                "Failed to read JSON file "
                "or file is empty."
            )

            return None

        total_articles = len(data)

        print(
            f"Total articles to summarize: "
            f"{total_articles}\n"
        )

        successful = 0
        failed = 0

        # ----------------------------------------------------
        # Process every article
        # ----------------------------------------------------

        for article_id, article_data in data.items():

            print("-" * 80)

            print(
                f"Processing article "
                f"{article_id}/{total_articles}"
            )

            headline = article_data.get(
                "headline",
                "N/A"
            )

            print(
                f"Headline: {headline[:100]}"
            )

            article_content = article_data.get(
                "article_content",
                ""
            )

            # ------------------------------------------------
            # Validate content
            # ------------------------------------------------

            if not article_content:

                print(
                    f"No article content found "
                    f"for article {article_id}"
                )

                article_data["summary"] = None

                failed += 1

                continue

            print(
                f"Article content length: "
                f"{len(article_content)} characters"
            )

            # ------------------------------------------------
            # Call Groq
            # ------------------------------------------------

            print(
                f"Sending article {article_id} "
                f"to Groq..."
            )

            summary = summarize_article_with_groq(
                article_content,
                api_key=api_key,
                model=model
            )

            # ------------------------------------------------
            # Handle response
            # ------------------------------------------------

            if summary:

                article_data["summary"] = summary

                successful += 1

                print(
                    f"Article {article_id} "
                    f"summarized successfully."
                )

                print(
                    f"Summary preview: "
                    f"{summary[:200]}..."
                )

            else:

                article_data["summary"] = None

                failed += 1

                print(
                    f"Failed to summarize "
                    f"article {article_id}"
                )

        # ----------------------------------------------------
        # Save updated JSON
        # ----------------------------------------------------

        print("\n" + "=" * 80)

        print(
            f"Saving updated data to: "
            f"{json_file_path}"
        )

        FileUtils.create_file(
            json_file_path,
            data
        )

        # ----------------------------------------------------
        # Final statistics
        # ----------------------------------------------------

        print("\n" + "=" * 80)
        print("SUMMARIZATION COMPLETE")
        print("=" * 80)

        print(
            f"Successfully summarized: "
            f"{successful}/{total_articles}"
        )

        print(
            f"Failed: "
            f"{failed}/{total_articles}"
        )

        print(
            f"Groq Model Used: {model}"
        )

        print("=" * 80 + "\n")

        return data

    except Exception as e:

        print(
            f"Error summarizing articles: "
            f"{str(e)}"
        )

        import traceback
        traceback.print_exc()

        return None


# ============================================================
# PROCESS + TRANSFORM + SUMMARIZE
# ============================================================

def process_and_transform_json(
    input_json_file,
    output_json_file,
    model=GROQ_MODEL,
    api_key=None
):
    """
    Transform a JSON file and summarize all articles
    using Groq.

    Args:
        input_json_file (str):
            Original JSON file.

        output_json_file (str):
            Transformed JSON file.

        model (str):
            Groq model to use.

        api_key (str):
            Optional Groq API key.

    Returns:
        dict: Processed news data
    """

    try:

        print("\n" + "=" * 80)
        print("NEWS DATA PROCESSOR")
        print("=" * 80)

        # ----------------------------------------------------
        # Transform
        # ----------------------------------------------------

        transformed = transform_news_data(
            input_json_file,
            output_json_file
        )

        if not transformed:

            print(
                "\nTransformation failed."
            )

            return None

        # ----------------------------------------------------
        # Show sample data
        # ----------------------------------------------------

        print(
            "\n--- Sample Transformed Data ---"
        )

        for i in range(
            1,
            min(3, len(transformed) + 1)
        ):

            article = transformed.get(
                str(i)
            )

            if article:

                print(
                    f"\nArticle {i}:"
                )

                print(
                    f"  Source: "
                    f"{article['source']}"
                )

                print(
                    f"  Headline: "
                    f"{article['headline'][:80]}..."
                )

                print(
                    f"  Content length: "
                    f"{len(article['article_content'])} "
                    f"characters"
                )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        print(
            "\n--- Article Statistics ---"
        )

        count_articles_by_source(
            output_json_file
        )

        print(
            "\n=== Transformation Complete ===\n"
        )

        # ----------------------------------------------------
        # Summarization
        # ----------------------------------------------------

        print(
            "Summarization enabled."
        )

        print(
            f"Using Groq model: {model}\n"
        )

        return summarize_all_articles(
            output_json_file,
            model=model,
            api_key=api_key
        )

    except Exception as e:

        print(
            f"Error in process_and_transform_json: "
            f"{str(e)}"
        )

        import traceback
        traceback.print_exc()

        return None


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Input / Output files
    # --------------------------------------------------------

    input_file = (
        "dumps/2026_09_19_13_32.json"
    )

    output_file = (
        "dumps/2026_09_19_13_32_transformed_1.json"
    )

    # --------------------------------------------------------
    # Process + Summarize
    # --------------------------------------------------------

    process_and_transform_json(
        input_json_file=input_file,
        output_json_file=output_file,
        # Explicitly select Groq model
        model="qwen/qwen3.8-27b"
    )