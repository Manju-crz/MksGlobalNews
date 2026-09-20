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
from util.youtubeUtil.upload_video import upload_single_video
from util.llmUtil.TitleThumbnailConstructor import generate_youtube_assets

# Shared project paths used by the pipeline methods.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DUMPS_FOLDER = os.path.join(PROJECT_ROOT, "dumps")

# Add the project root to the path
sys.path.insert(0, PROJECT_ROOT)

from scrapers.utils.NewsScraper import run_news_scraper
from scripter.summarizer import process_and_transform_json
from scripter.conciser import group_paired_articles, consolidate_grouped_articles
from util.dateTimeUtil.date_time_util import DateTimeUtil


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


def quality_check_transformed_file(transformed_file):
    """Remove articles that start with 'This blog is now closed.' from transformed.json"""
    print("\n" + "="*80)
    print("Quality check: Removing closed blog articles...")
    print("="*80)
    
    transformed_data = JsonUtil.read_json_content(transformed_file)
    if not transformed_data:
        print(f"No data found in transformed file: {transformed_file}")
        return
    
    original_count = len(transformed_data)
    records_to_remove = []
    
    for record_number, record in transformed_data.items():
        article_content = record.get("article_content", "")
        if article_content.strip().startswith("This blog is now closed."):
            records_to_remove.append(record_number)
            print(f"Found closed blog article - Record {record_number}: removing")
    
    # Remove the identified records
    for record_number in records_to_remove:
        del transformed_data[record_number]
    
    # Save the cleaned data back to the file
    JsonUtil.replace_json_content(transformed_file, transformed_data)
    
    removed_count = len(records_to_remove)
    print(f"Quality check completed: Removed {removed_count} closed blog articles out of {original_count} total articles")
    print(f"Remaining articles: {len(transformed_data)}")
    print("="*80)


def groupArticles(transformed_file, articles_groups_file):
    # groups Stores similarity clusters, not article records themselves. For example, {"groups": [["1","4","9"]]}
    # means article IDs 1, 4, and 9 were all considered duplicates/near-duplicates above the 80% similarity threshold,
    # and the code keeps track of them as a single grouped set.
    groups = group_paired_articles(json_file=transformed_file, similarity_threshold=80.0)
    print(f"Groupped data: {groups}")
    # Write groups data to articles_groups_file using JsonUtil
    JsonUtil.replace_json_content(articles_groups_file, groups)
    print(f"Groups data saved to: {articles_groups_file}")


def generate_images_for_articles(base_name, refined_file):
    """Generate images for all articles in the refined file."""
    refined_data = JsonUtil.read_json_content(refined_file)
    if not refined_data:
        print(f"No records found in refined file: {refined_file}")
        return

    # Delete existing files in generated_images folder
    generated_images_dir = os.path.join(DUMPS_FOLDER, "generated_images")
    if os.path.exists(generated_images_dir):
        print(f"Cleaning up existing images in: {generated_images_dir}")
        for filename in os.listdir(generated_images_dir):
            file_path = os.path.join(generated_images_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")

    for record_number, record in refined_data.items():
        article_text = record.get("article_content", "")
        if not article_text:
            print(f"Skipping record {record_number}: no article content found")
            continue
        output_name = f"{base_name}_{record_number}"
        print(f"\nGenerating image for article {record_number}...")
        image_path = generate_image_for_article(article_text, output_name)
        print(f"Image file: {image_path}")


def generate_audio_for_articles(base_name, refined_file):
    """Generate audio voiceovers for all articles in the refined file."""
    refined_data = JsonUtil.read_json_content(refined_file)
    if not refined_data:
        print(f"No records found in refined file: {refined_file}")
        return

    # Delete existing files in generated_audios folder
    generated_audios_dir = os.path.join(DUMPS_FOLDER, "generated_audios")
    if os.path.exists(generated_audios_dir):
        print(f"Cleaning up existing audio files in: {generated_audios_dir}")
        for filename in os.listdir(generated_audios_dir):
            file_path = os.path.join(generated_audios_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")

    for record_number, record in refined_data.items():
        article_text = record.get("article_content", "")
        if not article_text:
            print(f"Skipping record {record_number}: no article content found")
            continue
        output_name = f"{base_name}_{record_number}"
        print(f"\nGenerating audio for article {record_number}...")
        audio_path = generate_audio_for_article(article_text, output_name)
        print(f"Audio file: {audio_path}")


def groupAudioFilesDuration(base_filename, audios_group_file):
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
            f"Group{group_number}": audio_group
        })
    print(f"Grouped audio files: {grouped_audio_files}")
    # Save grouped audio files to JSON file
    JsonUtil.replace_json_content(audios_group_file, grouped_audio_files)
    return grouped_audio_files


