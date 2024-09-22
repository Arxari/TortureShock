import os
import time
import requests
from dotenv import load_dotenv
import curses

ENV_FILE = os.path.join(os.path.dirname(__file__), '.env')

def load_env():
    """Loads the API key and Shock ID from the .env file."""
    if os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
        api_key = os.getenv('SHOCK_API_KEY')
        shock_id = os.getenv('SHOCK_ID')
        return api_key, shock_id
    return None, None

def trigger_shock(api_key, shock_id, intensity, duration, shock_type='Shock'):
    """Sends a shock or vibrate command to the OpenShock API."""
    url = 'https://api.shocklink.net/2/shockers/control'
    headers = {
        'accept': 'application/json',
        'OpenShockToken': api_key,
        'Content-Type': 'application/json'
    }

    payload = {
        'shocks': [{
            'id': shock_id,
            'type': shock_type,
            'intensity': intensity,
            'duration': duration,
            'exclusive': True
        }],
        'customName': 'ShockControl'
    }

    try:
        response = requests.post(url=url, headers=headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def draw_bar(stdscr, value):
    """Draws the intensity bar and instructions."""
    height, width = stdscr.getmaxyx()
    max_bar_length = 50
    filled_length = int(value * max_bar_length / 100)

    bar = '#' * filled_length + '-' * (max_bar_length - filled_length)
    bar_text = f"[{bar}]"
    volume_text = f"Intensity: {value}%"
    instructions = "Press Up/Down to adjust intensity. Press q to quit."

    stdscr.clear()
    stdscr.addstr(height // 2 - 2, (width - len(instructions)) // 2, instructions)
    stdscr.addstr(height // 2, (width - len(volume_text)) // 2, volume_text)
    stdscr.addstr(height // 2 + 2, (width - len(bar_text)) // 2, bar_text)
    stdscr.refresh()

def main(stdscr):
    api_key, shock_id = load_env()

    if not api_key or not shock_id:
        print("API key or Shock ID not found. Please set up your .env file.")
        return

    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    intensity = 0
    last_shock_time = 0
    shock_interval = 1

    while True:
        draw_bar(stdscr, intensity)

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            intensity = min(100, intensity + 5)
        elif key == curses.KEY_DOWN:
            intensity = max(0, intensity - 5)

        current_time = time.time()
        if current_time - last_shock_time >= shock_interval and intensity > 0:
            if trigger_shock(api_key, shock_id, intensity, 300):
                last_shock_time = current_time

if __name__ == "__main__":
    curses.wrapper(main)
