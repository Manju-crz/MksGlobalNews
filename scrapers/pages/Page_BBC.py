import re
import sys
import os
from utils.common_utils import CommonUtils

# Add parent directory to path for config utility
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from util.configUtil import ConfigUtil


class BBCPage:

    def __init__(self, page):
        self.page = page
        self.timeout = 10000
        self.common_utils = CommonUtils(page)

        self.home_link_selector = "a[data-testid='mainNavigationLink-active']:has-text('Home')"
        self.privacy_modal_selector = "div.message.type-modal"
        self.accept_button_selector = "button.sp_choice_type_11"

    def scroll_page_after_load(self):
        """Scroll page down and up after loading"""
        print("\n" + "="*80)
        print("Scrolling page to load dynamic content...")
        print("="*80)
        self.common_utils.scroll_page_smoothly(direction='down', duration=2)
        print("="*80)

    def close_privacy_modal_if_visible(self):
        try:
            print("Checking if privacy modal iframe is visible...")
            import time

            # Wait for iframe to appear (max 5 seconds)
            try:
                iframe_selector = 'iframe[id*="sp_message_iframe"]'
                self.page.wait_for_selector(iframe_selector, timeout=5000, state='visible')
                print("Privacy modal iframe detected. Switching to iframe context...")

                # Get the iframe element
                iframe_element = self.page.frame_locator(iframe_selector)

                # Wait for and click the accept button inside the iframe
                print("Looking for 'Accept and Continue' button inside iframe...")

                # Try multiple button selectors
                button_selectors = [
                    'button[title="Accept and Continue"]',
                    'button[aria-label="Accept and Continue"]',
                    'button.sp_choice_type_11',
                    'button:has-text("Accept and Continue")'
                ]

                clicked = False
                for selector in button_selectors:
                    try:
                        accept_button = iframe_element.locator(selector)
                        accept_button.wait_for(timeout=3000, state='visible')
                        print(f"Button found with selector: {selector}. Clicking...")

                        # Try JavaScript click as well
                        try:
                            accept_button.evaluate("button => button.click()")
                            print("Privacy modal button clicked via JavaScript.")
                        except:
                            accept_button.click(force=True, timeout=5000)
                            print("Privacy modal button clicked via Playwright.")

                        clicked = True
                        break
                    except Exception as btn_err:
                        print(f"Failed with selector {selector}: {str(btn_err)}")
                        continue

                if not clicked:
                    print("Could not find or click accept button with any selector.")
                    return False

                # Wait for modal to close and verify it's gone
                time.sleep(3)

                # Check if iframe is still visible
                try:
                    self.page.wait_for_selector(iframe_selector, timeout=2000, state='hidden')
                    print("Privacy modal closed and hidden successfully.")
                except:
                    print("Warning: Modal iframe may still be visible.")

                return True

            except Exception as e:
                print(f"Privacy modal not visible or timed out: {str(e)}")
                print("No action needed - continuing with scraping.")
                return True

        except Exception as e:
            print(f"Error closing privacy modal: {str(e)}")
            return False

    def close_survey_popup_if_visible(self):
        try:
            print("Checking if survey popup is visible...")
            import time

            try:
                # Wait for survey popup to appear (max 3 seconds)
                survey_close_selector = 'a#no:has-text("Close")'
                self.page.wait_for_selector(survey_close_selector, timeout=3000, state='visible')
                print("Survey popup detected. Clicking 'Close' button...")

                # Click the close button
                self.page.click(survey_close_selector, timeout=3000)
                print("Survey popup closed successfully.")

                # Wait a moment for popup to close
                time.sleep(1)
                return True

            except Exception as e:
                print(f"Survey popup not visible or timed out: {str(e)}")
                print("No action needed - continuing with scraping.")
                return True

        except Exception as e:
            print(f"Error closing survey popup: {str(e)}")
            return False

    def click_home_link(self):
        try:
            print("Looking for HOME link...")
            self.page.wait_for_selector(self.home_link_selector, timeout=self.timeout)
            print("HOME link found. Clicking on it...")
            self.page.click(self.home_link_selector)
            return True
        except Exception as e:
            print(f"Error clicking HOME link: {str(e)}")
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

        mins_pattern = r'(\d+)\s*mins?\s*ago'
        hrs_pattern = r'(\d+)\s*hrs?\s*ago'

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
            card_elements = self.page.locator('div[data-testid="card-text-wrapper"]').all()
            print(f"Found {len(card_elements)} total card elements")

            filtered_cards = []

            for index, card in enumerate(card_elements):
                try:
                    metadata_element = card.locator('span[data-testid="card-metadata-lastupdated"]')
                    time_text = metadata_element.text_content(timeout=3000)

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
                headline = card_element.locator('h2[data-testid="card-headline"]')
                details['headline'] = headline.text_content(timeout=3000)
            except:
                details['headline'] = None

            try:
                description = card_element.locator('p[data-testid="card-description"]')
                details['description'] = description.text_content(timeout=3000)
            except:
                details['description'] = None

            try:
                time_updated = card_element.locator('span[data-testid="card-metadata-lastupdated"]')
                details['time_updated'] = time_updated.text_content(timeout=3000)
            except:
                details['time_updated'] = None

            try:
                tag = card_element.locator('span[data-testid="card-metadata-tag"]')
                details['tag'] = tag.text_content(timeout=3000)
            except:
                details['tag'] = None

            return details

        except Exception as e:
            print(f"Error extracting card details: {str(e)}")
            return None

    def read_article_paragraphs(self):
        try:
            print("Reading article paragraphs from the page...")
            self.page.wait_for_selector('article', timeout=self.timeout)

            # Use more stable selector - any p tag with class starting with "Paragraph-styles__ParagraphStyled"
            paragraphs = self.page.locator('article p[class*="Paragraph-styles__ParagraphStyled"]').all()

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