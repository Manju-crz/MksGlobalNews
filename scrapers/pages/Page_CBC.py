import re
import sys
import os
from utils.common_utils import CommonUtils

# Add parent directory to path for config utility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from util.configUtil import ConfigUtil


class CBCPage:

    def __init__(self, page):
        self.page = page
        self.timeout = 10000
        self.common_utils = CommonUtils(page)

    def scroll_page_after_load(self):
        """Scroll page down and up after loading"""
        print("\n" + "="*80)
        print("Scrolling page to load dynamic content...")
        print("="*80)
        self.common_utils.scroll_page_smoothly(direction='down', duration=2)
        print("="*80)

    def wait_for_page_load(self):
        try:
            print("Waiting for page to load (3 seconds)...")
            import time
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Error waiting for page load: {str(e)}")
            return False

    def get_page_title(self):
        try:
            title = self.page.title()
            print(f"Page title: {title}")
            return title
        except Exception as e:
            print(f"Error getting page title: {str(e)}")
            return None

    def get_current_url(self):
        try:
            url = self.page.url
            print(f"Current URL: {url}")
            return url
        except Exception as e:
            print(f"Error getting current URL: {str(e)}")
            return None

    def _is_within_time_limit(self, time_text):
        time_text = time_text.strip().lower()

        # Pattern for minutes: "X minutes ago", "X mins ago", "X min ago"
        mins_pattern = r'(\d+)\s*(?:minutes?|mins?)\s*ago'
        # Pattern for hours: "X hours ago", "X hour ago"
        hrs_pattern = r'(\d+)\s*hours?\s*ago'

        mins_match = re.search(mins_pattern, time_text)
        if mins_match:
            if ConfigUtil.should_include_minutes_ago():
                return True
            else:
                return False

        hrs_match = re.search(hrs_pattern, time_text)
        if hrs_match:
            hours = int(hrs_match.group(1))
            time_limit = ConfigUtil.get_time_limit_hours()
            if hours <= time_limit:
                return True

        return False

    def get_recent_news_cards(self):
        try:
            print("Finding all news card elements...")
            # Find all cards with contentWrapper
            card_elements = self.page.locator('div.contentWrapper').all()
            print(f"Found {len(card_elements)} total card elements")

            filtered_cards = []

            for index, card in enumerate(card_elements):
                try:
                    # Find time element within the card
                    time_element = card.locator('time.timeStamp')
                    time_text = time_element.text_content(timeout=3000)

                    if self._is_within_time_limit(time_text):
                        filtered_cards.append(card)
                        print(f"Card {index + 1}: '{time_text}' - INCLUDED")
                    else:
                        print(f"Card {index + 1}: '{time_text}' - EXCLUDED (exceeds 6 hours)")

                except Exception as e:
                    print(f"Card {index + 1}: No metadata found or error - {str(e)}")
                    continue

            print(f"\nTotal filtered cards: {len(filtered_cards)}")
            return filtered_cards

        except Exception as e:
            print(f"Error finding news cards: {str(e)}")
            return []

    def get_card_details(self, card_element):
        try:
            details = {}

            try:
                # Headline from h3.headline
                headline = card_element.locator('h3.headline')
                details['headline'] = headline.text_content(timeout=3000)
            except:
                details['headline'] = None

            try:
                # Author name
                author = card_element.locator('div.authorName')
                details['author'] = author.text_content(timeout=3000)
            except:
                details['author'] = None

            try:
                # Time from time.timeStamp
                time_element = card_element.locator('time.timeStamp')
                details['time_updated'] = time_element.text_content(timeout=3000)
            except:
                details['time_updated'] = None

            try:
                # Department/category from metadataText
                metadata_text = card_element.locator('div.metadataText')
                details['category'] = metadata_text.text_content(timeout=3000)
            except:
                details['category'] = None

            return details

        except Exception as e:
            print(f"Error extracting card details: {str(e)}")
            return None

    def read_article_paragraphs(self):
        try:
            print("Reading article paragraphs from the page...")
            self.page.wait_for_selector('div.story', timeout=self.timeout)

            # Find all paragraph elements in the story div
            paragraphs = self.page.locator('div.story p').all()

            paragraph_texts = []
            for index, para in enumerate(paragraphs, 1):
                text = para.inner_text(timeout=3000).strip()
                if text:
                    paragraph_texts.append(text)
                    # Show first 150 chars for preview, but full text is stored
                    preview = text if len(text) <= 150 else text[:150] + "..."
                    print(f"Paragraph {index}: {preview}")

            full_text = "\n\n".join(paragraph_texts)
            print(f"\nTotal paragraphs read: {len(paragraph_texts)}")

            return {
                'full_text': full_text,
                'paragraph_list': paragraph_texts,
                'paragraph_count': len(paragraph_texts)
            }

        except Exception as e:
            print(f"Error reading article paragraphs: {str(e)}")
            return None