def create_videos_for_audio_group(audio_group, refined_file):
    """Create one video for every audio filename in a grouped audio dictionary."""
    refined_data = JsonUtil.read_json_content(refined_file)
    if not refined_data:
        raise ValueError(f"No refined article data found in: {refined_file}")

    # Extract audio files from the audio_group dictionary
    # audio_group structure: {"Group1": {"audio1.mp3": "4.10", "audio2.mp3": "5.42"}}
    group_data = next(iter(audio_group.values()))
    audio_files = list(group_data.keys())
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


def get_video_merger_files(base_filename, generated_videos, audio_group):
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
    group_name = next(iter(audio_group))
    base_name = os.path.splitext(base_filename)[0]
    merger_video_filename = os.path.join(
        DUMPS_FOLDER,
        "generated_videos",
        f"{base_name}_{group_name}.mp4",
    )
    print(f"Ready to generate videos: {generated_videos}")
    print(f"merger_video_filename: {merger_video_filename}")
    return merger_video_filename, generated_videos



def upload_video(video_file, audio_files, transformed_file):
    # Extract record numbers from audio files and get headlines
    record_numbers = []
    headlines = []
    
    # audio_files structure: {"2026_09_20_01_32_1.mp3": "4.10", "2026_09_20_01_32_2.mp3": "5.42"}
    for audio_filename in audio_files.keys():
        # Extract record number from filename (format: <timestamp>_<record_number>.mp3)
        file_stem = os.path.splitext(audio_filename)[0]
        record_number = file_stem.rsplit("_", 1)[-1]
        if record_number.isdigit():
            record_numbers.append(record_number)
    
    # Read transformed file to get headlines for each record
    transformed_data = JsonUtil.read_json_content(transformed_file)
    if transformed_data:
        for record_number in record_numbers:
            record = transformed_data.get(record_number)
            if record and "headline" in record:
                headlines.append(record["headline"])
    
    print(f"Record numbers: {record_numbers}")
    print(f"Headlines: {headlines}")

    # Create thumbnail image path by replacing .mp4 with .png and generated_videos with generated_images
    thumbnailImage = os.path.splitext(video_file)[0] + ".png"
    thumbnailImage = thumbnailImage.replace("generated_videos", "generated_images")
    print(f"Thumbnail image path: {thumbnailImage}")
    # Generate YouTube assets (title and thumbnail) using headlines
    youtube_assets = generate_youtube_assets(headings=headlines, thumbnail_filepath=thumbnailImage)
    generated_title = youtube_assets.get("title")
    generated_thumbnail = youtube_assets.get("thumbnail_file")
    print(f"Generated title: {generated_title}")
    print(f"Generated thumbnail: {generated_thumbnail}")

    # Format headlines for description
    headlines_text = "\n".join([f"• {headline}" for headline in headlines])

    # Create description template
    MKS_GLOBAL_NEWS_DESCRIPTION_TEMPLATE = f"""
📰 **{generated_title}**

{headlines_text}

In this video, **MksGlobalNews** brings you the latest updates and important developments from around the world, explained in a clear and easy-to-understand format.

🔔 **Subscribe to MksGlobalNews** for regular updates on:
• World News
• India News
• Breaking News
• Technology & AI
• Business & Economy
• Science & Innovation
• Important Global Developments

👍 If you found this video informative, **Like, Share & Subscribe** to support the channel.

💬 **What do you think about this development?** Share your views in the comments.

━━━━━━━━━━━━━━━━━━━━

⚠️ **Disclaimer:**
This video is created for informational and educational purposes. Information presented is based on publicly available sources and may be updated as new developments emerge. Viewers are encouraged to verify important information through official and reliable sources.

Some visuals, narration, or other elements in this video may be created or enhanced using AI tools. AI-generated content is used for presentation and informational purposes and does not represent real events unless explicitly stated.

© MksGlobalNews. All rights reserved.

#MksGlobalNews #News #WorldNews #BreakingNews
"""

    # Upload a single video
    result = upload_single_video(
        video_file=video_file,
        title=generated_title,
        description=MKS_GLOBAL_NEWS_DESCRIPTION_TEMPLATE,
        tags=["news", "India News", "World News", "MksGlobalNews"],
        privacy_status="public",
        thumbnail_file=generated_thumbnail,
        add_to_playlist=True
    )
    print(f"Video uploaded: {result['url']}")



