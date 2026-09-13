"""
Driver.py - Main entry point for the MksGlobalNews scraper application
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.utils.NewsScraper import run_news_scraper
from scripter.summarizer import process_and_transform_json
from scripter.similaritySegregator import compare_all_articles
from scripter.conciser import group_paired_articles, consolidate_grouped_articles


def main():
    """
    Main driver function to run the news scraper application
    """

    # Run the news scraper
    # headless=False: Shows browser (set to True to run in background)
    # save_file=True: Saves results to JSON file
    # show_sample=True: Displays sample data in console

    news_data, json_filename = run_news_scraper(
        headless=False,     # Change to True for headless mode
        save_file=True,     # Change to False to skip saving
        show_sample=True    # Change to False to skip sample output
    )

    # Extract just the filename (basename) from the full path
    file_name = os.path.basename(json_filename)

    print(f"\nGenerated file (full path): {json_filename}")
    print(f"File name only: {file_name}")

    # Transform and summarize the scraped data
    print("\n" + "="*80)
    print("Starting transformation and summarization...")
    print("="*80)

    # Create output filename for transformed data (ensure it's in project root dumps folder)
    project_root = os.path.dirname(os.path.abspath(__file__))
    dumps_folder = os.path.join(project_root, 'dumps')
    base_filename = os.path.basename(json_filename)
    output_file = os.path.join(dumps_folder, base_filename.replace('.json', '_transformed.json'))

    # Process and transform the JSON with summarization enabled
    process_and_transform_json(
        input_json_file=json_filename,
        output_json_file=output_file,
        summarize=False  # Set to True to enable summarization
    )

    # Step 3: Compare articles for similarity and update pairedwith relationships
    print("\n" + "="*80)
    print("Starting article similarity analysis...")
    print("="*80)

    comparison_results = compare_all_articles(json_file=output_file, similarity_threshold=90.0)

    if comparison_results:
        print(f"\n✅ Successfully compared {len(comparison_results)} article pairs!")
    else:
        print("\n⚠️ No similarity comparisons were made.")

    # Step 4: Group, consolidate and refine articles
    print("\n" + "="*80)
    print("Starting article grouping, consolidation and refinement...")
    print("="*80)

    # Group articles based on similarity (90% threshold)
    groups = group_paired_articles(json_file=output_file, similarity_threshold=90.0)

    # Consolidate and refine all grouped articles
    refined_output = os.path.join(dumps_folder, base_filename.replace('.json', '_refined.json'))
    refined_articles = consolidate_grouped_articles(groups=groups, input_file=output_file, output_file=refined_output)

    print("\n" + "="*80)
    print("All processing complete!")
    print(f"📄 Original file: {json_filename}")
    print(f"🔄 Transformed file: {output_file}")
    print(f"✨ Refined file: {refined_output}")
    print("="*80)


if __name__ == "__main__":
    main()