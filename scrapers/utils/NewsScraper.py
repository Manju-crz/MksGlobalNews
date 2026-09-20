import sys
import os

# Add parent directory to path to import from util packages
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finders import scrape_bbc, scrape_guardian, scrape_dw, scrape_cbc, scrape_apnews
from util.filesystemUtil.file_utils import FileUtils
from util.dateTimeUtil.date_time_util import DateTimeUtil
import time


class NewsScraper:

    def __init__(self, headless=False):
        self.headless = headless
        self.all_news_data = {}

    def scrape_all(self):
        """Scrape all news websites and return combined dictionary"""
        print("\n" + "="*80)
        print("STARTING NEWS SCRAPING FROM ALL SOURCES")
        print("="*80)

        start_time = time.time()

        # Call the finder functions directly
        print("\n" + "="*80)
        print("SCRAPING BBC NEWS")
        print("="*80)
        bbc_data = scrape_bbc(headless=self.headless)

        print("\n" + "="*80)
        print("SCRAPING THE GUARDIAN")
        print("="*80)
        guardian_data = scrape_guardian(headless=self.headless)

        print("\n" + "="*80)
        print("SCRAPING DW NEWS")
        print("="*80)
        dw_data = scrape_dw(headless=self.headless)

        print("\n" + "="*80)
        print("SCRAPING CBC NEWS")
        print("="*80)
        cbc_data = scrape_cbc(headless=self.headless)

        print("\n" + "="*80)
        print("SCRAPING AP NEWS")
        print("="*80)
        #apnews_data = scrape_apnews(headless=self.headless)

        # Combine all data
        self.all_news_data = {
            'bbc': bbc_data,
            'guardian': guardian_data,
            'dw': dw_data,
            'cbc': cbc_data,
            #'apnews': apnews_data
        }

        # Calculate statistics
        total_articles = sum(
            len(source_data) for source_data in self.all_news_data.values()
        )
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "="*80)
        print("SCRAPING COMPLETED")
        print("="*80)
        print(f"Total articles collected: {total_articles}")
        return self.all_news_data

    def save_to_json(self, filename='news_data.json'):
        """Save scraped data to JSON file in dumps folder using FileUtils"""
        try:
            # Get the project root directory (go up two levels from utils folder)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            dumps_folder = os.path.join(project_root, 'dumps')

            # Full path to the JSON file
            filepath = os.path.join(dumps_folder, filename)

            # Use FileUtils to create the file (it will auto-create the dumps folder)
            FileUtils.create_file(filepath, self.all_news_data)

        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")

    def get_data(self):
        """Return the scraped data dictionary"""
        return self.all_news_data

    def run_scraper_and_save(self, filename):
        """
        Reusable function to run the scraper and save results.
        This can be called from other Python files.

        Args:
            filename (str): Name of the JSON file to save the scraped data

        Returns:
            tuple: (news_data, filename) where:
                - news_data (dict): Scraped news data from all sources
                - filename (str): Full path to the saved JSON file

        Examples:
            # From another Python file:
            from scrapers.NewsScraper import NewsScraper

            # Run scraper and save
            scraper = NewsScraper(headless=True)
            data, filename = scraper.run_scraper_and_save("news_data.json")
        """
        # Scrape all news sources
        all_news = self.scrape_all()
        # Save to JSON file with the provided filename
        self.save_to_json(filename)

        # Store the full path for return
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        dumps_folder = os.path.join(project_root, 'dumps')
        saved_filename = os.path.join(dumps_folder, filename)

        # Print sample data
        print("\n" + "="*80)
        print("SAMPLE DATA")
        print("="*80)
        for source, articles in all_news.items():
            print(f"\n{source.upper()}:")
            for card_key, card_data in list(articles.items())[:2]:  # Show first 2 articles from each source
                print(f"  {card_key}:")
                print(f"    Headline: {card_data.get('headline', 'N/A')[:80]}...")
                print(f"    Paragraphs: {card_data.get('paragraph_count', 0)}")

        return all_news


def run_news_scraper(headless=False, filename=None):
    """
    Standalone reusable function to run the news scraper.
    Can be called from any Python file without creating a class instance.

    Args:
        headless (bool): Run browser in headless mode (default: False)

    Returns:
        tuple: (news_data, filename) where:
            - news_data (dict): Scraped news data from all sources
            - filename (str): Full path to generated JSON file

    Examples:
        # From another Python file:
        from scrapers.NewsScraper import run_news_scraper

        # Run scraper with visible browser
        data, filename = run_news_scraper(headless=False)
        print(f"Data saved to: {filename}")

        # Run scraper in background (headless mode)
        data, filename = run_news_scraper(headless=True)
    """
    # Generate timestamped filename using DateTimeUtil
    scraper = NewsScraper(headless=headless)
    return scraper.run_scraper_and_save(filename)


def main():
    """Main function to run the news scraper when executed directly"""
    # Use the reusable function
    run_news_scraper(headless=False)


if __name__ == "__main__":
    main()