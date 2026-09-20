import re
import sys
import os
from utils.common_utils import CommonUtils

# Add parent directory to path for config utility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from util.configUtil import ConfigUtil


class DWPage:

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

    def close_consent_popup_if_visible(self):
        try:
            print("Checking if consent popup is visible...")
            import time

            try:
                # Wait for consent popup to appear (max 5 seconds)
                consent_box_selector = 'div.cmpboxinner'
                self.page.wait_for_selector(consent_box_selector, timeout=5000, state='visible')
                print("Consent popup detected. Looking for 'Agree' button...")

                # Click the Agree button
                agree_button_selector = 'a.cmpboxbtnyes:has-text("Agree")'
                self.page.wait_for_selector(agree_button_selector, timeout=3000, state='visible')
                print("'Agree' button found. Clicking...")

                # Try JavaScript click first
                try:
                    self.page.locator(agree_button_selector).evaluate("button => button.click()")
                    print("Consent 'Agree' button clicked via JavaScript.")
                except:
                    self.page.click(agree_button_selector, force=True, timeout=5000)
                    print("Consent 'Agree' button clicked via Playwright.")

                # Wait for popup to close
                time.sleep(2)

                # Verify popup is gone
                try:
                    self.page.wait_for_selector(consent_box_selector, timeout=2000, state='hidden')
                    print("Consent popup closed successfully.")
                except:
                    print("Warning: Consent popup may still be visible.")

                return True

            except Exception as e:
                print(f"Consent popup not visible or timed out: {str(e)}")
                print("No action needed - continuing with scraping.")
                return True

        except Exception as e:
            print(f"Error closing consent popup: {str(e)}")
            return False

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

            # Find all teaser-wrap cards
            teaser_cards = self.page.locator('div.teaser-wrap[data-tracking-list-item="true"]').all()
            print(f"Found {len(teaser_cards)} teaser-wrap cards")

            # Find all news-item cards
            news_item_cards = self.page.locator('div.news-item[data-tracking-list-item="true"]').all()
            print(f"Found {len(news_item_cards)} news-item cards")

            # Combine both types
            all_cards = teaser_cards + news_item_cards
            print(f"Total cards found: {len(all_cards)}")

            filtered_cards = []

            for index, card in enumerate(all_cards):
                try:
                    # Try to find time element - different selectors for different card types
                    time_text = None

                    # Try teaser-wrap format first
                    try:
                        time_element = card.locator('span.date-time time')
                        time_text = time_element.text_content(timeout=3000)
                    except:
                        # Try news-item format
                        try:
                            time_element = card.locator('span.timestamp time')
                            time_text = time_element.text_content(timeout=3000)
                        except:
                            pass

                    if time_text and self._is_within_time_limit(time_text):
                        filtered_cards.append(card)
                        print(f"Card {index + 1}: '{time_text}' - INCLUDED")
                    elif time_text:
                        print(f"Card {index + 1}: '{time_text}' - EXCLUDED (exceeds 6 hours)")
                    else:
                        print(f"Card {index + 1}: No time metadata found")

                except Exception as e:
                    print(f"Card {index + 1}: Error - {str(e)}")
                    continue

            print(f"\nTotal filtered cards: {len(filtered_cards)}")
            return filtered_cards

        except Exception as e:
            print(f"Error finding news cards: {str(e)}")
            return []

    def get_card_details(self, card_element):
        try:
            details = {}

            # Try to extract headline - different selectors for different card types
            try:
                # Try teaser-wrap format (h4.title a)
                headline = card_element.locator('h4.title a')
                details['headline'] = headline.text_content(timeout=3000)
            except:
                try:
                    # Try news-item format (h3 a)
                    headline = card_element.locator('h3 a')
                    details['headline'] = headline.text_content(timeout=3000)
                except:
                    details['headline'] = None

            # Description (only in teaser-wrap cards)
            try:
                description = card_element.locator('div.teaser-description a')
                details['description'] = description.text_content(timeout=3000)
            except:
                details['description'] = None

            # Time - try both formats
            try:
                # Try teaser-wrap format
                time_element = card_element.locator('span.date-time time')
                details['time_updated'] = time_element.text_content(timeout=3000)
            except:
                try:
                    # Try news-item format
                    time_element = card_element.locator('span.timestamp time')
                    details['time_updated'] = time_element.text_content(timeout=3000)
                except:
                    details['time_updated'] = None

            # Kicker/category (only in teaser-wrap cards)
            try:
                kicker = card_element.locator('span.kicker')
                details['kicker'] = kicker.text_content(timeout=3000)
            except:
                details['kicker'] = None

            return details

        except Exception as e:
            print(f"Error extracting card details: {str(e)}")
            return None

    def read_article_paragraphs(self):
        try:
            print("Reading article paragraphs from the page...")
            self.page.wait_for_selector('div.content-area', timeout=self.timeout)

            # Find all paragraph elements in the rich-text content area
            paragraphs = self.page.locator('div.rich-text p').all()

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