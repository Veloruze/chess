import logging
from playwright.sync_api import sync_playwright, Page, Browser
from src import selectors
import re

class ChessBrowser:
    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page = None
        self.nickname = "null"
        self.current_elo = "null"

    def start(self):
        """Starts the browser with anti-detection features."""
        logging.debug("Starting browser with stealth mode...")
        self.playwright = sync_playwright().start()

        # Launch browser with anti-automation flags
        self.browser = self.playwright.chromium.launch(
            headless=self.config.getboolean("play", "headless"),
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--window-size=1920,1080',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )

        self.page = self.browser.new_page()

        # Inject stealth scripts to mask automation
        self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Spoof Chrome user agent
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            });

            // Add realistic plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Spoof languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Add chrome property
            window.chrome = {
                runtime: {}
            };

            // Spoof permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        logging.info("Browser started with anti-detection features enabled")

    def login(self, username, password):
        """Logs into chess.com."""
        logging.debug("Logging in...")
        self.page.goto("https://www.chess.com/login")
        self.page.fill(selectors.LOGIN_USERNAME_INPUT, username)
        self.page.fill(selectors.LOGIN_PASSWORD_INPUT, password)
        login_button_selectors = [
            "button:has-text('Log In')",
            "button[type='submit']", # Fallback
        ]
        clicked = False
        for selector in login_button_selectors:
            try:
                with self.page.expect_navigation():
                    self.page.click(selector, timeout=5000)
                clicked = True
                break
            except Exception:
                logging.debug(f"Could not click login button with selector: {selector}")
        
        if not clicked:
            logging.error("Failed to find and click any login button.")
            raise Exception("Login button not found.")

        if "chess.com" not in self.page.url or "login" in self.page.url:
            screenshot_path = "login_failure.png"
            self.page.screenshot(path=screenshot_path)
            logging.error(f"Login failed. Current URL: {self.page.url}. Screenshot saved to {screenshot_path}")
            raise Exception("Login failed: Not redirected to home page.")
        logging.debug("Login successful.")
        try:
            self.page.wait_for_selector("a.home-username-link", timeout=20000) # Wait for username link as login success indicator
            logging.debug("Home page loaded successfully after login.")
        except Exception as e:
            screenshot_path = "home_page_load_failure.png"
            self.page.screenshot(path=screenshot_path)
            logging.error(f"Home page did not load after login: {e}. Screenshot saved to {screenshot_path}")
            raise
        
        

    def select_mode(self):
        """Selects the game mode."""
        logging.info(f"Selecting mode: {self.config.get('play', 'mode')}")
        try:
            self.page.goto("https://www.chess.com/play/online", timeout=30000) # Increased timeout for goto
            self.page.wait_for_url("https://www.chess.com/play/online", timeout=30000) # Explicitly wait for URL
            self.page.wait_for_selector(selectors.TIME_CONTROL_DROPDOWN_BUTTON, timeout=30000) # Wait for a key element
            logging.info("Successfully navigated to play online page.")
        except Exception as e:
            screenshot_path = "play_online_navigation_failure.png"
            self.page.screenshot(path=screenshot_path)
            logging.error(f"Failed to navigate to play online page: {e}. Screenshot saved to {screenshot_path}")
            raise

        # Click the time control dropdown button
        try:
            self.page.click(selectors.TIME_CONTROL_DROPDOWN_BUTTON, timeout=10000)
            logging.info("Clicked time control dropdown.")
        except Exception as e:
            logging.error(f"Could not click time control dropdown: {e}")
            raise

        mode = self.config.get("play", "mode").lower()
        time_control_selector = selectors.TIME_CONTROL_SELECTORS.get(mode)

        if not time_control_selector:
            logging.error(f"Invalid mode specified: {mode}")
            raise ValueError(f"Invalid mode specified: {mode}")

        try:
            # Wait for the specific time control option to be visible after dropdown click
            self.page.wait_for_selector(time_control_selector, state="visible", timeout=10000)
            self.page.click(time_control_selector, timeout=10000)
            logging.info(f"Clicked time control: {mode}")
        except Exception as e:
            logging.error(f"Could not click time control {mode}: {e}")
            raise

        clicked_play_button = False
        for selector in selectors.PLAY_BUTTON_SELECTORS:
            try:
                with self.page.expect_navigation():
                    self.page.click(selector, timeout=5000)
                clicked_play_button = True
                break
            except Exception:
                logging.debug(f"Could not click play button with selector: {selector}")

        if not clicked_play_button:
            logging.error("Failed to find and click any play button.")
            raise Exception("Play button not found.")

        try:
            self.page.wait_for_selector(selectors.BOARD_SELECTOR, timeout=30000)
            logging.debug("Board loaded successfully.")
            self._extract_user_info() # Extract user info after board is loaded
        except Exception as e:
            logging.error(f"Board did not load after selecting mode: {e}")
            raise

    def _extract_user_info(self):
        """Extracts nickname and ELO rating from the current page."""
        try:
            # Wait for at least one of the nickname selectors to be visible
            # Use page.locator().or_().wait_for() for multiple XPath selectors
            self.page.locator(selectors.USER_TAGLINE_USERNAME_SELECTOR).or_(
                self.page.locator(selectors.CC_USER_USERNAME_SELECTOR)
            ).wait_for(timeout=10000)

            # Extract Nickname
            nickname_element = self.page.query_selector(selectors.USER_TAGLINE_USERNAME_SELECTOR) or \
                               self.page.query_selector(selectors.CC_USER_USERNAME_SELECTOR)
            if nickname_element:
                self.nickname = nickname_element.inner_text().strip()
            else:
                self.nickname = "null"

            # Wait for at least one of the ELO selectors to be visible
            self.page.locator(selectors.CC_USER_RATING_SELECTOR_WHITE).or_(
                self.page.locator(selectors.CC_USER_RATING_SELECTOR_BLACK)
            ).wait_for(timeout=10000)
            # Extract ELO Rating
            elo_element = self.page.query_selector(selectors.CC_USER_RATING_SELECTOR_WHITE) or \
                          self.page.query_selector(selectors.CC_USER_RATING_SELECTOR_BLACK)
            if elo_element:
                elo_text = elo_element.inner_text().strip()
                elo_match = re.search(r'\((\d+)\)', elo_text)
                if elo_match:
                    self.current_elo = elo_match.group(1)
                else:
                    self.current_elo = "null"
            else:
                self.current_elo = "null"

            logging.info(f"User: {self.nickname}, ELO: {self.current_elo}")
        except Exception as e:
            logging.warning(f"Could not extract user info: {e}")
            self.nickname = "null"
            self.current_elo = "null"

    def close(self):
        """Closes the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()