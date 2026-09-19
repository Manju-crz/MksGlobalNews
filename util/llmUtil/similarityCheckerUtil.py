"""
Similarity Checker Utility
Uses sentence-transformers (all-mpnet-base-v2) to calculate similarity between articles
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sentence Transformers imports
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")


# Global model instance (loaded once for efficiency)
_model = None


def _load_model():
    """
    Load the sentence transformer model (lazy loading).
    Model is loaded only once and reused for all comparisons.
    """

    global _model

    if _model is None:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers package is not installed. Install with: pip install sentence-transformers")

        print("Loading similarity model (all-mpnet-base-v2)... This may take a moment on first run.")
        _model = SentenceTransformer('all-mpnet-base-v2')
        print("Model loaded successfully!")

    return _model


def calculate_similarity(article1, article2):
    """
    Calculate similarity percentage between two articles.

    Args:
        article1 (str): First article text
        article2 (str): Second article text

    Returns:
        float: Similarity percentage (0-100)
            - 90-100%: Nearly identical (duplicates)
            - 70-89%: Very similar (same story, different sources)
            - 50-69%: Related topics
            - 30-49%: Somewhat related
            - 0-29%: Different topics

    Examples:
        # Compare two articles
        similarity = calculate_similarity(
            "Trump announces new policy on immigration...",
            "President Trump unveils immigration policy..."
        )
        print(f"Similarity: {similarity:.2f}%")
        # Output: Similarity: 87.50%

        # Check if articles are duplicates
        if similarity > 90:
            print("Articles are duplicates")
        elif similarity > 70:
            print("Articles are very similar (same story)")
        else:
            print("Articles are different")

    Setup:
        1. Install: pip install sentence-transformers
        2. First run will download the model (~420MB)
        3. Model is cached locally for future use
    """

    try:
        # Validate inputs
        if not article1 or not article2:
            print("Error: Both articles must be non-empty strings")
            return 0.0

        if not isinstance(article1, str) or not isinstance(article2, str):
            print("Error: Both inputs must be strings")
            return 0.0

        # Load the model (lazy loading)
        model = _load_model()

        # Generate embeddings for both articles
        print("Calculating embeddings...")
        embedding1 = model.encode(article1, convert_to_tensor=True)
        embedding2 = model.encode(article2, convert_to_tensor=True)

        # Calculate cosine similarity
        cosine_score = util.cos_sim(embedding1, embedding2)

        # Convert to percentage (0-100)
        similarity_percentage = float(cosine_score[0][0]) * 100

        print(f"Similarity calculated: {similarity_percentage:.2f}%")

        return similarity_percentage

    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0.0


def compare_articles_batch(articles_dict):
    """
    Compare multiple articles and find similar pairs.

    Args:
        articles_dict (dict): Dictionary with article IDs as keys and article text as values
            Example: {"1": "Article 1 text...", "2": "Article 2 text..."}

    Returns:
        list: List of tuples (article_id1, article_id2, similarity_percentage)
            Sorted by similarity (highest first)

    Examples:
        articles = {
            "1": "Trump announces policy...",
            "2": "President Trump unveils...",
            "3": "Biden responds to...",
        }

        similar_pairs = compare_articles_batch(articles)

        for id1, id2, similarity in similar_pairs:
            if similarity > 70:
                print(f"Articles {id1} and {id2} are {similarity:.2f}% similar")
    """

    try:
        if not articles_dict or len(articles_dict) < 2:
            print("Error: Need at least 2 articles to compare")
            return []

        # Load the model
        model = _load_model()

        # Get article IDs and texts
        article_ids = list(articles_dict.keys())
        article_texts = list(articles_dict.values())

        print(f"\nGenerating embeddings for {len(article_texts)} articles...")

        # Generate embeddings for all articles at once (more efficient)
        embeddings = model.encode(article_texts, convert_to_tensor=True, show_progress_bar=True)

        print("Calculating pairwise similarities...")

        # Calculate all pairwise similarities
        similarities = []

        for i in range(len(article_ids)):
            for j in range(i + 1, len(article_ids)):
                # Calculate cosine similarity
                cosine_score = util.cos_sim(embeddings[i], embeddings[j])
                similarity_percentage = float(cosine_score[0][0]) * 100

                similarities.append((article_ids[i], article_ids[j], similarity_percentage))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[2], reverse=True)

        print(f"Found {len(similarities)} article pairs")

        return similarities

    except Exception as e:
        print(f"Error in batch comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def find_duplicates(articles_dict, threshold=90.0):
    """
    Find duplicate or near-duplicate articles.

    Args:
        articles_dict (dict): Dictionary with article IDs as keys and article text as values
        threshold (float): Similarity threshold for duplicates (default: 90.0%)

    Returns:
        list: List of duplicate pairs [(id1, id2, similarity), ...]

    Examples:
        articles = {
            "1": "Trump announces policy...",
            "2": "President Trump announces policy...",  # Very similar to #1
            "3": "Biden responds to...",
        }

        duplicates = find_duplicates(articles, threshold=85.0)

        if duplicates:
            print(f"Found {len(duplicates)} duplicate pairs:")
            for id1, id2, similarity in duplicates:
                print(f"  Articles {id1} and {id2}: {similarity:.2f}% similar")
    """

    try:
        # Get all similarities
        all_similarities = compare_articles_batch(articles_dict)

        # Filter by threshold
        duplicates = [(id1, id2, sim) for id1, id2, sim in all_similarities if sim >= threshold]

        if duplicates:
            print(f"\nFound {len(duplicates)} duplicate pairs (threshold: {threshold}%):")
            for id1, id2, similarity in duplicates:
                print(f"  Articles {id1} and {id2}: {similarity:.2f}% similar")
        else:
            print(f"\nNo duplicates found (threshold: {threshold}%)")

        return duplicates

    except Exception as e:
        print(f"Error finding duplicates: {str(e)}")
        return []


def get_similarity_category(similarity_percentage):
    """
    Get a human-readable category for similarity percentage.

    Args:
        similarity_percentage (float): Similarity percentage (0-100)

    Returns:
        str: Category description

    Examples:
        category = get_similarity_category(87.5)
        print(category)  # Output: "Very Similar (same story, different sources)"
    """

    if similarity_percentage >= 90:
        return "Nearly Identical (duplicates)"
    elif similarity_percentage >= 70:
        return "Very Similar (same story, different sources)"
    elif similarity_percentage >= 50:
        return "Related Topics"
    elif similarity_percentage >= 30:
        return "Somewhat Related"
    else:
        return "Different Topics"