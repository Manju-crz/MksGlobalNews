import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.filesystemUtil import JsonUtil
from util.llmUtil.scriptEditor import generate_news_script


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


def consolidate_grouped_articles(articles_group_file, input_file, output_file):
    """
    Consolidate grouped articles into a refined output.

    Args:
        articles_group_file (str): Path to the JSON file containing grouped articles
        input_file (str): Path to the input JSON file
        output_file (str): Path to save the consolidated output

    Returns:
        dict: Consolidated articles data
    """

    # Read the groups data from file
    groups = JsonUtil.read_json_content(articles_group_file)
    if not groups:
        print(f"Error reading groups file: {articles_group_file}")
        return {}

    # Read the original data
    data = JsonUtil.read_json_content(input_file)
    
    # Remove duplicate article IDs across groups
    article_groups = groups.get("groups", [])
    filtered_groups = []
    used_ids = set()

    for group in article_groups:
        # Remove IDs that are already used in previous groups
        filtered_group = [article_id for article_id in group if article_id not in used_ids]
        
        # Only keep the group if it still has articles after filtering
        if filtered_group:
            filtered_groups.append(filtered_group)
            # Mark these IDs as used for subsequent groups
            used_ids.update(filtered_group)
        else:
            print(f"Discarded group {group} - all articles were duplicates of previous groups")

    print(f"Filtered groups: {len(article_groups)} -> {len(filtered_groups)} groups")
    print(f"Filtered groups structure: {filtered_groups}")
    # filtered_groups structure: [["1", "4", "9"], ["2", "5"], ["7"]] where each inner list contains unique article IDs

    # Initialize refined_data as empty dictionary
    refined_data = {}

    # Loop through each filtered group to extract article content and sources
    for group_index, group in enumerate(filtered_groups, start=1):
        article_content_list = []
        sources_list = []

        for article_id in group:
            # Find the record in input data
            record = data.get(article_id)
            if record:
                # Get article content
                article_content = record.get('article_content', '')
                if article_content:
                    article_content_list.append(article_content)

                # Get source
                source = record.get('source', '')
                if source and source not in sources_list:
                    sources_list.append(source)

        # Create comma-separated sources string
        sources_string = ', '.join(sources_list) if sources_list else ''

        print(f"Group {group_index}: {group}")
        print(f"  Article count: {len(article_content_list)}")
        print(f"  Sources: {sources_string}")
        print(f"  Article contents preview: {[content[:50] + '...' if len(content) > 50 else content for content in article_content_list]}")

        # Generate consolidated news script if we have article content
        if article_content_list:
            print(f"  Generating consolidated script for group {group_index}...")
            try:
                consolidated_script = generate_news_script(article_texts=article_content_list)
                print(f"  Script generated successfully for group {group_index}")

                # Get the first article ID from the group as the representative
                first_article_id = group[0]

                # Get the original record for the first article
                original_record = data.get(first_article_id)

                if original_record:
                    # Create a new record with consolidated content
                    new_record = original_record.copy()
                    new_record['article_content'] = consolidated_script
                    new_record['source'] = sources_string

                    # Store in refined_data using the first article ID
                    refined_data[first_article_id] = new_record
                    print(f"  Stored consolidated record for article {first_article_id}")

            except Exception as e:
                print(f"  Error generating script for group {group_index}: {str(e)}")
                # Fallback: use the first article as-is
                first_article_id = group[0]
                original_record = data.get(first_article_id)
                if original_record:
                    new_record = original_record.copy()
                    new_record['source'] = sources_string
                    refined_data[first_article_id] = new_record
        else:
            print(f"  No article content found for group {group_index}, skipping...")

    # Add ungrouped articles (articles that don't appear in any group)
    all_grouped_ids = set()
    for group in filtered_groups:
        all_grouped_ids.update(group)

    for article_id, record in data.items():
        if article_id not in all_grouped_ids:
            refined_data[article_id] = record
            print(f"Added ungrouped article {article_id}")

    print(f"Total articles in refined data: {len(refined_data)}")

    # Save to output file
    saved = JsonUtil.replace_json_content(output_file, refined_data)

    if saved:
        print(f"Consolidated data saved to: {output_file}")
        return refined_data

    print(f"Failed to save consolidated data to: {output_file}")
    return refined_data

