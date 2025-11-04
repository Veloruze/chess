
import logging
import random
import time
import math
from src import selectors

class AutoMove:
    """
    Executes a move on the board with human-like behavior.
    """
    def __init__(self, config, browser):
        self.config = config
        self.browser = browser
        self.fast_mode = False  # Flag for fast movement in time pressure

    def _human_mouse_move(self, from_x, from_y, to_x, to_y):
        """
        Simulate human-like mouse movement using Bezier curves with jitter.
        Uses fast mode when in time pressure.
        """
        # FAST MODE: Simplified movement for time pressure
        if self.fast_mode:
            # Direct linear movement with minimal steps
            steps = 5  # Much fewer steps
            for i in range(steps + 1):
                t = i / steps
                x = from_x + (to_x - from_x) * t
                y = from_y + (to_y - from_y) * t
                self.browser.page.mouse.move(x, y)
                self.browser.page.wait_for_timeout(2)  # Minimal delay (2ms)
            return

        # NORMAL MODE: Full Bezier curve animation
        # Calculate distance
        distance = math.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)

        # Dynamic steps based on distance (more steps = smoother but slower)
        steps = max(10, int(distance / 15) + random.randint(3, 8))

        # Generate Bezier curve control points with randomness
        control_x1 = from_x + (to_x - from_x) * random.uniform(0.2, 0.4)
        control_y1 = from_y + (to_y - from_y) * random.uniform(0.2, 0.4) + random.randint(-30, 30)

        control_x2 = from_x + (to_x - from_x) * random.uniform(0.6, 0.8)
        control_y2 = from_y + (to_y - from_y) * random.uniform(0.6, 0.8) + random.randint(-30, 30)

        logging.debug(f"Human mouse movement: {steps} steps from ({from_x:.1f}, {from_y:.1f}) to ({to_x:.1f}, {to_y:.1f})")

        for i in range(steps + 1):
            t = i / steps

            # Cubic Bezier curve formula
            x = ((1-t)**3 * from_x +
                 3*(1-t)**2*t * control_x1 +
                 3*(1-t)*t**2 * control_x2 +
                 t**3 * to_x)

            y = ((1-t)**3 * from_y +
                 3*(1-t)**2*t * control_y1 +
                 3*(1-t)*t**2 * control_y2 +
                 t**3 * to_y)

            # Add micro-jitter (simulates human hand shake)
            jitter_x = random.uniform(-1.5, 1.5)
            jitter_y = random.uniform(-1.5, 1.5)

            self.browser.page.mouse.move(x + jitter_x, y + jitter_y)

            # Variable speed (slower at start/end, faster in middle)
            # This simulates human acceleration/deceleration
            if t < 0.25 or t > 0.75:
                delay = random.uniform(12, 25)  # Slower at endpoints
            else:
                delay = random.uniform(6, 15)   # Faster in middle

            self.browser.page.wait_for_timeout(delay)

    def _add_overshoot_correction(self, target_x, target_y):
        """
        Occasionally overshoot target and correct (15% chance).
        Simulates human imprecision.
        """
        if random.random() < 0.15:  # 15% chance
            logging.debug("Adding overshoot correction")

            # Overshoot by small amount
            overshoot_x = target_x + random.uniform(-8, 8)
            overshoot_y = target_y + random.uniform(-8, 8)

            self.browser.page.mouse.move(overshoot_x, overshoot_y)
            self.browser.page.wait_for_timeout(random.uniform(40, 100))

            # Correct back to target
            self.browser.page.mouse.move(target_x, target_y)
            self.browser.page.wait_for_timeout(random.uniform(30, 80))

    def execute_move(self, move, letak_gerakan, is_flipped=False, move_duration=0.0):
        """
        Executes a move on the board with human-like mouse behavior.
        """
        logging.debug(f"automove.execute_move received is_flipped: {is_flipped}")
        auto_move_enabled = self.config.getboolean("play", "auto_move")
        logging.debug(f"Auto-move enabled: {auto_move_enabled}")
        if not auto_move_enabled:
            return

        from_square_xy = selectors.algebraic_to_xy_selector(move.uci()[:2], is_flipped)
        to_square_xy = selectors.algebraic_to_xy_selector(move.uci()[2:], is_flipped)

        logging.debug(f"Auto-moving {move.uci()[:2]} to {move.uci()[2:]} (XY: {from_square_xy} to {to_square_xy})")

        from_selector = "#highlight1"
        to_selector = "#highlight2"

        logging.debug(f"From selector: {from_selector}")
        logging.debug(f"To selector: {to_selector}")

        try:
            logging.debug(f"Attempting to drag and drop from {from_selector} to {to_selector}")

            # Get bounding box of the from_selector element
            from_element = self.browser.page.locator(from_selector)
            from_element.wait_for(state='visible', timeout=5000)
            from_box = from_element.bounding_box()
            if not from_box:
                raise Exception(f"Could not get bounding box for {from_selector}")
            from_x = from_box['x'] + from_box['width'] / 2
            from_y = from_box['y'] + from_box['height'] / 2

            # Get bounding box of the to_selector element
            to_element = self.browser.page.locator(to_selector)
            to_element.wait_for(state='visible', timeout=5000)
            to_box = to_element.bounding_box()
            if not to_box:
                raise Exception(f"Could not get bounding box for {to_selector}")
            to_x = to_box['x'] + to_box['width'] / 2
            to_y = to_box['y'] + to_box['height'] / 2

            # Move to start position with human-like movement
            current_pos = self.browser.page.evaluate("() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })")
            current_x = current_pos.get('x', from_x)
            current_y = current_pos.get('y', from_y)

            self._human_mouse_move(current_x, current_y, from_x, from_y)

            if self.fast_mode:
                # FAST MODE: Minimal delays
                self.browser.page.wait_for_timeout(10)  # Tiny hover
                self.browser.page.mouse.down()
                self.browser.page.wait_for_timeout(10)  # Tiny hold
                self._human_mouse_move(from_x, from_y, to_x, to_y)  # Fast linear drag
                self.browser.page.wait_for_timeout(10)  # Tiny drop delay
                self.browser.page.mouse.up()
            else:
                # NORMAL MODE: Full human-like animation
                # Small hover before clicking (human hesitation)
                hover_delay = random.uniform(80, 300)
                self.browser.page.wait_for_timeout(hover_delay)

                # Click and hold
                self.browser.page.mouse.down()
                hold_delay = random.uniform(50, 180)
                self.browser.page.wait_for_timeout(hold_delay)

                # Occasional mid-drag hesitation (5% chance)
                if random.random() < 0.05:
                    logging.debug("Adding mid-drag hesitation")
                    mid_x = (from_x + to_x) / 2 + random.uniform(-20, 20)
                    mid_y = (from_y + to_y) / 2 + random.uniform(-20, 20)
                    self._human_mouse_move(from_x, from_y, mid_x, mid_y)
                    self.browser.page.wait_for_timeout(random.uniform(200, 600))

                # Complete drag with Bezier curve
                self._human_mouse_move(from_x, from_y, to_x, to_y)

                # Add overshoot correction (15% chance)
                self._add_overshoot_correction(to_x, to_y)

                # Drop with slight delay
                drop_delay = random.uniform(40, 150)
                self.browser.page.wait_for_timeout(drop_delay)
                self.browser.page.mouse.up()

            logging.debug(f"Successfully executed human-like drag from {from_selector} to {to_selector}")
        except Exception as e:
            logging.error(f"Error during automated move execution: {e}. From: {from_selector}, To: {to_selector}")
