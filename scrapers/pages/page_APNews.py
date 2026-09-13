import re
from utils.common_utils import CommonUtils


class APNewsPage:

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

    def close_notification_bar_if_visible(self):
        try:
            print("Checking if notification bar is visible...")
            import time

            try:
                # Wait for notification bar to appear (max 5 seconds)
                notification_bar_selector = 'div.bcpNotificationBar'
                self.page.wait_for_selector(notification_bar_selector, timeout=5000, state='visible')
                print("Notification bar detected. Looking for close button...")

                # Click the close button
                close_button_selector = 'div.bcpNotificationBarClose'
                self.page.wait_for_selector(close_button_selector, timeout=3000, state='visible')
                print("Close button found. Clicking...")

                # Try JavaScript click first
                try:
                    self.page.locator(close_button_selector).evaluate("button => button.click()")
                    print("Notification bar close button clicked via JavaScript.")
                except:
                    self.page.click(close_button_selector, force=True, timeout=5000)
                    print("Notification bar close button clicked via Playwright.")

                # Wait for notification bar to close
                time.sleep(2)

                # Verify notification bar is gone
                try:
                    self.page.wait_for_selector(notification_bar_selector, timeout=2000, state='hidden')
                    print("Notification bar closed successfully.")
                except:
                    print("Warning: Notification bar may still be visible.")

                return True

            except Exception as e:
                print(f"Notification bar not visible or timed out: {str(e)}")
                print("No action needed - continuing with scraping.")
                return True

        except Exception as e:
            print(f"Error closing notification bar: {str(e)}")
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

        # Pattern for minutes: "X min read", "X mins read"
        mins_pattern = r'(\d+)\s*mins?\s*read'

        mins_match = re.search(mins_pattern, time_text)
        if mins_match:
            # For AP News, we'll include all articles with reading time
            # as they don't show "X hours ago" format
            return True

        return False

    def get_recent_news_cards(self):
        try:
            print("Finding all news card elements...")
            # Find all cards with PagePromo class
            card_elements = self.page.locator('div.PagePromo').all()
            print(f"Found {len(card_elements)} total card elements")

            filtered_cards = []

            for index, card in enumerate(card_elements):
                try:
                    # Find reading time element within the card
                    time_element = card.locator('span.ReadingTime-template')
                    time_text = time_element.text_content(timeout=3000)

                    if self._is_within_time_limit(time_text):
                        filtered_cards.append(card)
                        print(f"Card {index + 1}: '{time_text}' - INCLUDED")
                    else:
                        print(f"Card {index + 1}: '{time_text}' - EXCLUDED")

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
                # Headline from h3.PagePromo-title a
                headline = card_element.locator('h3.PagePromo-title a span.PagePromoContentIcons-text')
                details['headline'] = headline.text_content(timeout=3000)
            except:
                details['headline'] = None

            try:
                # Reading time from ReadingTime-template
                time_element = card_element.locator('span.ReadingTime-template')
                details['reading_time'] = time_element.text_content(timeout=3000)
            except:
                details['reading_time'] = None

            return details

        except Exception as e:
            print(f"Error extracting card details: {str(e)}")
            return None

    def read_article_paragraphs(self):
        try:
            print("Reading article paragraphs from the page...")
            self.page.wait_for_selector('div.RichTextStoryBody', timeout=self.timeout)

            # Find all paragraph elements in the RichTextStoryBody div
            paragraphs = self.page.locator('div.RichTextStoryBody p').all()

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