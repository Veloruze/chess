"""
Phase 5: Human-like Typing Patterns
Simulates realistic typing speed with occasional typos and corrections
"""
import logging
import random
import time


class HumanTyping:
    """
    Handles human-like typing with variable speed and occasional errors.
    """

    def __init__(self, config):
        self.config = config
        self.enabled = config.getboolean("typing_patterns", "enabled", fallback=False)

        if self.enabled:
            self.min_cpm = config.getfloat("typing_patterns", "min_typing_speed_cpm", fallback=180)
            self.max_cpm = config.getfloat("typing_patterns", "max_typing_speed_cpm", fallback=350)
            self.typo_probability = config.getfloat("typing_patterns", "typo_probability", fallback=0.05)
            self.min_correction_delay = config.getfloat("typing_patterns", "min_correction_delay", fallback=0.3)
            self.max_correction_delay = config.getfloat("typing_patterns", "max_correction_delay", fallback=1.2)

            logging.info(f"Human typing enabled: {self.min_cpm}-{self.max_cpm} CPM")

    def type_text(self, page, selector, text):
        """
        Type text into a field with human-like characteristics.

        Args:
            page: Playwright page object
            selector: CSS selector for input field
            text: Text to type
        """
        if not self.enabled:
            # Fallback to regular typing
            page.fill(selector, text)
            return

        # Clear field first
        page.fill(selector, "")

        # Click field to focus
        page.click(selector)
        time.sleep(random.uniform(0.1, 0.3))

        # Type character by character
        for i, char in enumerate(text):
            # Calculate delay based on CPM (characters per minute)
            cpm = random.uniform(self.min_cpm, self.max_cpm)
            base_delay = 60.0 / cpm  # seconds per character

            # Add variation to each keystroke (humans aren't perfectly consistent)
            delay = base_delay * random.uniform(0.7, 1.3)

            # Occasional longer pauses (thinking/looking at keyboard)
            if random.random() < 0.05:
                delay += random.uniform(0.3, 1.0)

            # Check for typo
            if random.random() < self.typo_probability and i < len(text) - 1:
                # Make a typo (type wrong character)
                wrong_char = self._get_adjacent_key(char)
                page.type(selector, wrong_char, delay=0)
                logging.debug(f"Typo: typed '{wrong_char}' instead of '{char}'")

                # Pause (realize mistake)
                correction_delay = random.uniform(self.min_correction_delay, self.max_correction_delay)
                time.sleep(correction_delay)

                # Backspace to delete typo
                page.keyboard.press("Backspace")
                time.sleep(random.uniform(0.1, 0.2))

            # Type the correct character
            page.type(selector, char, delay=0)
            time.sleep(delay)

        # Small pause after finishing typing (before clicking submit)
        time.sleep(random.uniform(0.2, 0.6))

        logging.debug(f"Typed '{text}' with human-like pattern")

    def _get_adjacent_key(self, char):
        """
        Get a key adjacent to the given character on QWERTY keyboard.

        Args:
            char: Original character

        Returns:
            Adjacent character (for typo simulation)
        """
        # QWERTY keyboard layout
        keyboard_layout = {
            'q': ['w', 'a'],
            'w': ['q', 'e', 's'],
            'e': ['w', 'r', 'd'],
            'r': ['e', 't', 'f'],
            't': ['r', 'y', 'g'],
            'y': ['t', 'u', 'h'],
            'u': ['y', 'i', 'j'],
            'i': ['u', 'o', 'k'],
            'o': ['i', 'p', 'l'],
            'p': ['o', 'l'],
            'a': ['q', 's', 'z'],
            's': ['w', 'a', 'd', 'x'],
            'd': ['e', 's', 'f', 'c'],
            'f': ['r', 'd', 'g', 'v'],
            'g': ['t', 'f', 'h', 'b'],
            'h': ['y', 'g', 'j', 'n'],
            'j': ['u', 'h', 'k', 'm'],
            'k': ['i', 'j', 'l'],
            'l': ['o', 'k', 'p'],
            'z': ['a', 'x'],
            'x': ['z', 's', 'c'],
            'c': ['x', 'd', 'v'],
            'v': ['c', 'f', 'b'],
            'b': ['v', 'g', 'n'],
            'n': ['b', 'h', 'm'],
            'm': ['n', 'j'],
        }

        char_lower = char.lower()
        if char_lower in keyboard_layout and keyboard_layout[char_lower]:
            adjacent = random.choice(keyboard_layout[char_lower])
            # Preserve original case
            if char.isupper():
                return adjacent.upper()
            return adjacent

        # If not in layout, return a random nearby letter
        return random.choice('qwertyuiopasdfghjklzxcvbnm')

    def pause_before_action(self, min_delay=0.5, max_delay=2.0):
        """
        Add a human-like pause before performing an action.

        Args:
            min_delay: Minimum pause duration
            max_delay: Maximum pause duration
        """
        if not self.enabled:
            time.sleep(random.uniform(0.2, 0.5))
            return

        pause = random.uniform(min_delay, max_delay)
        time.sleep(pause)
        logging.debug(f"Human pause: {pause:.2f}s")
