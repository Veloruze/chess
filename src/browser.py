import logging
from playwright.sync_api import sync_playwright, Page, Browser
from src import selectors
from src.human_typing import HumanTyping
import re

class ChessBrowser:
    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page = None
        self.nickname = "null"
        self.current_elo = "null"
        self.human_typing = HumanTyping(config)

    def start(self):
        """Starts the browser with anti-detection features."""
        logging.debug("Starting browser with stealth mode...")
        self.playwright = sync_playwright().start()

        # Phase 4: Randomize window size to prevent fingerprinting
        import random
        if self.config.getboolean("viewport", "randomize_window_size", fallback=False):
            min_width = self.config.getint("viewport", "min_window_width", fallback=1366)
            max_width = self.config.getint("viewport", "max_window_width", fallback=1920)
            min_height = self.config.getint("viewport", "min_window_height", fallback=768)
            max_height = self.config.getint("viewport", "max_window_height", fallback=1080)

            window_width = random.randint(min_width, max_width)
            window_height = random.randint(min_height, max_height)
            logging.info(f"Randomized window size: {window_width}x{window_height}")
        else:
            window_width = 1920
            window_height = 1080

        # Launch browser with anti-automation flags
        self.browser = self.playwright.chromium.launch(
            headless=self.config.getboolean("play", "headless"),
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                f'--window-size={window_width},{window_height}',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )

        self.page = self.browser.new_page()

        # Phase 4: Randomize viewport zoom (80-120%)
        if self.config.getboolean("viewport", "randomize_zoom", fallback=False):
            zoom_level = random.uniform(0.9, 1.1)
            self.page.evaluate(f"document.body.style.zoom = '{zoom_level}'")
            logging.debug(f"Randomized zoom level: {zoom_level:.2f}")

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
        """Logs into chess.com with human-like typing."""
        logging.debug("Logging in...")
        self.page.goto("https://www.chess.com/login")

        # Phase 5: Use human-like typing for credentials
        self.human_typing.type_text(self.page, selectors.LOGIN_USERNAME_INPUT, username)
        self.human_typing.pause_before_action(0.3, 0.8)
        self.human_typing.type_text(self.page, selectors.LOGIN_PASSWORD_INPUT, password)
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
            # Go to the main play page first
            self.page.goto("https://www.chess.com/play/online", timeout=30000)

            # Don't wait for networkidle (too unreliable with ads/tracking)
            # Instead wait for domcontentloaded which is faster and more reliable
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            logging.info("Navigated to play online page.")

            # Wait for page to fully load and ads to settle
            import time
            time.sleep(3)

            # Check if we need to select opponent type (vs Computer, vs Person, etc)
            # Sometimes Chess.com defaults to "Friend" mode, we need "Online" mode
            try:
                # Look for "Online" or "Rated" option and click it
                online_selectors = [
                    "button:has-text('Online')",
                    "button:has-text('Rated')",
                    "[data-cy='challenge-online']",
                ]
                for sel in online_selectors:
                    try:
                        elem = self.page.query_selector(sel)
                        if elem:
                            elem.click()
                            logging.info(f"Clicked online/rated mode selector: {sel}")
                            time.sleep(1)
                            break
                    except:
                        pass
            except Exception as e:
                logging.debug(f"Could not select opponent type (may not be needed): {e}")

            # Wait for time control dropdown
            self.page.wait_for_selector(selectors.TIME_CONTROL_DROPDOWN_BUTTON, timeout=30000)
            logging.info("Time control dropdown found.")
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

        # Wait a bit for the play button to appear after time control selection
        import time
        time.sleep(1)

        clicked_play_button = False

        # Try each selector with wait
        for selector in selectors.PLAY_BUTTON_SELECTORS:
            try:
                # Wait for the button to be visible
                self.page.wait_for_selector(selector, state="visible", timeout=3000)
                logging.debug(f"Found play button with selector: {selector}")

                # Click and wait for navigation
                with self.page.expect_navigation(timeout=15000):
                    self.page.click(selector, timeout=5000)

                clicked_play_button = True
                logging.info(f"Successfully clicked play button with selector: {selector}")
                break
            except Exception as e:
                logging.debug(f"Could not click play button with selector: {selector}, error: {e}")

        if not clicked_play_button:
            # Take screenshot for debugging
            screenshot_path = "play_button_failure.png"
            self.page.screenshot(path=screenshot_path)

            # Log all available buttons for debugging
            try:
                all_buttons = self.page.query_selector_all("button")
                button_texts = [btn.inner_text() for btn in all_buttons[:10]]  # First 10 buttons
                logging.error(f"Available buttons: {button_texts}")
            except Exception:
                pass

            logging.error(f"Failed to find and click any play button. Screenshot saved to {screenshot_path}")
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
        # Note: User info extraction disabled - selectors need updating for current Chess.com UI
        # This is non-critical for gameplay functionality
        try:
            # Try to extract username from common selectors
            username_selectors = [
                ".user-username-component",
                ".user-tagline-username",
                "[class*='username']"
            ]

            for selector in username_selectors:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        self.nickname = elem.inner_text().strip()
                        logging.debug(f"Found username: {self.nickname}")
                        break
                except:
                    continue

            # Try to extract rating
            rating_selectors = [
                ".user-tagline-rating",
                "[class*='rating']",
                ".clock-bottom"
            ]

            for selector in rating_selectors:
                try:
                    elem = self.page.query_selector(selector)
                    if elem:
                        text = elem.inner_text().strip()
                        elo_match = re.search(r'\((\d+)\)', text)
                        if elo_match:
                            self.current_elo = elo_match.group(1)
                            logging.debug(f"Found ELO: {self.current_elo}")
                            break
                except:
                    continue

            if self.nickname != "null" and self.current_elo != "null":
                logging.info(f"User: {self.nickname}, ELO: {self.current_elo}")

        except Exception as e:
            logging.debug(f"Could not extract user info: {e}")
            # Non-critical, continue without user info

    def close(self):
        """Closes the browser."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()