import json
import os
import logging
from config import SETTINGS_PATH, VOCAB_FILES

class UserDB:
    def __init__(self):
        self.users = {}
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        self.load_all()

    def load_all(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                    # Convert string keys back to integers for Telegram IDs
                    self.users = {int(k): v for k, v in raw.items()}
            except (json.JSONDecodeError, ValueError):
                logging.error("Settings file corrupted. Starting fresh.")
                self.users = {}
        else:
            # First time run: file doesn't exist yet
            self.users = {}
            logging.info("First run detected. Settings file will be created on first save.")

    def save_all(self):
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def get_user(self, uid):
        if uid not in self.users:
            # Create default profile for a new user
            self.users[uid] = {
                "modes": {"definition": True, "test": True, "typing": True},
                "interval": 15,
                "is_active": True,
                "waiting_ack": False,
                "target_lang": "fr"
            }
            self.save_all()
        return self.users[uid]


    def update_user(self, uid, **kwargs):
        user = self.get_user(uid)
        for key, value in kwargs.items():
            user[key] = value
        self.save_all()

    def get_vocab(self, lang):
        path = VOCAB_FILES.get(lang, VOCAB_FILES['fr'])
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading vocab {lang}: {e}")
            return {}

# Global instance to use across the project
db = UserDB()