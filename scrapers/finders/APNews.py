import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.browser_utility import BrowserUtility
from utils.common_utils import CommonUtils
from pages.page_APNews import APNewsPage
import time


def scrape_apnews(headless=False):
    """Scrape AP News and return data dictionary"""
    browser = BrowserUtility()

    try:
        print("Launching AP News website...")
        page = browser.launch_browser(url="https://apnews.com/", headless=headless)

        apnews_page = APNewsPage(page)
        apnews_page.wait_for_page_load()

        # Scroll page to load dynamic content
        apnews_page.scroll_page_after_load()

        print("\n" + "="*80)
        print("Checking for notification bar...")
        print("="*80)
        apnews_page.close_notification_bar_if_visible()

        print("\nGetting current page title and URL...")
        apnews_page.get_page_title()
        apnews_page.get_current_url()

        print("\n" + "="*80)
        print("Fetching recent news cards...")
        print("="*80 + "\n")
        recent_cards = apnews_page.get_recent_news_cards()

        news_cards = {}

        if recent_cards:
            print(f"\n{'='*80}")
            print(f"Extracting details from {len(recent_cards)} filtered cards...")
            print(f"{'='*80}\n")

            for index, card in enumerate(recent_cards, 1):
                details = apnews_page.get_card_details(card)
                # Only add cards with valid headlines (not None, not empty, not 'none')
                if details and details.get('headline') and details.get('headline').strip() and details.get('headline').lower() != 'none':
                    news_cards[f"card_{len(news_cards) + 1}"] = details
                else:
                    print(f"Skipping card {index}: Invalid or missing headline")

        if news_cards:
            print(f"\n{'='*80}")
            print(f"Clicking on each headline and reading article content...")
            print(f"{'='*80}\n")

            common_utils = CommonUtils(page)

            for card_key, card_details in news_cards.items():
                headline = card_details.get('headline')

                if headline and headline.lower() != 'none':
                    print(f"\n{'='*80}")
                    print(f"Processing {card_key}: {headline}")
                    print(f"{'='*80}")

                    try:
                        # Find <a> tag with the headline text in h3.PagePromo-title
                        print(f"Looking for headline link...")
                        link_selector = f'h3.PagePromo-title a span.PagePromoContentIcons-text:has-text("{headline}")'
                        page.wait_for_selector(link_selector, timeout=5000)
                        print("Link found. Clicking on it...")
                        page.click(link_selector, timeout=10000)
                        time.sleep(3)

                        article_content = apnews_page.read_article_paragraphs()

                        if article_content:
                            news_cards[card_key]['article_content'] = article_content['full_text']
                            news_cards[card_key]['paragraph_count'] = article_content['paragraph_count']
                            print(f"\nArticle content added to {card_key}")

                        page.go_back()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Failed to click on headline for {card_key}: {str(e)}")

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
                print(f"    'reading_time': '{card_details.get('reading_time', 'N/A')}'")
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
            print("No recent news cards found.")
            print("\nClosing browser...")
            browser.quit_browser()
            return {}

    except KeyboardInterrupt:
        print("\n\nClosing browser...")
        browser.quit_browser()
        return {}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        browser.quit_browser()
        return {}


def test_apnews_navigation():
    """Test function for standalone execution"""
    data = scrape_apnews(headless=False)
    print(f"\nTest completed successfully! Collected {len(data)} articles.")


if __name__ == "__main__":
    test_apnews_navigation()