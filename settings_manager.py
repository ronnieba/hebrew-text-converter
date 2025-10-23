import json
import os
from typing import Dict, Any

class SettingsManager:
    """מנהל הגדרות עבור ממיר העברית"""
    
    def __init__(self, settings_file: str = "hebrew_converter_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "hotkeys": {
                "convert": "<ctrl>+<alt>+h",
                "exit": ["<ctrl>+<shift>+q", "<alt>+q"]
            },
            "conversion": {
                "auto_detect_hebrew": True,
                "skip_terminal_commands": True,
                "preserve_caps": True
            },
            "ui": {
                "show_splash": True,
                "splash_duration": 5,
                "history_size": 50
            },
            "logging": {
                "level": "INFO",
                "log_to_file": True
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """טוען הגדרות מקובץ JSON"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # מיזוג עם הגדרות ברירת מחדל עבור מפתחות חסרים
                return self._merge_settings(self.default_settings, settings)
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"שגיאה בטעינת הגדרות: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """שומר הגדרות לקובץ JSON"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"שגיאה בשמירת הגדרות: {e}")
            return False
    
    def _merge_settings(self, default: Dict, user: Dict) -> Dict:
        """ממזג הגדרות משתמש עם ברירת מחדל"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_hotkey(self, action: str) -> str:
        """מחזיר מקש קיצור לפעולה מסוימת"""
        return self.settings["hotkeys"].get(action, "")
    
    def get_exit_hotkeys(self) -> list:
        """מחזיר רשימת מקשי יציאה"""
        return self.settings["hotkeys"].get("exit", [])
    
    def set_hotkey(self, action: str, hotkey: str) -> bool:
        """מגדיר מקש קיצור חדש"""
        try:
            if action == "exit":
                # עבור יציאה, שמור כרשימה
                if isinstance(hotkey, str):
                    self.settings["hotkeys"]["exit"] = [hotkey]
                else:
                    self.settings["hotkeys"]["exit"] = hotkey
            else:
                self.settings["hotkeys"][action] = hotkey
            return self.save_settings()
        except Exception as e:
            print(f"שגיאה בהגדרת מקש קיצור: {e}")
            return False
    
    def get_setting(self, category: str, key: str, default=None):
        """מחזיר הגדרה ספציפית"""
        return self.settings.get(category, {}).get(key, default)
    
    def set_setting(self, category: str, key: str, value) -> bool:
        """מגדיר הגדרה ספציפית"""
        try:
            if category not in self.settings:
                self.settings[category] = {}
            self.settings[category][key] = value
            return self.save_settings()
        except Exception as e:
            print(f"שגיאה בהגדרת הגדרה: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """מחזיר הגדרות לברירת מחדל"""
        try:
            self.settings = self.default_settings.copy()
            return self.save_settings()
        except Exception as e:
            print(f"שגיאה באיפוס הגדרות: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """מחזיר את כל ההגדרות"""
        return self.settings.copy()

# יצירת מופע גלובלי
settings_manager = SettingsManager()