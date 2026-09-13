import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filesystemUtil import JsonUtil, FileUtils
from llmUtil import calculate_similarity


def transform_news_data(input_json_file, output_json_file=None):
    """
    Transform news data from source-grouped format to flat numbered format.

    Converts from:
    {
        "bbc": {
            "bbc_card_1": {"headline": "...", "description": "...", "article_content": "...", ...},
            "bbc_card_2": {...}
        },
        "guardian": {...}
    }

    To:
    {
        "1": {"headline": "...", "article_content": "...", "source": "bbc"},
        "2": {"headline": "...", "article_content": "...", "source": "bbc"},
        "3": {"headline": "...", "article_content": "...", "source": "guardian"}
    }

    Args:
        input_json_file (str): Path to the input JSON file
        output_json_file (str): Path to save the transformed JSON (optional)
                               If None, overwrites the input file

    Returns:
        dict: Transformed news data

    Examples:
        # Transform and save to new file
        transformed = transform_news_data('dumps/2026_08_14_00_56.json', 'dumps/transformed.json')

        # Transform and overwrite original file
        transformed = transform_news_data('dumps/2026_08_14_00_56.json')
    """
    try:
        # Read the original JSON file
        print(f"Reading JSON file: {input_json_file}")
        original_data = JsonUtil.read_json_content(input_json_file)

        if not original_data:
            print("Failed to read JSON file or file is empty")
            return None

        # Transform the data
        transformed_data = {}
        counter = 1

        # Iterate through each source (bbc, guardian, dw, cbc, apnews)
        for source_name, articles in original_data.items():
            print(f"Processing {source_name}: {len(articles)} articles")

            # Iterate through each article in the source
            for article_key, article_data in articles.items():
                # Extract only headline and article_content
                transformed_article = {
                    "headline": article_data.get("headline", ""),
                    "article_content": article_data.get("article_content", ""),
                    "source": source_name
                }

                # Add to transformed data with numerical key
                transformed_data[str(counter)] = transformed_article
                counter += 1

        print(f"\nTransformation complete!")
        print(f"Total articles: {counter - 1}")

        # Save the transformed data
        if output_json_file is None:
            output_json_file = input_json_file

        print(f"Saving transformed data to: {output_json_file}")

        # Use FileUtils to create/update the file (creates file if it doesn't exist)
        FileUtils.create_file(output_json_file, transformed_data)

        return transformed_data

    except Exception as e:
        print(f"Error transforming news data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_article_by_number(json_file, article_number):
    """
    Get a specific article by its number from the transformed JSON.

    Args:
        json_file (str): Path to the transformed JSON file
        article_number (int or str): Article number to retrieve

    Returns:
        dict: Article data or None if not found

    Examples:
        # Get article number 1
        article = get_article_by_number('dumps/transformed.json', 1)
        print(article['headline'])
    """
    try:
        data = JsonUtil.read_json_content(json_file)

        if not data:
            return None

        article = data.get(str(article_number))

        if article:
            print(f"Article {article_number} found from source: {article.get('source')}")
            return article
        else:
            print(f"Article {article_number} not found")
            return None

    except Exception as e:
        print(f"Error getting article: {str(e)}")
        return None


def get_articles_by_source(json_file, source_name):
    """
    Get all articles from a specific source.

    Args:
        json_file (str): Path to the transformed JSON file
        source_name (str): Source name (e.g., 'bbc', 'guardian', 'dw', 'cbc', 'apnews')

    Returns:
        dict: Dictionary of articles from the specified source

    Examples:
        # Get all BBC articles
        bbc_articles = get_articles_by_source('dumps/transformed.json', 'bbc')
    """
    try:
        data = JsonUtil.read_json_content(json_file)

        if not data:
            return {}

        # Filter articles by source
        filtered_articles = {
            key: article for key, article in data.items()
            if article.get('source') == source_name
        }

        print(f"Found {len(filtered_articles)} articles from {source_name}")
        return filtered_articles

    except Exception as e:
        print(f"Error filtering articles: {str(e)}")
        return {}


def count_articles_by_source(json_file):
    """
    Count articles grouped by source.

    Args:
        json_file (str): Path to the transformed JSON file

    Returns:
        dict: Dictionary with source names as keys and article counts as values

    Examples:
        # Get article counts
        counts = count_articles_by_source('dumps/transformed.json')
        # Returns: {'bbc': 5, 'guardian': 6, 'dw': 4, 'cbc': 5, 'apnews': 5}
    """
    try:
        data = JsonUtil.read_json_content(json_file)

        if not data:
            return {}

        # Count articles by source
        counts = {}
        for article in data.values():
            source = article.get('source', 'unknown')
            counts[source] = counts.get(source, 0) + 1

        print("Article counts by source:")
        for source, count in counts.items():
            print(f"  {source}: {count} articles")

        return counts

    except Exception as e:
        print(f"Error counting articles: {str(e)}")
        return {}


def summarize_all_articles(json_file_path, model="llama3.2"):
    """
    Summarize all articles in a transformed JSON file and add summaries as a new key.
    Uses Ollama (100% FREE - Runs locally, unlimited!).

    Args:
        json_file_path (str): Path to the transformed JSON file
        model (str): Ollama model to use for summarization
                     Default: "llama3.2"
                     Other options: "llama3.1", "mistral", "gemma2", "qwen2.5"

    Returns:
        dict: Updated JSON data with summaries or None if failed

    Examples:
        from scripter.summarizer import summarize_all_articles

        # Use default Llama model
        updated_data = summarize_all_articles('dumps/2026_08_14_01_22_transformed.json')

        # Use Mistral model
        updated_data = summarize_all_articles('dumps/2026_08_14_01_22_transformed.json',
                                              model='mistral')
    """
    try:
        print("\n=== Article Summarization Started ===\n")

        # Read the transformed JSON file
        print(f"Reading JSON file: {json_file_path}")
        data = JsonUtil.read_json_content(json_file_path)

        if not data:
            print("Failed to read JSON file or file is empty")
            return None

        total_articles = len(data)
        print(f"Total articles to summarize: {total_articles}\n")

        successful = 0
        failed = 0

        # Iterate through each article and summarize
        for article_id, article_data in data.items():
            print(f"Processing article {article_id}/{total_articles}...")
            print(f"  Headline: {article_data.get('headline', 'N/A')[:60]}...")

            article_content = article_data.get('article_content', '')

            if not article_content:
                print(f"  X No content found for article {article_id}\n")
                article_data['summary'] = None
                failed += 1
                continue

            # Summarize the article using Ollama
            summary = summarize_article_with_ollama(article_content, model=model)

            if summary:
                # Add summary to the article data
                article_data['summary'] = summary
                successful += 1
                print(f"  ✓ Article {article_id} summarized successfully")
                print(f"  Summary preview: {summary[:100]}...\n")
            else:
                article_data['summary'] = None
                failed += 1
                print(f"  X Failed to summarize article {article_id}\n")

        # Save the updated data back to the file
        print(f"Saving updated data with summaries to: {json_file_path}")
        FileUtils.create_file(json_file_path, data)

        print("\n=== Summarization Complete ===")
        print(f"Successfully summarized: {successful}/{total_articles}")
        print(f"Failed: {failed}/{total_articles}")
        print("="*80 + "\n")

        return data

    except Exception as e:
        print(f"Error summarizing articles: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def compare_all_articles(json_file, similarity_threshold=90.0):
    """
    Compare all articles in the JSON file for similarity.

    Args:
        json_file (str): Path to the JSON file containing articles
        similarity_threshold (float): Threshold for considering articles similar (default: 90.0)

    Returns:
        list: List of tuples (article1_id, article2_id, similarity_score) for pairs above threshold
    """
    try:
        # Read the JSON file
        data = JsonUtil.read_json_content(json_file)
        if not data:
            print(f"Error reading JSON file: {json_file}")
            return []

        # Compare all pairs
        article_ids = list(data.keys())
        similar_pairs = []

        print(f"Comparing {len(article_ids)} articles for similarity...")

        for i in range(len(article_ids)):
            for j in range(i + 1, len(article_ids)):
                id1 = article_ids[i]
                id2 = article_ids[j]

                article1 = data[id1]
                article2 = data[id2]

                # Get article content for comparison
                content1 = article1.get('article_content', article1.get('headline', ''))
                content2 = article2.get('article_content', article2.get('headline', ''))

                if content1 and content2:
                    similarity = calculate_similarity(content1, content2)

                    if similarity >= similarity_threshold:
                        similar_pairs.append((id1, id2, similarity))
                        print(f"Articles {id1} and {id2}: {similarity:.2f}% similar")

        return similar_pairs

    except Exception as e:
        print(f"Error comparing articles: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def process_and_transform_json(input_json_file, output_json_file, summarize=False):
    """
    Reusable function to process and transform a JSON file.
    Transforms the file and optionally summarizes all articles.

    Args:
        input_json_file (str): Path to the input JSON file
        output_json_file (str): Path to save the transformed JSON file
        summarize (bool): Whether to summarize articles after transformation (default: False)

    Returns:
        dict: Transformed news data or None if failed

    Examples:
        # From Driver.py or any other file:
        from scripter.summarizer import process_and_transform_json

        # Transform only
        transformed = process_and_transform_json('dumps/2026_08_14_01_22.json',
                                                 'dumps/2026_08_14_01_22_transformed.json')

        # Transform and summarize
        transformed = process_and_transform_json('dumps/2026_08_14_01_22.json',
                                                 'dumps/2026_08_14_01_22_transformed.json',
                                                 summarize=True)
    """
    try:
        print("=== News Data Transformer ===\n")

        # Transform the data
        transformed = transform_news_data(input_json_file, output_json_file)

        if transformed:
            print("\n--- Sample Transformed Data ---")
            # Show first 2 articles
            for i in range(1, min(3, len(transformed) + 1)):
                article = transformed.get(str(i))
                if article:
                    print(f"\nArticle {i}:")
                    print(f"  Source: {article['source']}")
                    print(f"  Headline: {article['headline'][:80]}...")
                    print(f"  Content length: {len(article['article_content'])} characters")

            # Count articles by source
            print("\n--- Article Statistics ---")
            counts = count_articles_by_source(output_json_file)

            print("\n=== Transformation Complete ===\n")

            # Summarize articles if requested
            if summarize:
                print("Summarization requested. Starting summarization process...\n")
                updated_data = summarize_all_articles(output_json_file)
                return updated_data

            return transformed
        else:
            print("\n=== Transformation Failed ===\n")
            return None

    except Exception as e:
        print(f"Error in process_and_transform_json: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# Example usage
if __name__ == "__main__":
    # Example: Transform a JSON file
    input_file = "dumps/2026_08_14_00_56.json"
    output_file = "dumps/2026_08_14_00_56_transformed.json"

    # Use the reusable function with summarization
    process_and_transform_json(input_file, output_file, summarize=False)