import argparse
import configparser
import logging
import os
import sys
import time
import random
import datetime

from src.browser import ChessBrowser
from src.game import Game

CREDENTIALS_FILE = "credentials.txt"
from src.utils import _parse_config_value

# Helper function to calculate display width, accounting for wide characters like emojis and ignoring ANSI escape codes
def get_display_width(text):
    # Remove ANSI escape codes first
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    clean_text = ansi_escape.sub('', text)

    width = 0
    for char in clean_text:
        if ord(char) > 127: # Assuming non-ASCII characters are wide
            width += 2
        else:
            width += 1
    return width

def pad_to_inner_width(text, target_width):
    current_width = get_display_width(text)
    padding_needed = target_width - current_width
    return text + ' ' * max(0, padding_needed)

class GameStats:
    def __init__(self):
        self.nickname = "null"
        self.current_elo = "null"
        self.start_elo = "null"
        self.delta_elo = "+0"
        self.auto_move_enabled = False
        self.auto_play_enabled = False
        self.max_games_limit = 0
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.win_rate = 0.0
        self.avg_move_time = 0.0
        self.log_history = [] # Stores up to 10 log lines

    def add_log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_history.append(f"[{timestamp}] {message}")
        if len(self.log_history) > 10:
            self.log_history.pop(0)

def display_hud_and_log(stats, config):
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Get config values for HUD
    auto_move_status = "✅" if config.getboolean("play", "auto_move") else "❌"
    auto_play_status = "✅" if config.getboolean("play", "auto_play") else "❌"
    max_games_limit_display = str(stats.max_games_limit) if stats.max_games_limit != 0 else "Unlimited"

    # Define the inner width of the box
    INNER_WIDTH = 32

    # ANSI Color Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"

    # Prepare content for each line, then pad it
    # Nickname line
    line_nickname_content = f"{BOLD}{YELLOW}{stats.nickname}{RESET}"
    line_nickname = pad_to_inner_width(f"♔ {line_nickname_content}", INNER_WIDTH)

    # ELO line (removed "dari Start")
    line_elo_content = f"{BOLD}{YELLOW}{stats.current_elo}{RESET} ({BOLD}{YELLOW}{stats.delta_elo}{RESET})"
    line_elo = pad_to_inner_width(f"{BOLD}{GREEN}ELO            :{RESET} {line_elo_content}", INNER_WIDTH)

    # Auto Move line
    line_auto_move_content = f"{BOLD}{YELLOW}{auto_move_status}{RESET}"
    line_auto_move = pad_to_inner_width(f"{BOLD}{GREEN}Auto Move      :{RESET} {line_auto_move_content}", INNER_WIDTH)

    # Auto Play line (new line)
    line_auto_play_content = f"{BOLD}{YELLOW}{auto_play_status}{RESET}"
    line_auto_play = pad_to_inner_width(f"{BOLD}{GREEN}Auto Play      :{RESET} {line_auto_play_content}", INNER_WIDTH)

    # Max Games Limit line
    line_max_games_content = f"{BOLD}{YELLOW}{max_games_limit_display}{RESET}"
    line_max_games = pad_to_inner_width(f"{BOLD}{GREEN}Max Games Limit:{RESET} {line_max_games_content}", INNER_WIDTH)

    # Played games line
    line_played_content = f"{BOLD}{YELLOW}{stats.games_played}{RESET}"
    line_played = pad_to_inner_width(f"{BOLD}{GREEN}Played         :{RESET} {line_played_content}", INNER_WIDTH)

    # Win/Loss/Draw line
    win_loss_draw_str = f"{BOLD}{YELLOW}{stats.wins}{RESET} / {BOLD}{YELLOW}{stats.losses}{RESET} / {BOLD}{YELLOW}{stats.draws}{RESET}"
    line_win_loss_draw = pad_to_inner_width(f"{BOLD}{GREEN}Win/Loss/Draw  :{RESET} {win_loss_draw_str}", INNER_WIDTH)

    # Win Rate line
    line_win_rate_content = f"{BOLD}{YELLOW}{stats.win_rate:.2f}%{RESET}"
    line_win_rate = pad_to_inner_width(f"{BOLD}{GREEN}Win Rate       :{RESET} {line_win_rate_content}", INNER_WIDTH)

    # Avg Move Time line
    line_avg_move_content = f"{BOLD}{YELLOW}{stats.avg_move_time:.2f}s{RESET}"
    line_avg_move = pad_to_inner_width(f"{BOLD}{GREEN}Avg Move       :{RESET} {line_avg_move_content}", INNER_WIDTH)

    # Construct the HUD string with colors
    hud = f"""{BOLD}{BLUE}╔════════════════════════════════╗{RESET}
{BOLD}{BLUE}║{RESET} {line_nickname}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_elo}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}╠────────────────────────────────╣{RESET}
{BOLD}{BLUE}║{RESET} {line_auto_move}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_auto_play}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_max_games}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_played}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_win_loss_draw}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_win_rate}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}║{RESET} {line_avg_move}{BOLD}{BLUE}║{RESET}
{BOLD}{BLUE}╚════════════════════════════════╝{RESET}"""
    print(hud)

    print("Log:")
    for log_line in stats.log_history:
        print(log_line)

    # Add empty lines to push up the content if log history is less than 10
    for _ in range(10 - len(stats.log_history)):
        print()

def get_credentials():
    username = ""
    password = ""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                username = lines[0].strip()
                password = lines[1].strip()
    
    if not username or not password:
        print("Credentials not found or incomplete. Please enter them.")
        username = input("Enter Chess.com username: ")
        password = input("Enter Chess.com password: ")
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(f"{username}\n{password}\n")
        print(f"Credentials saved to {CREDENTIALS_FILE}")
    
    return username, password

