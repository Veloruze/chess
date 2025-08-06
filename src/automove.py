
import logging
import random
import time
import math
from src import selectors

class AutoMove:
    """
    Executes a move on the board.
    """
    def __init__(self, config, browser):
        self.config = config
        self.browser = browser

    def execute_move(self, move, letak_gerakan, is_flipped=False):
        """
        Executes a move on the board.
        """
        logging.debug(f"automove.execute_move received is_flipped: {is_flipped}")
        auto_move_enabled = self.config.getboolean("play", "auto_move")
        logging.debug(f"Auto-move enabled: {auto_move_enabled}")
        if not auto_move_enabled:
            return

        mode = self.config.get('play', 'mode')
        # Assuming letak_gerakan is passed as an argument to execute_move
        # For now, let's assume a placeholder or that it will be passed.
        # I will add it as a parameter to execute_move in the next step.
        # For now, I'll use a placeholder for letak_gerakan to implement the delay logic.
        # This will be corrected when modifying the function signature.

        # Placeholder for letak_gerakan, will be replaced with actual parameter
        # For now, let's assume letak_gerakan is available.
        # I will add letak_gerakan as a parameter to execute_move in the next step.
        # For now, I'll use a dummy value or assume it's passed.

        # The user provided the logic, so I'll implement it as is,
        # and then adjust the function signature to accept letak_gerakan.

        # The user's provided code snippet:
        if mode == 'bullet':
            if letak_gerakan <= 15:
                waktu = random.uniform(0.05,0.10)
                print('delay', waktu,' detik')
                time.sleep( waktu )
            else:
                waktu = random.uniform(0.05,0.25)
                print('delay', waktu,' detik')
                time.sleep( waktu )
        elif mode == 'blitz':
            if letak_gerakan <= 15:
                waktu = random.uniform(0.05,0.25)
                print('delay', waktu,' detik')
                time.sleep( waktu )
            else:
                waktu = random.uniform(0.05,1.25)
                print('delay', waktu,' detik')
                time.sleep( waktu )
        elif mode == 'rapid':
            if letak_gerakan <= 15:
                waktu = random.uniform(0.05,1.25)
                print('delay', waktu,' detik')
                time.sleep( waktu )
            else:
                waktu = random.uniform(0.05,2.25)
                print('delay', waktu,' detik')
                time.sleep( waktu )

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

            # Perform drag and drop with human-like mouse movement
            # This involves moving the mouse in small steps with random offsets and delays
            # to simulate a less robotic and more natural mouse trajectory.
            self.browser.page.mouse.move(from_x, from_y)
            self.browser.page.mouse.down()
            self.browser.page.wait_for_timeout(100) # Small initial delay for visual effect

            # Number of steps for the mouse movement. More steps mean smoother, but slower, movement.
            steps = 10 
            for i in range(steps + 1):
                # Calculate intermediate coordinates along a straight line
                current_x = from_x + (to_x - from_x) * i / steps
                current_y = from_y + (to_y - from_y) * i / steps

                # Add a small random offset to simulate human-like imperfection and variability
                # This offset is not applied to the final destination to ensure accuracy.
                if i < steps: 
                    current_x += random.uniform(-2, 2) # Random offset in X direction (e.g., -2 to +2 pixels)
                    current_y += random.uniform(-2, 2) # Random offset in Y direction (e.g., -2 to +2 pixels)

                self.browser.page.mouse.move(current_x, current_y)
                # Small random delay between steps to make the movement less instantaneous
                self.browser.page.wait_for_timeout(random.uniform(5, 20)) # Delay between 5 and 20 milliseconds

            self.browser.page.mouse.up()

            logging.debug(f"Successfully dragged from {from_selector} to {to_selector}")
        except Exception as e:
            logging.error(f"Terjadi kesalahan saat melakukan gerakan otomatis: {e}. From selector: {from_selector}, To selector: {to_selector}")
