import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get token from environment variable
TOKEN = os.getenv("BOT_TOKEN")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
VOCAB_FILES = {
    'fr': os.path.join(DATA_DIR, 'fr.json'),
    'en': os.path.join(DATA_DIR, 'en.json')
}
SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')