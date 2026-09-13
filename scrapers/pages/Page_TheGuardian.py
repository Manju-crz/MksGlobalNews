import re
from utils.common_utils import CommonUtils


class TheGuardianPage:

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

        self.privacy_message_selector = "div.message.type-bottom"
        self.close_button_selector = "button.gu-close-btn.sp_choice_type_11"

    def close_privacy_message_if_visible(self):
        try:
            print("Checking if privacy message is visible...")

            if self.page.locator(self.privacy_message_selector).is_visible():
                print("Privacy message detected. Looking for close button...")

                close_button = self.page.locator(self.close_button_selector)

                if close_button.is_visible():
                    print("Close button found. Clicking on it...")
                    close_button.click()
                    print("Privacy message closed successfully.")
                    return True
                else:
                    print("Close button not visible.")
                    return False
            else:
                print("Privacy message not visible. No action needed.")
                return True

        except Exception as e:
            print(f"Error closing privacy message: {str(e)}")
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

    def wait_for_page_load(self, timeout=3):
        import time
        print(f"Waiting for page to load ({timeout} seconds)...")
        time.sleep(timeout)

    def _is_within_time_limit(self, time_text):
        time_text = time_text.strip().lower()

        mins_pattern = r'(\d+)m\s*ago'
        hrs_pattern = r'(\d+)h\s*ago'

        mins_match = re.search(mins_pattern, time_text)
        if mins_match:
            return True

        hrs_match = re.search(hrs_pattern, time_text)
        if hrs_match:
            hours = int(hrs_match.group(1))
            if hours <= 6:
                return True

        return False

    def get_recent_news_cards(self):
        try:
            print("Finding all news card elements...")
            # Find all h3.card-headline elements, then get their closest parent container
            headlines = self.page.locator('h3.card-headline').all()

            # Get unique parent containers by using a set to track seen cards
            seen_headlines = set()
            card_elements = []

            for headline in headlines:
                try:
                    headline_text = headline.text_content(timeout=2000)
                    # Skip if headline is None, empty, or already seen
                    if headline_text and headline_text.strip() and headline_text.lower() != 'none' and headline_text not in seen_headlines:
                        seen_headlines.add(headline_text)
                        # Get the parent container that has both headline and footer
                        parent = headline.locator('xpath=ancestor::div[.//footer//time][1]')
                        if parent.count() > 0:
                            card_elements.append(parent.first)
                except:
                    continue

            print(f"Found {len(card_elements)} total card elements")

            filtered_cards = []

            for index, card in enumerate(card_elements):
                try:
                    time_element = card.locator('footer time')
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
                headline = card_element.locator('h3.card-headline span.headline-text')
                details['headline'] = headline.text_content(timeout=3000)
            except:
                details['headline'] = None

            try:
                # Kicker is the first div inside h3.card-headline
                kicker = card_element.locator('h3.card-headline > div').first
                details['kicker'] = kicker.text_content(timeout=3000)
            except:
                details['kicker'] = None

            try:
                time_element = card_element.locator('footer time')
                details['time_updated'] = time_element.text_content(timeout=3000)
            except:
                details['time_updated'] = None

            return details

        except Exception as e:
            print(f"Error extracting card details: {str(e)}")
            return None

    def read_article_paragraphs(self):
        try:
            print("Reading article paragraphs from the page...")
            self.page.wait_for_selector('div.article-body-viewer-selector', timeout=self.timeout)

            paragraphs = self.page.locator('div.article-body-viewer-selector p.dcr-1s160rg').all()

            paragraph_texts = []
            for index, para in enumerate(paragraphs, 1):
                # Use inner_text() to properly handle nested tags like strong, a, etc.
                text = para.inner_text(timeout=5000).strip()
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