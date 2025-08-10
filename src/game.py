import logging
import chess
from src.engine import StockfishEngine
from src.automove import AutoMove
from src import selectors
from playwright.sync_api import Error, TimeoutError as PlaywrightTimeoutError
import random
import time # Import time module
from src.engine import _parse_config_value

class Game:
    """
    Manages the game state and interaction.
    """
    # A simple opening book mapping FEN strings to a list of UCI moves.
    # This can be expanded with more openings and variations.
    OPENING_BOOK = {
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": ["e2e4", "d2d4", "g1f3", "c2c4"],
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": ["c7c5", "e7e5", "c7c6"],
        "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": ["g8f6", "d7d5", "c7c5"],
    }
    def __init__(self, config, browser, stats, display_callback):
        self.config = config
        self.browser = browser
        self.stats = stats # Store stats object
        self.display_callback = display_callback # Store display callback
        self.board = chess.Board()
        self.engine = StockfishEngine(config)
        self.automove = AutoMove(config, browser, stats, display_callback)
        self.color = None

    def start(self):
        """Starts the game loop."""
        self.board = chess.Board() # Reset the board for a new game
        self.detect_color()
        if self.color == chess.WHITE:
            logging.info("Playing as WHITE, attempting to make first move...")
            self.browser.page.wait_for_timeout(3000) # Add 3 second delay for first move as White
            self.play_best_move()
        self.track_moves()

        # Remove the infinite loop here, as main.py will handle game restarts
        # while True:
        #     self.browser.page.wait_for_timeout(1000) # Wait for a second

    def detect_color(self):
        """Detects the player's color and extracts user info."""
        logging.debug("Detecting color...")
        board_element = self.browser.page.wait_for_selector(selectors.BOARD_SELECTOR)
        self.browser._extract_user_info() # Extract user info now that the game board is loaded
        class_name = board_element.get_attribute("class")
        if "flipped" in class_name:
            self.color = chess.BLACK
            logging.debug("Playing as BLACK")
        else:
            self.color = chess.WHITE
            logging.debug("Playing as WHITE")
        logging.debug(f"Detected color: {self.color} (chess.WHITE: {chess.WHITE}, chess.BLACK: {chess.BLACK})")

    

    def _update_stats_from_result(self, result_text):
        """
        Updates game statistics based on the game result text.
        """
        if result_text == "1-0": # White wins
            if self.color == chess.WHITE:
                self.stats.wins += 1
            else:
                self.stats.losses += 1
        elif result_text == "0-1": # Black wins
            if self.color == chess.BLACK:
                self.stats.wins += 1
            else:
                self.stats.losses += 1
        elif result_text == "1/2-1/2": # Draw
            self.stats.draws += 1
        else:
            logging.warning(f"Unknown game result text: {result_text}")
            return

        # Update win rate
        total_games = self.stats.wins + self.stats.losses + self.stats.draws
        if total_games > 0:
            self.stats.win_rate = (self.stats.wins / total_games) * 100

    def track_moves(self):
        """Tracks moves made on the board."""
        logging.debug("Tracking moves...")

        try:
            self.browser.page.wait_for_selector("wc-simple-move-list", state='attached', timeout=20000) # Ensure move list is present
        except Exception as e:
            screenshot_path = "move_list_failure.png"
            self.browser.page.screenshot(path=screenshot_path)
            logging.error(f"Move list element not found: {e}. Screenshot saved to {screenshot_path}")
            raise
        
        while True:
            # Prioritize checking for game result element
            game_result_element = self.browser.page.query_selector(selectors.GAME_RESULT_SELECTOR)
            if game_result_element:
                result_text = game_result_element.inner_text().strip()
                logging.info(f"Game result element detected: {result_text}. Exiting track_moves.")
                self._update_stats_from_result(result_text)
                return # Exit track_moves if game result is found

            if self.board.is_game_over():
                result = self.board.result()
                logging.info(f"Game is over. Result: {result}")
                self._update_stats_from_result(result)
                return # Exit track_moves if game is over
            
            # Check for game over modal as an alternative way to detect game end
            game_over_modal = self.browser.page.query_selector(".game-over-modal-content")
            if game_over_modal:
                logging.debug("Game over modal detected. Exiting track_moves.")
                return

            try:
                expected_ply = self.board.ply()
                xpath = f"//div[@data-node='0-{expected_ply}']"
                logging.debug(f"Waiting for opponent move with XPath: {xpath}")
                
                move_element = self.browser.page.wait_for_selector(xpath, timeout=10000) # Wait up to 10 seconds for opponent move
                raw_san_move = move_element.inner_text().strip()
                logging.info(f"Opponent move detected (raw): {raw_san_move}")
                
                # Clean the move string from the UI (e.g., "1. e4 " -> "e4")
                san_move = raw_san_move.split('.')[-1].strip()

                # Attempt to extract piece type for ambiguous SAN moves (e.g., captures like 'xb1')
                if san_move.startswith('x') or (len(san_move) == 2 and san_move[0].islower() and san_move[1].isdigit()): # Likely a pawn move or capture without explicit piece
                    try:
                        # Look for piece icon within the move element
                        piece_icon_element = move_element.query_selector("span[class*='icon-font-chess']")
                        if piece_icon_element:
                            class_list = piece_icon_element.get_attribute("class").split()
                            piece_char = ''
                            for cls in class_list:
                                if cls.startswith('knight'): piece_char = 'N'
                                elif cls.startswith('bishop'): piece_char = 'B'
                                elif cls.startswith('rook'): piece_char = 'R'
                                elif cls.startswith('queen'): piece_char = 'Q'
                                elif cls.startswith('king'): piece_char = 'K'
                                # Pawns don't have a piece character in SAN unless capturing, which is handled by 'x'
                            if piece_char and not san_move.startswith(piece_char):
                                san_move = piece_char + san_move
                                logging.debug(f"Disambiguated SAN move with piece: {san_move}")
                    except Exception as e:
                        logging.debug(f"Could not extract piece type for SAN disambiguation: {e}")

                logging.debug(f"Opponent move detected (cleaned SAN): {san_move}")
                
                self.handle_move(san_move)
            except Error as e: # Catch TimeoutException specifically
                if isinstance(e, PlaywrightTimeoutError):
                    logging.debug("Timeout waiting for opponent move. Checking for game over modal.")
                    try:
                        game_over_modal = self.browser.page.wait_for_selector(".game-over-modal-content", timeout=2000) # Wait up to 2 seconds for modal
                        logging.debug("Game over modal detected after timeout. Exiting track_moves.")
                        # If modal is detected, we should also try to get the result from the .game-result span
                        # as it's likely to be present with the modal.
                        game_result_element_on_modal = self.browser.page.query_selector(selectors.GAME_RESULT_SELECTOR)
                        if game_result_element_on_modal:
                            result_text = game_result_element_on_modal.inner_text().strip()
                            logging.info(f"Game result element detected within modal: {result_text}.")
                            self._update_stats_from_result(result_text)
                        else:
                            logging.warning("Game over modal detected, but could not find game result element.")
                        return # Exit track_moves if game is over
                    except Error as modal_e:
                        if isinstance(modal_e, PlaywrightTimeoutError):
                            if logging.getLogger().level == logging.DEBUG:
                                logging.debug("Timeout waiting for opponent move, but no game over modal found within 2 seconds. Continuing to wait for opponent move.")
                            # If no game over modal, it means opponent is just taking a long time.
                            # The outer while True loop will re-enter the try block and wait again.
                            pass
                        else:
                            logging.error(f"An unexpected error occurred while checking for game over modal: {modal_e}")
                            break # Break for other unexpected errors during modal check
                else:
                    logging.error(f"An unexpected error occurred while tracking moves: {e}")
                    break # Break for other unexpected errors

    def handle_move(self, san_move):
        """
        Handles a move made on the board.
        """
        logging.debug(f"handle_move called with SAN move: {san_move}")
        logging.debug(f"Opponent move: {san_move}")
        move_successfully_pushed = False
        try:
            move = self.board.parse_san(san_move)
            self.board.push(move)
            move_successfully_pushed = True
        except ValueError:
            # Handle incomplete/ambiguous SAN (e.g., "xd4" or "Nf3")
            move_found = False
            for move in self.board.legal_moves:
                if self.board.san(move) == san_move or self.board.san(move).endswith(san_move):
                    self.board.push(move)
                    move_found = True
                    move_successfully_pushed = True
                    logging.debug(f"Successfully parsed ambiguous SAN move: {san_move} as {move}")
                    break
            if not move_found:
                logging.warning(f"Could not parse SAN move: {san_move} on board FEN: {self.board.fen()}")

        if move_successfully_pushed:
            self.display_callback() # Refresh HUD after a move is pushed
            logging.debug(f"Current board turn: {self.board.turn}, Player color: {self.color}")
            if self.board.turn == self.color:
                self.play_best_move()

    def _get_remaining_time(self):
        """Attempts to get the remaining time for the current player from the UI."""
        try:
            # This selector might need adjustment based on actual Chess.com HTML structure
            # It looks for the time element for the current player (bottom player)
            time_element_selector = ".clock-bottom .clock-time-monospace"
            time_text = self.browser.page.evaluate(f"document.querySelector('{time_element_selector}').innerText")
            
            # Parse time_text (e.g., "0:59", "1:30", "10:00") into seconds
            minutes, seconds = map(int, time_text.split(':'))
            remaining_seconds = minutes * 60 + seconds
            logging.debug(f"Remaining time detected: {remaining_seconds} seconds")
            return remaining_seconds
        except Exception as e:
            logging.warning(f"Could not get remaining time from UI: {e}")
            return None # Return None if time cannot be retrieved

    def play_best_move(self):
        """
        Calculates and plays the best move using the Stockfish engine.
        """
        try:
            move_start_time = time.time() # Start timing the move

            # Check opening book first
            current_fen = self.board.fen()
            if current_fen in self.OPENING_BOOK:
                possible_moves = self.OPENING_BOOK[current_fen]
                # Filter out illegal moves from the opening book
                legal_opening_moves = [
                    move for move in possible_moves
                    if chess.Move.from_uci(move) in self.board.legal_moves
                ]
                if legal_opening_moves:
                    best_move_uci = random.choice(legal_opening_moves)
                    best_move = chess.Move.from_uci(best_move_uci)
                    logging.debug(f"Playing opening book move: {best_move_uci}")
                else:
                    logging.debug("No legal opening book moves found, falling back to engine.")
                    best_move, moves_with_scores = self.engine.get_best_move(self.board)
                    logging.info(f"Best move: {best_move.uci()}")
            else:
                best_move, moves_with_scores = self.engine.get_best_move(self.board)
                logging.info(f"Best move: {best_move.uci()}")

            if best_move is None:
                logging.error("No best move found by the engine.")
                return

            moves_with_scores = [] # Initialize moves_with_scores

            # Contextual thinking time
            # This delay is applied in addition to the random delay in automove.py
            additional_delay = 0

            # Advanced Time Management
            advanced_time_management = self.config.getboolean("play", "advanced_time_management")
            if advanced_time_management:
                remaining_time = self._get_remaining_time()
                if remaining_time is not None:
                    # Adjust delay based on remaining time
                    # This is a simplified example; more sophisticated logic can be added.
                    if remaining_time < 10: # Less than 10 seconds left
                        logging.debug(f"Low time ({remaining_time}s). Reducing thinking time.")
                        additional_delay = max(0, additional_delay - 0.3) # Reduce delay, ensure not negative
                    elif remaining_time > 60: # More than 60 seconds left
                        logging.debug(f"Plenty of time ({remaining_time}s). Increasing thinking time.")
                        additional_delay += 0.5 # Add more delay

                # Add artificial random delay
                min_art_delay = float(_parse_config_value(self.config.get("play", "min_artificial_move_delay_seconds")))
                max_art_delay = float(_parse_config_value(self.config.get("play", "max_artificial_move_delay_seconds")))
                if min_art_delay > 0 or max_art_delay > 0:
                    random_artificial_delay = random.uniform(min_art_delay, max_art_delay)
                    additional_delay += random_artificial_delay
                    logging.debug(f"Added random artificial delay: {random_artificial_delay:.2f}s. Total additional delay: {additional_delay:.2f}s.")

            if additional_delay > 0:
                logging.debug(f"Applying total additional delay of {additional_delay:.2f}s.")
                time.sleep(additional_delay) # Use time.sleep for seconds

            logging.debug("Starting highlight process...")
            from_square_alg = chess.square_name(best_move.from_square)
            to_square_alg = chess.square_name(best_move.to_square)
            logging.debug(f"Calculated from_square_alg: {from_square_alg}, to_square_alg: {to_square_alg}")
            file_awal_num = ord(from_square_alg[0]) - ord("a") + 1
            file_tujuan_num = ord(to_square_alg[0]) - ord("a") + 1
            rank_awal_num_chess = int(from_square_alg[1])
            rank_tujuan_num_chess = int(to_square_alg[1])

            is_board_flipped = False
            logging.debug("Attempting to find board element for flipped check.")
            try:
                board_element = self.browser.page.wait_for_selector("#board-single", timeout=5000, force=True)
                if board_element and "flipped" in board_element.get_attribute("class"):
                    is_board_flipped = True
            except Exception:
                logging.debug("Board element or flipped class not found, assuming not flipped for highlight.")
                pass # Board element or flipped class not found, assume not flipped

            if is_board_flipped:
                rank_awal_num_html = 9 - rank_awal_num_chess
                rank_tujuan_num_html = 9 - rank_tujuan_num_chess
            else:
                rank_awal_num_html = rank_awal_num_chess
                rank_tujuan_num_html = rank_tujuan_num_chess

            lokasi_awal = f"{file_awal_num}{rank_awal_num_html}"
            lokasi_tujuan = f"{file_tujuan_num}{rank_tujuan_num_html}"

            logging.debug(f"Attempting to draw suggestion from {from_square_alg} ({lokasi_awal}) to {to_square_alg} ({lokasi_tujuan})")
            logging.debug(f"Board flipped: {is_board_flipped}")
            logging.debug(f"Highlighting from {lokasi_awal} to {lokasi_tujuan}")
            try:
                logging.debug("Executing highlight script...")
                self.browser.page.evaluate(f'''
                    var highlight1 = document.getElementById("highlight1");
                    if (highlight1) {{
                      highlight1.remove();
                    }}
                    var highlight2 = document.getElementById("highlight2");
                    if (highlight2) {{
                      highlight2.remove();
                    }}
                    var board = document.getElementById("board-single");
                    if (board) {{
                        var element1 = document.createElement("div");
                        element1.setAttribute("id", "highlight1");
                        element1.setAttribute("style", "background-color: rgb(255,0,0); opacity: 0.5;");
                        element1.setAttribute("class", "highlight square-{lokasi_awal}");
                        board.appendChild(element1);
                        var element2 = document.createElement("div");
                        element2.setAttribute("id", "highlight2");
                        element2.setAttribute("style", "background-color: rgb(0,255,255); opacity: 0.5;");
                        element2.setAttribute("class", "highlight square-{lokasi_tujuan}");
                        board.appendChild(element2);
                    }} else {{
                        console.error("Board element with ID 'board-single' not found for highlighting.");
                    }}
                ''')
                logging.debug("Highlight script executed.")
            except Exception as e:
                logging.error(f"Terjadi kesalahan saat menyorot kotak: {e}")

            move_duration = time.time() - move_start_time

            logging.debug("Starting auto-move process...")
            logging.debug(f"Passing is_flipped: {self.color == chess.BLACK} (self.color: {self.color})")
            self.automove.execute_move(best_move, self.board.ply() // 2, is_flipped=self.color == chess.BLACK, move_duration=move_duration)
            logging.debug("Auto-move process finished. Pushing move to board.")
            self.board.push(best_move)
        except Exception as e:
            logging.error(f"An error occurred in play_best_move: {e}")