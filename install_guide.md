# מדריך התקנה - ממיר עברית מתקדם

## הורדת הפרויקט

### אפשרות 1: הורדה ישירה
1. לחץ ימין על כל קובץ ב-Cursor
2. בחר "Download" או "Save As"
3. שמור את כל הקבצים בתיקייה חדשה

### אפשרות 2: העתקה ידנית
העתק את הקבצים הבאים לתיקייה חדשה:
- `settings_manager.py`
- `simple_hotkey_configurator.py`
- `hebrew_converter_simple_advanced.py`
- `hebrew_converter_advanced.py`
- `hotkey_settings_demo.py`
- `requirements.txt`
- `README_ADVANCED.md`

## התקנת התלויות

### Windows:
```cmd
pip install pyperclip pynput pystray Pillow
```

### macOS:
```bash
pip3 install pyperclip pynput pystray Pillow
```

### Linux:
```bash
pip3 install pyperclip pynput pystray Pillow
```

## הפעלה

### 1. בדיקת המערכת:
```bash
python3 hotkey_settings_demo.py
```

### 2. הגדרת מקשי קיצור:
```bash
python3 simple_hotkey_configurator.py
```

### 3. הפעלת הממיר המתקדם:
```bash
python3 hebrew_converter_simple_advanced.py
```

## פתרון בעיות

### בעיות הרשאות (Windows):
- הרץ את CMD כמנהל
- או השתמש ב-PowerShell

### בעיות הרשאות (macOS):
- עבור ל-System Preferences > Security & Privacy > Privacy > Accessibility
- הוסף את Terminal או Python לרשימה

### בעיות הרשאות (Linux):
- ודא שהמשתמש נמצא בקבוצת input
- או הרץ עם sudo (לא מומלץ)

## בדיקה מהירה

1. הרץ את הדמו:
```bash
python3 hotkey_settings_demo.py
```

2. שנה מקש קיצור:
```bash
python3 simple_hotkey_configurator.py
```

3. בדוק שההגדרות נשמרו:
```bash
python3 -c "from settings_manager import settings_manager; print('Convert:', settings_manager.get_hotkey('convert'))"
```

## קבצי הגדרות

ההגדרות נשמרות ב-`hebrew_converter_settings.json` - אתה יכול לערוך אותן ידנית אם תרצה.