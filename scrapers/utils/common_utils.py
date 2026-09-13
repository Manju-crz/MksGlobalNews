import time
from playwright.sync_api import Page


class CommonUtils:

    def __init__(self, page: Page):
        self.page = page
        self.timeout = 10000

    def click_element_by_tag_and_text(self, tag_name: str, text_content: str) -> bool:
        """Clicks an element by tag name and partial text match."""
        try:
            print(f"Looking for <{tag_name}> element containing text: '{text_content}'")
            locator = self.page.locator(tag_name).filter(has_text=text_content).first
            locator.wait_for(timeout=self.timeout)
            print("Element found. Clicking on it...")
            locator.click()
            return True
        except Exception as e:
            print(f"Error clicking element by tag and text: {str(e)}")
            return False

    def click_element_by_exact_tag_and_text(self, tag_name: str, exact_text: str) -> bool:
        """Clicks an element by tag name and exact text match."""
        try:
            print(f"Looking for <{tag_name}> element with exact text: '{exact_text}'")
            locator = self.page.locator(tag_name).get_by_text(exact_text, exact=True).first
            locator.wait_for(timeout=self.timeout)
            print("Element found. Clicking on it...")
            locator.click()
            return True
        except Exception as e:
            print(f"Error clicking element by exact tag and text: {str(e)}")
            return False

    def scroll_page_down(self, scroll_distance: int | None = None, delay: float = 0.5) -> bool:
        """Scroll down the page. If scroll_distance is None, scrolls to bottom."""
        try:
            print("Scrolling page down...")
            if scroll_distance:
                self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                print(f"Scrolled down by {scroll_distance}px")
            else:
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print("Scrolled to bottom of page")

            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Error scrolling page down: {str(e)}")
            return False

    def scroll_page_up(self, scroll_distance: int | None = None, delay: float = 0.5) -> bool:
        """Scroll up the page. If scroll_distance is None, scrolls to top."""
        try:
            print("Scrolling page up...")
            if scroll_distance:
                self.page.evaluate(f"window.scrollBy(0, -{scroll_distance})")
                print(f"Scrolled up by {scroll_distance}px")
            else:
                self.page.evaluate("window.scrollTo(0, 0)")
                print("Scrolled to top of page")

            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Error scrolling page up: {str(e)}")
            return False

    def scroll_page_smoothly(self, direction: str = 'down', duration: float = 2.0, steps: int = 5) -> bool:
        """
        Gradually scrolls the page in increments to trigger lazy-loaded images/cards,
        then returns to origin.
        """
        try:
            print(f"Performing step-based smooth scroll ({direction} first)...")

            if direction == 'down':
                for _ in range(steps):
                    self.page.evaluate("window.scrollBy(0, document.body.scrollHeight / 5)")
                    time.sleep(duration / steps)
                self.scroll_page_up(delay=0.5)
            else:
                self.scroll_page_up(delay=duration)
                self.scroll_page_down(delay=0.5)

            print("Smooth scroll completed")
            return True
        except Exception as e:
            print(f"Error during smooth scroll: {str(e)}")
            return False