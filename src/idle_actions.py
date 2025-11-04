"""
Phase 3: Idle Actions During Opponent's Turn
Simulates human behavior like random mouse movements, checking pieces, etc.
"""
import logging
import random
import time


class IdleActions:
    """
    Performs human-like idle actions during opponent's turn.
    """

    def __init__(self, config, browser):
        self.config = config
        self.browser = browser
        self.enabled = config.getboolean("idle_actions", "enabled", fallback=False)

        if self.enabled:
            self.action_probability = config.getfloat("idle_actions", "action_probability", fallback=0.25)
            action_types_str = config.get("idle_actions", "action_types", fallback="random_move,piece_hover,board_scan")
            self.action_types = [x.strip() for x in action_types_str.split(',')]

            logging.info(f"Idle actions enabled: {self.action_types}")

    def perform_idle_action(self):
        """
        Randomly perform an idle action during opponent's turn.
        """
        if not self.enabled:
            return

        # Random chance to perform action
        if random.random() > self.action_probability:
            return

        # Choose random action type
        action = random.choice(self.action_types)
        logging.debug(f"Performing idle action: {action}")

        try:
            if action == "random_move":
                self._random_mouse_movement()
            elif action == "piece_hover":
                self._hover_random_piece()
            elif action == "board_scan":
                self._scan_board()
            elif action == "tab_check":
                self._simulate_tab_check()
        except Exception as e:
            logging.debug(f"Error during idle action '{action}': {e}")

    def _random_mouse_movement(self):
        """
        Move mouse to random screen position (simulates looking away).
        """
        try:
            # Get viewport dimensions
            viewport = self.browser.page.viewport_size
            width = viewport['width']
            height = viewport['height']

            # Random position within viewport
            target_x = random.randint(100, width - 100)
            target_y = random.randint(100, height - 100)

            # Smooth movement with Bezier curve (reuse from automove)
            current_pos = self.browser.page.evaluate("() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })")
            current_x = current_pos.get('x', width // 2)
            current_y = current_pos.get('y', height // 2)

            self._smooth_mouse_move(current_x, current_y, target_x, target_y)

            # Stay there briefly
            time.sleep(random.uniform(0.5, 2.0))

            logging.debug(f"Random mouse movement to ({target_x}, {target_y})")
        except Exception as e:
            logging.debug(f"Error in random mouse movement: {e}")

    def _hover_random_piece(self):
        """
        Hover over a random piece on the board (simulates analysis).
        """
        try:
            # Select a random square (1-8 for both file and rank)
            file_num = random.randint(1, 8)
            rank_num = random.randint(1, 8)
            square_class = f".square-{file_num}{rank_num}"

            # Try to find the square element
            square_element = self.browser.page.query_selector(square_class)
            if square_element:
                box = square_element.bounding_box()
                if box:
                    # Move to center of square
                    center_x = box['x'] + box['width'] / 2
                    center_y = box['y'] + box['height'] / 2

                    current_pos = self.browser.page.evaluate("() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })")
                    current_x = current_pos.get('x', center_x)
                    current_y = current_pos.get('y', center_y)

                    self._smooth_mouse_move(current_x, current_y, center_x, center_y)

                    # Hover for a moment (analyzing piece)
                    hover_time = random.uniform(0.8, 3.0)
                    time.sleep(hover_time)

                    logging.debug(f"Hovered over square {file_num}{rank_num} for {hover_time:.1f}s")
        except Exception as e:
            logging.debug(f"Error in piece hover: {e}")

    def _scan_board(self):
        """
        Move mouse across board in scanning pattern (simulates evaluation).
        """
        try:
            # Define scan path: diagonal or horizontal sweep
            scan_type = random.choice(["diagonal", "horizontal", "vertical"])

            squares_to_visit = []
            if scan_type == "diagonal":
                # Diagonal scan (a1 to h8 or similar)
                for i in range(1, 9):
                    squares_to_visit.append((i, i))
            elif scan_type == "horizontal":
                # Horizontal scan of random rank
                rank = random.randint(1, 8)
                for file in range(1, 9):
                    squares_to_visit.append((file, rank))
            else:  # vertical
                # Vertical scan of random file
                file = random.randint(1, 8)
                for rank in range(1, 9):
                    squares_to_visit.append((file, rank))

            # Visit 3-5 squares along the path
            num_squares = random.randint(3, 5)
            selected_squares = random.sample(squares_to_visit, min(num_squares, len(squares_to_visit)))

            current_x, current_y = 0, 0
            for i, (file_num, rank_num) in enumerate(selected_squares):
                square_class = f".square-{file_num}{rank_num}"
                square_element = self.browser.page.query_selector(square_class)

                if square_element:
                    box = square_element.bounding_box()
                    if box:
                        target_x = box['x'] + box['width'] / 2
                        target_y = box['y'] + box['height'] / 2

                        if i == 0:
                            # First square, get current position
                            current_pos = self.browser.page.evaluate("() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })")
                            current_x = current_pos.get('x', target_x)
                            current_y = current_pos.get('y', target_y)

                        self._smooth_mouse_move(current_x, current_y, target_x, target_y)
                        current_x, current_y = target_x, target_y

                        # Brief pause at each square
                        time.sleep(random.uniform(0.3, 1.0))

            logging.debug(f"Board scan completed: {scan_type} pattern")
        except Exception as e:
            logging.debug(f"Error in board scan: {e}")

    def _simulate_tab_check(self):
        """
        Simulate checking another tab briefly (mouse leaves chess area).
        """
        try:
            # Move mouse to top of screen (tab area)
            viewport = self.browser.page.viewport_size
            width = viewport['width']

            target_x = random.randint(200, width - 200)
            target_y = random.randint(5, 40)  # Top bar area

            current_pos = self.browser.page.evaluate("() => ({ x: window.innerWidth / 2, y: window.innerHeight / 2 })")
            current_x = current_pos.get('x', width // 2)
            current_y = current_pos.get('y', 300)

            self._smooth_mouse_move(current_x, current_y, target_x, target_y)

            # "Check tab" briefly
            time.sleep(random.uniform(1.0, 3.0))

            # Return to board area
            board_x = random.randint(300, width - 300)
            board_y = random.randint(200, 600)
            self._smooth_mouse_move(target_x, target_y, board_x, board_y)

            logging.debug("Simulated tab check")
        except Exception as e:
            logging.debug(f"Error in tab check simulation: {e}")

    def _smooth_mouse_move(self, from_x, from_y, to_x, to_y):
        """
        Smooth mouse movement using simple linear interpolation.
        Lighter version than the full Bezier curve in automove.

        Args:
            from_x, from_y: Starting position
            to_x, to_y: Target position
        """
        import math

        distance = math.sqrt((to_x - from_x)**2 + (to_y - from_y)**2)
        steps = max(5, int(distance / 30))

        for i in range(steps + 1):
            t = i / steps
            x = from_x + (to_x - from_x) * t
            y = from_y + (to_y - from_y) * t

            # Small jitter
            jitter_x = random.uniform(-2, 2)
            jitter_y = random.uniform(-2, 2)

            self.browser.page.mouse.move(x + jitter_x, y + jitter_y)
            self.browser.page.wait_for_timeout(random.uniform(15, 40))
