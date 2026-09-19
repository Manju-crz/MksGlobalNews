import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.filesystemUtil import JsonUtil


def group_paired_articles(json_file, similarity_threshold=80.0):
    """
    Group articles based on similarity threshold.

    Args:
        json_file (str): Path to the JSON file containing articles
        similarity_threshold (float): Threshold for considering articles similar (default: 90.0)

    Returns:
        dict: Dictionary of groups where each group contains similar articles
    """
    try:
        # Read the JSON file
        data = JsonUtil.read_json_content(json_file)
        if not data:
            print(f"Error reading JSON file: {json_file}")
            return {}

        # Group articles by similarity
        from util.llmUtil import calculate_similarity

        article_ids = list(data.keys())
        groups = []
        used_ids = set()

        print(f"Grouping {len(article_ids)} articles based on {similarity_threshold}% similarity threshold...")

        for i in range(len(article_ids)):
            if article_ids[i] in used_ids:
                continue

            current_group = [article_ids[i]]
            used_ids.add(article_ids[i])

            for j in range(i + 1, len(article_ids)):
                if article_ids[j] in used_ids:
                    continue

                article1 = data[article_ids[i]]
                article2 = data[article_ids[j]]

                content1 = article1.get('article_content', article1.get('headline', ''))
                content2 = article2.get('article_content', article2.get('headline', ''))

                if content1 and content2:
                    similarity = calculate_similarity(content1, content2)

                    if similarity >= similarity_threshold:
                        current_group.append(article_ids[j])
                        used_ids.add(article_ids[j])

            if len(current_group) > 1:
                groups.append(current_group)
                print(f"Group {len(groups)}: {len(current_group)} similar articles")

        return {"groups": groups}

    except Exception as e:
        print(f"Error grouping articles: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}


def consolidate_grouped_articles(groups, input_file, output_file):
    """
    Consolidate grouped articles into a refined output.

    Args:
        groups (dict): Dictionary containing grouped articles
        input_file (str): Path to the input JSON file
        output_file (str): Path to save the consolidated output

    Returns:
        dict: Consolidated articles data
    """
    try:
        # Read the original data
        data = JsonUtil.read_json_content(input_file)
        if not data:
            print(f"Error reading input file: {input_file}")
            return {}

        #TODO: Implement actual consolidation logic based on groups
        # For now, just copy the data to the output file
        # In a full implementation, this would merge similar articles
        
        refined_data = data

        # Save to output file
        saved = JsonUtil.replace_json_content(output_file, refined_data)

        if saved:
            print(f"Consolidated data saved to: {output_file}")
            return refined_data

        print(f"Failed to save consolidated data to: {output_file}")
        return {}

    except Exception as e:
        print(f"Error consolidating articles: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}
