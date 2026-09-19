"""
Driver.py - Main entry point for the MksGlobalNews scraper application
"""

import sys
import os
from util.filesystemUtil import JsonUtil
from mediaGen.audioGenerator import generate_audio_for_article
from mediaGen.picsGenerator import generate_image_for_article
from mediaGen.videoGenerator import create_video
from mediaGen.videosMerger import merge_videos
from driverutil.audiofilesDurationUtil import (
    format_duration,
    get_audio_durations,
    group_audio_files_by_duration,
    resolve_ungrouped_audio_files,
)
from util.youtubeUtil.upload_video import upload_video

# Shared project paths used by the pipeline methods.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DUMPS_FOLDER = os.path.join(PROJECT_ROOT, "dumps")

# Add the project root to the path
sys.path.insert(0, PROJECT_ROOT)

from scrapers.utils.NewsScraper import run_news_scraper
from scripter.summarizer import process_and_transform_json
from scripter.conciser import group_paired_articles, consolidate_grouped_articles


def run_scraping_step():
    """
    Run the scraper and return the generated raw JSON path.
    """
    # Run the news scraper
    # headless=False: Shows browser (set to True to run in background)
    # save_file=True: Saves results to JSON file
    # show_sample=True: Displays sample data in console
    news_data, json_filename = run_news_scraper(
        headless=False,
        save_file=True,
        show_sample=True,
    )
    base_file_name = os.path.basename(json_filename) if json_filename else None
    print(f"\nGenerated file (full path): {json_filename}")
    print(f"File name only: {base_file_name}")
    return news_data, base_file_name, json_filename


def group_Articles(output_file, base_filename):
    # Step 4: Group, consolidate and refine articles
    print("\n" + "="*80)
    print("Starting article grouping, consolidation and refinement...")
    print("="*80)
    # groups Stores similarity clusters, not article records themselves. For example, {"groups": [["1","4","9"]]}
    # means article IDs 1, 4, and 9 were all considered duplicates/near-duplicates above the 80% similarity threshold,
    # and the code keeps track of them as a single grouped set.
    groups = group_paired_articles(json_file=output_file, similarity_threshold=80.0)
    # Consolidate and refine all grouped articles
    refined_output = os.path.join(DUMPS_FOLDER, base_filename.replace('.json', '_refined.json'))
    refined_articles = consolidate_grouped_articles(groups=groups, input_file=output_file, output_file=refined_output)
    return refined_output


def collectArticles():
    """
    Main driver function to run the news scraper application
    """
    news_data, base_filename, json_filename = run_scraping_step()

    # Create output filename in the project dumps folder.
    base_filename = os.path.basename(json_filename)
    output_file = os.path.join(DUMPS_FOLDER, base_filename.replace('.json', '_transformed.json'))
    # Process and transform the JSON with summarization enabled
    process_and_transform_json(
        input_json_file=json_filename,
        output_json_file=output_file
    )
    
    # groups Stores similarity clusters, not article records themselves. For example, {"groups": [["1","4","9"]]}
    # means article IDs 1, 4, and 9 were all considered duplicates/near-duplicates above the 80% similarity threshold,
    # and the code keeps track of them as a single grouped set.
    groups = group_paired_articles(json_file=output_file, similarity_threshold=80.0)
    print(f"Groupped data: {groups}")
    
    # Consolidate and refine all grouped articles
    refined_file = os.path.join(DUMPS_FOLDER, base_filename.replace('.json', '_refined.json'))
    refined_articles = consolidate_grouped_articles(groups=groups, input_file=output_file, output_file=refined_file)
    
    print("\n" + "="*80)
    print("All processing complete!")
    print(f"📄 Original file: {json_filename}")
    print(f"🔄 Transformed file: {output_file}")
    print(f"✨ Refined file: {refined_file}")
    print("="*80)
    return base_filename, refined_file, groups


def generate_media_for_articles(base_filename, refined_file):
    refined_data = JsonUtil.read_json_content(refined_file)
    if not refined_data:
        print(f"No records found in refined file: {refined_file}")
        return
    base_name = os.path.splitext(base_filename)[0]
    for record_number, record in refined_data.items():
        article_text = record.get("article_content", "")
        if not article_text:
            print(f"Skipping record {record_number}: no article content found")
            continue

        output_name = f"{base_name}_{record_number}"
        print(f"\nGenerating media for article {record_number}...")
        image_path = generate_image_for_article(article_text, output_name)
        audio_path = generate_audio_for_article(article_text, output_name)
        print(f"Image file: {image_path}")
        print(f"Audio file: {audio_path}")