def accomplish_videos(base_filename, refined_file, transformed_file, audios_group_file):
    # Delete existing files in generated_videos folder
    generated_videos_dir = os.path.join(DUMPS_FOLDER, "generated_videos")
    if os.path.exists(generated_videos_dir):
        print(f"Cleaning up existing videos in: {generated_videos_dir}")
        for filename in os.listdir(generated_videos_dir):
            file_path = os.path.join(generated_videos_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")
    
    grouped_audio_files = JsonUtil.read_json_content(audios_group_file)
    for audio_group in grouped_audio_files:
        # Get the group name and audio files
        group_name = next(iter(audio_group.keys()))
        audio_files = next(iter(audio_group.values()))
        # audio_files structure: {"audio1.mp3": "4.10", "audio2.mp3": "5.42"} where keys are filenames and values are durations
        print(f"Group: {group_name}")
        print(f"Audio files: {audio_files}")

        # Generate videos for this audio group
        generated_videos = create_videos_for_audio_group(audio_group, refined_file=refined_file)

        # Merge videos for this group
        merger_video_filename, generated_videos = get_video_merger_files(base_filename, generated_videos, audio_group)
        merge_videos(generated_videos, merger_video_filename)
        print(f"✅ Group {group_name} video generated successfully: {merger_video_filename}")
        
        # Upload video to YouTube
        #upload_video(merger_video_filename, audio_files, transformed_file)


def main():
    timestamp = "2026_09_21_00_18"
    #timestamp = DateTimeUtil.get_timestamp_string()
    base_filename = f"{timestamp}.json"
    articles_groups_filename = f"{timestamp}_articles_groups.json"
    transformed_filename = f"{timestamp}_transformed.json"
    refined_filename = f"{timestamp}_refined.json"
    audios_group_filename = f"{timestamp}_audios_groups.json"
    json_filename = os.path.join(DUMPS_FOLDER, base_filename)
    transformed_file = os.path.join(DUMPS_FOLDER, transformed_filename)
    articles_groups_file = os.path.join(DUMPS_FOLDER, articles_groups_filename)
    refined_file = os.path.join(DUMPS_FOLDER, refined_filename)
    audios_group_file = os.path.join(DUMPS_FOLDER, audios_group_filename)
    print(f'json_filename is : {json_filename}')
    print(f'transformed_file is : {transformed_file}')
    print(f'articles_groups_file is : {articles_groups_file}')
    print(f'refined_file is : {refined_file}')
    print(f'audios_group_file is : {audios_group_file}')

    # Step 1: Scrape news from multiple sources (BBC, Guardian, DW, CBC) and save to JSON
    #run_news_scraper(headless=False, filename=base_filename)
    # Step 2: Process and transform scraped articles using LLM summarization (creates transformed.json)
    #process_and_transform_json(input_json_file=json_filename, output_json_file=transformed_file)
    # Step 3: Quality check - remove articles that start with "This blog is now closed." from transformed.json
    #quality_check_transformed_file(transformed_file)
    # Step 4: Group similar articles based on content similarity (creates articles_groups.json)
    #groupArticles(transformed_file, articles_groups_file)
    # Step 5: Consolidate grouped articles to remove duplicates and refine content (creates refined.json)
    #consolidate_grouped_articles(articles_group_file=articles_groups_file, input_file=transformed_file, output_file=refined_file)
    # Step 6: Generate images for each refined article (creates image files)
    #generate_images_for_articles(timestamp, refined_file)
    # Step 7: Generate audio voiceovers for each refined article (creates audio files)
    #generate_audio_for_articles(timestamp, refined_file)
    # Step 8: Group audio files by duration (creates audios_group.json)
    grouped_audio_files = groupAudioFilesDuration(json_filename, audios_group_file)
    # Step 9: Create videos from audio/images, merge them, and upload to YouTube
    accomplish_videos(base_filename, refined_file, transformed_file, audios_group_file)




if __name__ == "__main__":
    main()


