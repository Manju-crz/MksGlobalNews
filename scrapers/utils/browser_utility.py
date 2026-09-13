from playwright.sync_api import sync_playwright
import time


class BrowserUtility:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch_browser(self, url, headless=False, browser_type="chromium"):
        try:
            self.playwright = sync_playwright().start()

            if browser_type.lower() == "chromium" or browser_type.lower() == "chrome":
                self.browser = self.playwright.chromium.launch(
                    headless=headless,
                    args=["--start-maximized"]
                )
            elif browser_type.lower() == "firefox":
                self.browser = self.playwright.firefox.launch(headless=headless)
            elif browser_type.lower() == "webkit" or browser_type.lower() == "edge":
                self.browser = self.playwright.webkit.launch(headless=headless)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()

            # Set longer timeout and use 'domcontentloaded' instead of 'load'
            self.page.set_default_navigation_timeout(60000)  # 60 seconds
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            print(f"Browser launched successfully. Navigated to: {url}")
            print(f"Headless mode: {headless}")
            return self.page

        except Exception as e:
            print(f"Error launching browser: {str(e)}")
            raise

    def close_browser(self):
        if self.page:
            try:
                self.page.close()
                print("Browser page closed successfully")
            except Exception as e:
                print(f"Error closing browser page: {str(e)}")
        else:
            print("No browser page to close")

    def quit_browser(self):
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            print("Browser quit successfully. All windows closed")
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

        except Exception as e:
            print(f"Error quitting browser: {str(e)}")

    def refresh_page(self):
        if self.page:
            try:
                self.page.reload()
                print("Page refreshed successfully")
            except Exception as e:
                print(f"Error refreshing page: {str(e)}")
        else:
            print("No browser page available to refresh")

    def reload_page(self):
        if self.page:
            try:
                current_url = self.page.url
                self.page.goto(current_url)
                print(f"Page reloaded successfully: {current_url}")
            except Exception as e:
                print(f"Error reloading page: {str(e)}")
        else:
            print("No browser page available to reload")

    def navigate_to(self, url):
        if self.page:
            try:
                self.page.goto(url)
                print(f"Navigated to: {url}")
            except Exception as e:
                print(f"Error navigating to URL: {str(e)}")
        else:
            print("No browser page available for navigation")

    def go_back(self):
        if self.page:
            try:
                self.page.go_back()
                print("Navigated back to previous page")
            except Exception as e:
                print(f"Error navigating back: {str(e)}")
        else:
            print("No browser page available")

    def go_forward(self):
        if self.page:
            try:
                self.page.go_forward()
                print("Navigated forward to next page")
            except Exception as e:
                print(f"Error navigating forward: {str(e)}")
        else:
            print("No browser page available")

    def get_current_url(self):
        if self.page:
            try:
                current_url = self.page.url
                print(f"Current URL: {current_url}")
                return current_url
            except Exception as e:
                print(f"Error getting current URL: {str(e)}")
                return None
        else:
            print("No browser page available")
            return None

    def get_page_title(self):
        if self.page:
            try:
                title = self.page.title()
                print(f"Page title: {title}")
                return title
            except Exception as e:
                print(f"Error getting page title: {str(e)}")
                return None
        else:
            print("No browser page available")
            return None

    def maximize_window(self):
        if self.page:
            try:
                self.page.set_viewport_size({"width": 1920, "height": 1080})
                print("Browser window maximized")
            except Exception as e:
                print(f"Error maximizing window: {str(e)}")
        else:
            print("No browser page available")

    def minimize_window(self):
        if self.page:
            try:
                self.page.set_viewport_size({"width": 800, "height": 600})
                print("Browser window minimized")
            except Exception as e:
                print(f"Error minimizing window: {str(e)}")
        else:
            print("No browser page available")

    def set_window_size(self, width, height):
        if self.page:
            try:
                self.page.set_viewport_size({"width": width, "height": height})
                print(f"Window size set to {width}x{height}")
            except Exception as e:
                print(f"Error setting window size: {str(e)}")
        else:
            print("No browser page available")

    def take_screenshot(self, filename):
        if self.page:
            try:
                self.page.screenshot(path=filename)
                print(f"Screenshot saved as: {filename}")
                return True
            except Exception as e:
                print(f"Error taking screenshot: {str(e)}")
                return False
        else:
            print("No browser page available")
            return False

    def clear_cookies(self):
        if self.context:
            try:
                self.context.clear_cookies()
                print("All cookies cleared successfully")
            except Exception as e:
                print(f"Error clearing cookies: {str(e)}")
        else:
            print("No browser context available")

    def execute_script(self, script):
        if self.page:
            try:
                result = self.page.evaluate(script)
                print("JavaScript executed successfully")
                return result
            except Exception as e:
                print(f"Error executing script: {str(e)}")
                return None
        else:
            print("No browser page available")
            return None

    def switch_to_new_window(self):
        if self.context:
            try:
                pages = self.context.pages
                if len(pages) > 1:
                    self.page = pages[-1]
                    print("Switched to new window")
                else:
                    print("No new window available to switch")
            except Exception as e:
                print(f"Error switching window: {str(e)}")
        else:
            print("No browser context available")

    def switch_to_default_window(self):
        if self.context:
            try:
                pages = self.context.pages
                self.page = pages[0]
                print("Switched to default window")
            except Exception as e:
                print(f"Error switching to default window: {str(e)}")
        else:
            print("No browser context available")


if __name__ == "__main__":
    browser = BrowserUtility()

    url = input("Enter URL to launch: ").strip()
    if not url:
        url = "https://www.google.com"
        print(f"No URL provided. Using default: {url}")

    headless_input = input("Run in headless mode? (yes/no): ").strip().lower()
    headless = headless_input in ['yes', 'y', 'true', '1']

    browser_type = input(
        "Enter browser type (chrome/firefox/edge) [default: chrome]: "
    ).strip().lower()

    if not browser_type:
        browser_type = "chrome"

    try:
        browser.launch_browser(
            url=url,
            headless=headless,
            browser_type=browser_type
        )

        time.sleep(2)
        browser.get_page_title()
        browser.get_current_url()

        time.sleep(3)

        browser.quit_browser()

    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        browser.quit_browser()