def groupAudioFilesDuration(base_filename):
    audio_durations = get_audio_durations(base_filename)
    print(f"Audio durations: {audio_durations}")

    audio_groups, ungrouped_files = group_audio_files_by_duration(audio_durations)
    audio_groups = resolve_ungrouped_audio_files(audio_groups, ungrouped_files)
    grouped_audio_files = []
    for group_number, (audio_group, total_duration) in enumerate(audio_groups, start=1):
        print(
            f"Group {group_number} "
            f"(total: {format_duration(total_duration)}): {audio_group}"
        )
        grouped_audio_files.append({
            f"Group{group_number}": list(audio_group.keys())
        })

    print(f"Grouped audio files: {grouped_audio_files}")
    return grouped_audio_files


def create_videos_for_audio_group(audio_group, refined_file):
    """Create one video for every audio filename in a grouped audio dictionary."""
    refined_data = JsonUtil.read_json_content(refined_file)
    if not refined_data:
        raise ValueError(f"No refined article data found in: {refined_file}")

    audio_files = next(iter(audio_group.values()))
    generated_videos = []

    for audio_file in audio_files:
        file_stem = os.path.splitext(audio_file)[0]
        record_number = file_stem.rsplit("_", 1)[-1]
        if not record_number.isdigit():
            raise ValueError(f"Could not identify record number from: {audio_file}")

        record = refined_data.get(record_number)
        source = record.get("source") if record else None
        if not source:
            raise ValueError(
                f"No source found for record {record_number} in: {refined_file}"
            )

        image_file = f"{file_stem}.png"
        video_file = f"{file_stem}.mp4"
        generated_videos.append(
            create_video(
                images=image_file,
                audio=audio_file,
                text=f"source:{source}",
                output=video_file,
            )
        )

    return generated_videos


def get_video_merger_files(base_filename, generated_videos, first_audio_group):
    generated_video_count = len(generated_videos)
    if generated_video_count > 0:
        boundary_video_count = min(generated_video_count, 6)
        welcome_video_path = os.path.abspath(
            os.path.join(
                PROJECT_ROOT,
                "data",
                f"Welcome_{boundary_video_count}.mp4",
            )
        )
        wrap_up_video_path = os.path.abspath(
            os.path.join(
                PROJECT_ROOT,
                "data",
                f"WrapUp_{boundary_video_count}.mp4",
            )
        )
        generated_videos.insert(0, welcome_video_path)
        generated_videos.append(wrap_up_video_path)

    switch_over_path = os.path.abspath(
        os.path.join(PROJECT_ROOT, "data", "SwitchOver.mp4")
    )
    if len(generated_videos) > 1:
        generated_videos = [
            item
            for index, video_file in enumerate(generated_videos)
            for item in (
                [video_file]
                + ([switch_over_path] if index < len(generated_videos) - 1 else [])
            )
        ]
    group_name = next(iter(first_audio_group))
    base_name = os.path.splitext(base_filename)[0]
    merger_video_filename = os.path.join(
        DUMPS_FOLDER,
        "generated_videos",
        f"{base_name}_{group_name}.mp4",
    )
    print(f"Ready to generate videos: {generated_videos}")
    print(f"merger_video_filename: {merger_video_filename}")
    return merger_video_filename, generated_videos


def main():
    #base_filename = "2026_09_14_01_06.json"
    #refined_file = "C:\\DATA\\VS_Code_Notes\\MksGlobalNews\\dumps\\2026_09_14_01_06_refined.json"
    base_filename, refined_file, groups = collectArticles()
    generate_media_for_articles(base_filename, refined_file)
    grouped_audio_files = groupAudioFilesDuration(base_filename)
    # Stores one group as {"Group1": [audio_filename, ...]}.
    first_audio_group = grouped_audio_files[0]
    generated_videos = create_videos_for_audio_group(first_audio_group, refined_file=refined_file)
    merger_video_filename, generated_videos = get_video_merger_files(base_filename, generated_videos, first_audio_group)
    merge_videos(generated_videos, merger_video_filename)
    #result = upload_video(
    #    video_file=merger_video_filename,
    #    title="My News Video",
    #    description="News video description",
    #    tags=["news", "India News", "World News", "MksGlobalNews"],
    #    category_id="25",
    #    privacy_status="public",
    #)






if __name__ == "__main__":
    main()


