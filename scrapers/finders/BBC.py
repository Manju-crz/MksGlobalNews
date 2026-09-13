import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.browser_utility import BrowserUtility
from utils.common_utils import CommonUtils
from pages.Page_BBC import BBCPage
import time


def scrape_bbc(headless=False):
    """Scrape BBC News and return data dictionary"""
    browser = BrowserUtility()

    try:
        print("Launching BBC website...")
        page = browser.launch_browser(url="https://www.bbc.com/", headless=headless)

        bbc_page = BBCPage(page)
        bbc_page.wait_for_page_load()

        # Scroll page to load dynamic content
        bbc_page.scroll_page_after_load()

        print("\n" + "="*80)
        print("Checking for privacy modal popup...")
        print("="*80)
        bbc_page.close_privacy_modal_if_visible()

        print("\n" + "="*80)
        print("Checking for survey popup...")
        print("="*80)
        bbc_page.close_survey_popup_if_visible()

        print("\nWaiting for a few seconds...")
        time.sleep(2)

        bbc_page.click_home_link()
        print("Waiting for a few seconds...")
        time.sleep(5)
        print("Getting current page title and URL...")
        bbc_page.get_page_title()
        bbc_page.get_current_url()
        print("\n" + "="*80)
        print("Fetching recent news cards (within 6 hours or in minutes)...")
        print("="*80 + "\n")
        recent_cards = bbc_page.get_recent_news_cards()

        news_cards = {}

        if recent_cards:
            print(f"\n{'='*80}")
            print(f"Extracting details from {len(recent_cards)} filtered cards...")
            print(f"{'='*80}\n")

            for index, card in enumerate(recent_cards, 1):
                details = bbc_page.get_card_details(card)
                # Only add cards with valid headlines (not None, not empty, not 'none')
                if details and details.get('headline') and details.get('headline').strip() and details.get('headline').lower() != 'none':
                    news_cards[f"bbc_card_{len(news_cards) + 1}"] = details
                else:
                    print(f"Skipping card {index}: Invalid or missing headline")

        if news_cards:
            print(f"\n{'='*80}")
            print(f"Clicking on each headline and reading article content...")
            print(f"{'='*80}\n")

            common_utils = CommonUtils(page)

            for card_key, card_details in news_cards.items():
                headline = card_details.get('headline')

                if headline:
                    print(f"\n{'='*80}")
                    print(f"Processing {card_key}: {headline}")
                    print(f"{'='*80}")

                    if common_utils.click_element_by_tag_and_text('h2', headline):
                        time.sleep(3)

                        article_content = bbc_page.read_article_paragraphs()

                        if article_content:
                            news_cards[card_key]['article_content'] = article_content['full_text']
                            news_cards[card_key]['paragraph_count'] = article_content['paragraph_count']
                            print(f"\nArticle content added to {card_key}")

                        page.go_back()
                        time.sleep(2)
                    else:
                        print(f"Failed to click on headline for {card_key}")

            # Filter out cards with 0 paragraph count
            print(f"\nFiltering out cards with 0 paragraph count...")
            filtered_news_cards = {
                key: value for key, value in news_cards.items()
                if value.get('paragraph_count', 0) > 0
            }

            removed_count = len(news_cards) - len(filtered_news_cards)
            if removed_count > 0:
                print(f"Removed {removed_count} card(s) with 0 paragraphs")

            print(f"\n{'='*80}")
            print(f"FINAL NEWS DATA DICTIONARY WITH ARTICLE CONTENT")
            print(f"{'='*80}\n")

            for card_key, card_details in filtered_news_cards.items():
                print(f"{card_key}: {{")
                print(f"    'headline': '{card_details.get('headline', 'N/A')}'")
                print(f"    'description': '{card_details.get('description', 'N/A')}'")
                print(f"    'time_updated': '{card_details.get('time_updated', 'N/A')}'")
                print(f"    'tag': '{card_details.get('tag', 'N/A')}'")
                print(f"    'paragraph_count': {card_details.get('paragraph_count', 0)}")

                article_preview = card_details.get('article_content', 'N/A')
                if article_preview != 'N/A' and len(article_preview) > 200:
                    article_preview = article_preview[:200] + "..."
                print(f"    'article_content': '{article_preview}'")
                print(f"}}\n")

            print(f"{'='*80}")
            print(f"Total cards in dictionary: {len(filtered_news_cards)}")
            print(f"{'='*80}")

            print("\nClosing browser...")
            browser.quit_browser()
            return filtered_news_cards
        else:
            print("No recent news cards found within the time limit.")
            print("\nClosing browser...")
            browser.quit_browser()
            return {}

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        browser.quit_browser()
        return {}


def test_bbc_home_navigation():
    """Test function for standalone execution"""
    data = scrape_bbc(headless=False)
    print(f"\nTest completed successfully! Collected {len(data)} articles.")


if __name__ == "__main__":
    test_bbc_home_navigation()