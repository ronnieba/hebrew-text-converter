import pyperclip
from pynput import keyboard
import time
import threading
import sys
import os
from datetime import datetime
import logging
from settings_manager import settings_manager

# הגדרת לוגים
def setup_logging():
    """מגדיר את מערכת הלוגים"""
    log_level = settings_manager.get_setting("logging", "level", "INFO")
    log_to_file = settings_manager.get_setting("logging", "log_to_file", True)
    
    handlers = [logging.StreamHandler()]
    if log_to_file:
        handlers.append(logging.FileHandler('hebrew_converter.log', encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

# 1. הגדרת מפת המיפוי (אנגלית לעברית)
HEB_QWERTY_MAP = {
    # שורה עליונה (מספרים וסימנים)
    '`': ';', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
    '6': '6', '7': '7', '8': '8', '9': '9', '0': '0', '-': '-',
    '=': '=',
    # שורת האותיות העליונה
    'q': '/', 'w': "'", 'e': 'ק', 'r': 'ר', 't': 'א', 'y': 'ט',
    'u': 'ו', 'i': 'ן', 'o': 'ם', 'p': 'פ', '[': ']', ']': '[',
    '\\\\': '\\\\',
    # שורת האותיות האמצעית (בית)
    'a': 'ש', 's': 'ד', 'd': 'ג', 'f': 'כ', 'g': 'ע', 'h': 'י',
    'j': 'ח', 'k': 'ל', 'l': 'ך', ';': 'ף', "'": ',',
    # שורת האותיות התחתונה
    'z': 'ז', 'x': 'ס', 'c': 'ב', 'v': 'ה', 'b': 'נ', 'n': 'מ',
    'm': 'צ', ',': 'ת', '.': 'ץ', '/': '.',
    # שורת הרווח
    ' ': ' '
}

# 2. אתחול בקר המקלדת לשליחת לחיצות
keyboard_controller = keyboard.Controller()

# משתנים גלובליים
conversion_history = []
hotkey_listener = None

# 3. פונקציה שבודקת אם הטקסט כבר בעברית
def is_hebrew_text(text):
    """בודק אם הטקסט מכיל אותיות עבריות."""
    hebrew_chars = 'אבגדהוזחטסעפצקרשתךםןףץ'
    return any(char in hebrew_chars for char in text)

# 4. פונקציית ההמרה
def convert_text(text):
    """ממיר טקסט אנגלי לעברית לפי המיפוי."""
    converted_chars = []
    for char in text:
        if 'A' <= char <= 'Z':
            # אם האות גדולה (CAPS LOCK), השאר אותה
            converted_chars.append(char)
        else:
            # נסה להמיר. אם אין במיפוי, השאר את התו המקורי
            converted_chars.append(HEB_QWERTY_MAP.get(char, char))
    return "".join(converted_chars)

# 5. הפונקציה הראשית שתופעל על ידי ה-Hotkey
def do_conversion_action():
    """מבצע את כל הפעולה: העתק, המר, הדבק."""
    logging.info("🔥 Hotkey activated... performing conversion.")
    
    # שלב 1: בצע "העתק" (Ctrl+C)
    with keyboard_controller.pressed(keyboard.Key.ctrl):
        keyboard_controller.press('c')
        keyboard_controller.release('c')
    
    # המתן רגע קט כדי שלוח העריכה יתעדכן
    time.sleep(0.1)

    # שלב 2: קרא את הטקסט מלוח העריכה
    try:
        text_to_convert = pyperclip.paste()
        if not text_to_convert:
            logging.warning("❌ No text selected or clipboard is empty.")
            return
        
        # בדוק אם הטקסט מכיל פקודות טרמינל (אם מופעל)
        if settings_manager.get_setting("conversion", "skip_terminal_commands", True):
            if any(word in text_to_convert.lower() for word in ['python', 'ps ', 'cmd', 'powershell', 'dir', 'ls', 'cd ']):
                logging.warning(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
                return
                
    except Exception as e:
        logging.error(f"❌ Error reading from clipboard: {e}")
        return

    # שלב 3: בדוק אם הטקסט כבר בעברית (אם מופעל)
    if settings_manager.get_setting("conversion", "auto_detect_hebrew", True):
        if is_hebrew_text(text_to_convert):
            logging.warning(f"⚠️ Text is already in Hebrew: '{text_to_convert}'")
            return
    
    # שלב 4: בצע את ההמרה
    converted_text = convert_text(text_to_convert)

    # שלב 5: כתוב את הטקסט המומר בחזרה ללוח
    pyperclip.copy(converted_text)
    time.sleep(0.1) # המתן לעדכון הלוח

    # שלב 6: בצע "הדבק" (Ctrl+V)
    with keyboard_controller.pressed(keyboard.Key.ctrl):
        keyboard_controller.press('v')
        keyboard_controller.release('v')

    logging.info(f"✅ Converted: '{text_to_convert}' -> '{converted_text}'")
    
    # הוסף להיסטוריה
    timestamp = datetime.now().strftime("%H:%M:%S")
    conversion_history.append((text_to_convert, converted_text, timestamp))
    
    # שמור רק את מספר המרות המוגדר
    history_size = settings_manager.get_setting("ui", "history_size", 50)
    if len(conversion_history) > history_size:
        conversion_history.pop(0)

# 6. פונקציית יציאה
def on_exit():
    """עוצר את ה-Listener וסוגר את הסקריפט."""
    logging.info("🚪 Exit hotkey pressed. Shutting down...")
    return False

# 7. פונקציות עזר
def show_status():
    """מציג סטטוס של התוכנה"""
    print("\n" + "="*50)
    print("ממיר עברית - סטטוס")
    print("="*50)
    print("✅ התוכנה פועלת ברקע")
    
    current_convert = settings_manager.get_hotkey("convert")
    current_exit = ", ".join(settings_manager.get_exit_hotkeys())
    
    print(f"\nמקש המרה: {current_convert}")
    print(f"מקשי יציאה: {current_exit}")
    print(f"מספר המרות: {len(conversion_history)}")
    
    if conversion_history:
        print("\nהמרות אחרונות:")
        for i, (original, converted, timestamp) in enumerate(conversion_history[-5:], 1):
            print(f"{i}. [{timestamp}] {original} -> {converted}")
    
    print("\n" + "="*50)

def show_settings():
    """מציג הגדרות נוכחיות"""
    print("\n" + "="*50)
    print("הגדרות ממיר עברית")
    print("="*50)
    
    # מקשי קיצור
    print("\nמקשי קיצור:")
    print(f"  המרה: {settings_manager.get_hotkey('convert')}")
    print(f"  יציאה: {', '.join(settings_manager.get_exit_hotkeys())}")
    
    # הגדרות המרה
    print("\nהגדרות המרה:")
    print(f"  זיהוי אוטומטי של עברית: {settings_manager.get_setting('conversion', 'auto_detect_hebrew', True)}")
    print(f"  דילוג על פקודות טרמינל: {settings_manager.get_setting('conversion', 'skip_terminal_commands', True)}")
    print(f"  שמירת אותיות רישיות: {settings_manager.get_setting('conversion', 'preserve_caps', True)}")
    
    # הגדרות ממשק
    print("\nהגדרות ממשק:")
    print(f"  הצגת מסך פתיחה: {settings_manager.get_setting('ui', 'show_splash', True)}")
    print(f"  משך מסך פתיחה: {settings_manager.get_setting('ui', 'splash_duration', 5)} שניות")
    print(f"  גודל היסטוריה: {settings_manager.get_setting('ui', 'history_size', 50)}")
    
    # הגדרות לוגים
    print("\nהגדרות לוגים:")
    print(f"  רמת לוגים: {settings_manager.get_setting('logging', 'level', 'INFO')}")
    print(f"  שמירה לקובץ: {settings_manager.get_setting('logging', 'log_to_file', True)}")
    
    print("\n" + "="*50)

def show_menu():
    """מציג תפריט ראשי"""
    while True:
        print("\n" + "="*50)
        print("ממיר עברית - תפריט ראשי")
        print("="*50)
        print("1. הצג סטטוס")
        print("2. הצג הגדרות")
        print("3. הגדר מקשי קיצור")
        print("4. הצג היסטוריית המרות")
        print("5. נקה היסטוריה")
        print("0. צא")
        
        choice = input("\nבחר אפשרות (0-5): ").strip()
        
        if choice == "1":
            show_status()
        elif choice == "2":
            show_settings()
        elif choice == "3":
            from simple_hotkey_configurator import SimpleHotkeyConfigurator
            configurator = SimpleHotkeyConfigurator()
            configurator.show_menu()
        elif choice == "4":
            show_conversion_history()
        elif choice == "5":
            clear_history()
        elif choice == "0":
            print("יציאה...")
            break
        else:
            print("אפשרות לא חוקית, נסה שוב.")

def show_conversion_history():
    """מציג את היסטוריית ההמרות"""
    print("\n" + "="*50)
    print("היסטוריית המרות")
    print("="*50)
    
    if conversion_history:
        for i, (original, converted, timestamp) in enumerate(conversion_history, 1):
            print(f"{i:3d}. [{timestamp}]")
            print(f"     מקורי: {original}")
            print(f"     מומר:  {converted}")
            print()
    else:
        print("אין המרות עדיין.")
    
    input("לחץ Enter לחזרה לתפריט...")

def clear_history():
    """מנקה את ההיסטוריה"""
    global conversion_history
    confirm = input("האם אתה בטוח שברצונך לנקות את ההיסטוריה? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', 'כן']:
        conversion_history.clear()
        print("ההיסטוריה נוקתה!")
    else:
        print("ניקוי ההיסטוריה בוטל.")

# 8. הגדרת והפעלת ה-Listener הגלובלי
def start_hotkey_listener():
    """מתחיל את מאזין המקשים"""
    global hotkey_listener
    
    logging.info("ממיר עברית פועל...")
    print("ממיר עברית פועל...")
    
    current_convert = settings_manager.get_hotkey("convert")
    current_exit = ", ".join(settings_manager.get_exit_hotkeys())
    
    print(f" - לחץ [{current_convert}] להמרת טקסט מסומן")
    print(f" - לחץ [{current_exit}] ליציאה")
    print(" - לחץ Ctrl+C לפתיחת תפריט")
    print("ממתין למקש קיצור...")

    # בנה את רשימת מקשי הקיצור
    hotkey_dict = {
        current_convert: do_conversion_action
    }
    
    # הוסף מקשי יציאה
    for exit_hotkey in settings_manager.get_exit_hotkeys():
        hotkey_dict[exit_hotkey] = on_exit

    # מאזין ללחיצות מקשים באופן גלובלי
    try:
        with keyboard.GlobalHotKeys(hotkey_dict) as h:
            hotkey_listener = h
            h.join()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        print("Please ensure you have necessary permissions.")

# 9. הפעלת האפליקציה
if __name__ == "__main__":
    try:
        # הגדר לוגים
        setup_logging()
        logging.info("Starting Hebrew Converter Simple Advanced...")
        
        # הצג הודעת פתיחה
        print("="*60)
        print("ממיר עברית - גרסה מתקדמת פשוטה")
        print("="*60)
        print("תוכנה זו מאפשרת להגדיר מקשי קיצור מותאמים אישית")
        print("להמרת טקסט עברי באותיות אנגליות לעברית אמיתית.")
        print("="*60)
        
        # הפעל את מאזין המקשים בת'רד נפרד
        hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
        hotkey_thread.start()
        
        # המתן קצת כדי שהמאזין יתחיל
        time.sleep(1)
        
        # הפעל תפריט אינטראקטיבי
        try:
            show_menu()
        except KeyboardInterrupt:
            print("\n\nיציאה מהתוכנה...")
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")