def main():
    """
    Main function to run the chess assistant.
    """
    parser = argparse.ArgumentParser(description="Chess.com assistant.")
    parser.add_argument("--mode", choices=["Bullet", "Blitz", "Rapid"], help="Game mode.")
    parser.add_argument("--headless", type=bool, help="Run in headless mode.")
    parser.add_argument("--engine-depth", type=int, help="Engine search depth.")
    parser.add_argument("--auto-move", type=bool, help="Enable auto-move.")
    
    
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        config["play"] = {
            "mode": "Blitz",
            "headless": "false",
            "engine_depth": "15",
            "auto_move": "false",
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
        print("config.ini not found. A new one has been created. Please fill it out and run the script again.")
        sys.exit(0)

    config.read("config.ini")

    # Manually parse config values to handle inline comments
    config_mode = _parse_config_value(config.get("play", "mode"))
    config_headless = _parse_config_value(config.get("play", "headless")).lower() == 'true'
    config_engine_depth = int(_parse_config_value(config.get("play", "engine_depth")))
    config_auto_move = _parse_config_value(config.get("play", "auto_move")).lower() == 'true'
    config_auto_play = _parse_config_value(config.get("play", "auto_play")).lower() == 'true'
    config_num_games = int(_parse_config_value(config.get("play", "num_games")))

    # Override config with CLI args
    if args.mode:
        config.set("play", "mode", args.mode)
    else:
        config.set("play", "mode", config_mode) # Set parsed value if not overridden by CLI

    if args.headless is not None:
        config.set("play", "headless", str(args.headless))
    else:
        config.set("play", "headless", str(config_headless))

    if args.engine_depth is not None:
        config.set("play", "engine_depth", str(args.engine_depth))
    else:
        config.set("play", "engine_depth", str(config_engine_depth))

    if args.auto_move is not None:
        config.set("play", "auto_move", str(args.auto_move))
    else:
        config.set("play", "auto_move", str(config_auto_move))
    
    config.set("play", "auto_play", str(config_auto_play))
    config.set("play", "num_games", str(config_num_games))

    log_level = logging.DEBUG if args.debug else logging.INFO

    # Initialize GameStats
    stats = GameStats()
    stats.auto_move_enabled = config_auto_move
    stats.auto_play_enabled = config_auto_play
    stats.max_games_limit = config_num_games

    # Custom logging handler to capture INFO messages for HUD
    class HUDLogHandler(logging.Handler):
        def __init__(self, stats_obj, config_obj):
            super().__init__()
            self.stats = stats_obj
            self.config = config_obj

        def emit(self, record):
            if record.levelno >= logging.INFO:
                self.stats.add_log(self.format(record))
                # Refresh HUD and log after every new log entry
                display_hud_and_log(self.stats, self.config)

    # Remove default handlers and add custom handler
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    hud_handler = HUDLogHandler(stats, config) # Pass config here
    formatter = logging.Formatter("%(message)s") # Only message, timestamp handled by add_log
    hud_handler.setFormatter(formatter)
    logging.root.addHandler(hud_handler)
    logging.root.setLevel(log_level)

    username, password = get_credentials()

    browser = ChessBrowser(config, stats)
    game = Game(config, browser, stats, lambda: display_hud_and_log(stats, config))

    try:
        browser.start()
        browser.login(username, password)
        stats.nickname = browser.nickname
        stats.current_elo = browser.current_elo
        stats.start_elo = browser.current_elo # Assuming start ELO is current ELO after login
        display_hud_and_log(stats, config)

        while True:
            if stats.max_games_limit != 0 and stats.games_played >= stats.max_games_limit:
                logging.info(f"Finished playing {stats.games_played} games as per num_games setting.")
                break

            stats.games_played += 1
            logging.info(f"Starting game {stats.games_played}...")
            # display_hud_and_log(stats, config) # This call is now handled by the HUDLogHandler

            browser.select_mode() # This needs to be called for each new game
            game.start() # This needs to be modified to return when game is over

            logging.info(f"Game {stats.games_played} finished.")
            # display_hud_and_log(stats, config) # This call is now handled by the HUDLogHandler

            if stats.auto_play_enabled:
                # Handle game over modal and click new game button
                if not handle_game_over_modal(browser, config_mode, stats, config): # New function
                    logging.info("Could not find game over modal or new game button. Stopping auto-play.")
                    break
                logging.info("Starting next game...")
            else:
                logging.info("Auto-play is disabled. Stopping after one game.")
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        browser.close()

def handle_game_over_modal(browser_instance, game_mode, stats, config):
    try:
        # Wait for the game over modal to appear
        game_over_modal = browser_instance.page.wait_for_selector(".game-over-modal-content", timeout=10000)
        stats.add_log("Game over modal detected.")

        # Determine the text for the new game button based on the mode
        button_text = ""
        if game_mode.lower() == "bullet":
            button_text = "New 1 min"
        elif game_mode.lower() == "blitz":
            button_text = "New 3 min"
        elif game_mode.lower() == "rapid":
            button_text = "New 10 min"
        else:
            logging.warning(f"Unknown game mode: {game_mode}. Cannot determine new game button text.")
            return False

        # Click the new game button within the modal
        new_game_button_selector = f"button:has-text('{button_text}')"
        
        # Add random delay before starting a new game
        delay = random.randint(10, 30)
        stats.add_log(f"Waiting for {delay} seconds before starting a new game...")
        time.sleep(delay)

        stats.add_log(f"Attempting to click new game button: {new_game_button_selector}")
        browser_instance.page.click(new_game_button_selector, timeout=5000)
        stats.add_log(f"Successfully clicked {button_text} button.")
        return True
    except Exception as e:
        logging.error(f"Error handling game over modal: {e}")
        return False


if __name__ == "__main__":
    main()