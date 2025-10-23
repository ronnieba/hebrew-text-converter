import pyperclip
from pynput import keyboard
import time
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from datetime import datetime
import logging

# הגדרת לוגים מפורטים
try:
    # מחק לוג ישן אם קיים
    if os.path.exists('hebrew_converter.log'):
        os.remove('hebrew_converter.log')
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('hebrew_converter.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info("לוגים הוגדרו בהצלחה")
except Exception as e:
    print(f"שגיאה בהגדרת לוגים: {e}")

# 1. הגדרת מפת המיפוי (אנגלית לעברית)
HEB_QWERTY_MAP = {
    # שורה עליונה (מספרים וסימנים)
    '`': ';', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
    '6': '6', '7': '7', '8': '8', '9': '9', '0': '0', '-': '-',
    '=': '=',
    # שורת האותיות העליונה
    'q': '/', 'w': "'", 'e': 'ק', 'r': 'ר', 't': 'א', 'y': 'ט',
    'u': 'ו', 'i': 'ן', 'o': 'ם', 'p': 'פ', '[': ']', ']': '[',
    '\\': '\\',
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
root_window = None

# 3. פונקציה שבודקת אם הטקסט כבר בעברית
def is_hebrew_text(text):
    """בודק אם הטקסט מכיל אותיות עבריות."""
    hebrew_chars = 'אבגדהוזחטיכלמנסעפצקרשתךםןףץ'
    return any(char in hebrew_chars for char in text)

# 4. פונקציית ההמרה
def convert_text(text):
    """ממיר טקסט אנגלי לעברית לפי המיפוי."""
    converted_chars = []
    for char in text:
        if 'A' <= char <= 'Z':
            # אם האות גדולה (CAPS LOCK), השאר אותה באנגלית
            converted_chars.append(char)
        elif char.lower() in HEB_QWERTY_MAP:
            # נסה להמיר אותיות קטנות. אם אין במיפוי, השאר את התו המקורי
            converted_chars.append(HEB_QWERTY_MAP[char.lower()])
        else:
            # אם אין במיפוי, השאר את התו המקורי
            converted_chars.append(char)
    return "".join(converted_chars)

# 4. פונקציה להמרה הפוכה (עברית לאנגלית)
def convert_text_reverse(text):
    """ממיר טקסט עברי לאנגלי לפי מיפוי QWERTY הפוך"""
    # מיפוי הפוך - עברית לאנגלית
    reverse_mapping = {
        'ק': 'e', 'ר': 'r', 'א': 't', 'ט': 'y', 'ו': 'u', 'ן': 'i', 'ם': 'o', 'פ': 'p',
        'ש': 'a', 'ד': 's', 'ג': 'd', 'כ': 'f', 'ע': 'g', 'י': 'h', 'ח': 'j', 'ל': 'k', 'ך': 'l',
        'ז': 'z', 'ס': 'x', 'ב': 'c', 'ה': 'v', 'נ': 'b', 'מ': 'n', 'צ': 'm', 'ת': ',', 'ץ': '.',
        ' ': ' ', '\n': '\n', '\t': '\t'
    }
    
    converted_chars = []
    for char in text:
        if char in reverse_mapping:
            converted_chars.append(reverse_mapping[char])
        else:
            # אם אין במיפוי, השאר את התו המקורי
            converted_chars.append(char)
    return "".join(converted_chars)

# 5. פונקציה לבדיקה אם הטקסט בעברית

# 6. פונקציה להמרה הפוכה (עברית לאנגלית)
def do_reverse_conversion_action():
    """מבצע את כל הפעולה: בחירת הכל, העתק, המרה הפוכה, הדבק."""
    logging.info("🔥 Hotkey Shift+Ctrl+] activated!")
    print("🔥 Hotkey Shift+Ctrl+] activated... performing reverse conversion.")
    
    try:
        # שלב 1: בצע "בחירת הכל" (Ctrl+A)
        logging.info("📝 Step 1: Selecting all text (Ctrl+A)")
        print("📝 Step 1: Selecting all text (Ctrl+A)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x41))  # VK_A
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x41))
        
        # המתן רגע קט כדי שהבחירה תתעדכן
        time.sleep(0.3)
        
        # שלב 2: בצע "העתק" (Ctrl+C)
        logging.info("📋 Step 2: Copying text (Ctrl+C)")
        print("📋 Step 2: Copying text (Ctrl+C)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x43))  # VK_C
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x43))
        
        # המתן רגע קט כדי שלוח העריכה יתעדכן
        time.sleep(0.3)

        # שלב 3: קרא את הטקסט מלוח העריכה
        logging.info("📖 Step 3: Reading from clipboard")
        print("📖 Step 3: Reading from clipboard")
        try:
            text_to_convert = pyperclip.paste()
            logging.info(f"📄 Clipboard content: '{text_to_convert}'")
            if not text_to_convert:
                logging.warning("❌ No text selected or clipboard is empty.")
                print("❌ No text selected or clipboard is empty.")
                return
            
            print(f"📄 Original text: '{text_to_convert}'")
            
        except Exception as e:
            logging.error(f"❌ Error reading from clipboard: {e}")
            print(f"❌ Error reading from clipboard: {e}")
            return

        # שלב 4: בדוק אם הטקסט מכיל פקודות טרמינל או דברים לא רלוונטיים
        if any(word in text_to_convert.lower() for word in ['python', 'ps ', 'cmd', 'powershell', 'dir', 'ls', 'cd ']):
            logging.warning(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            print(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            return
            
        # שלב 5: בדוק אם הטקסט כבר באנגלית
        if not is_hebrew_text(text_to_convert):
            logging.warning(f"⚠️ Text is already in English: '{text_to_convert}'")
            print(f"⚠️ Text is already in English: '{text_to_convert}'")
            return
        
        # שלב 6: בצע את ההמרה הפוכה
        logging.info("🔄 Step 4: Converting text (Hebrew to English)")
        print("🔄 Step 4: Converting text (Hebrew to English)")
        converted_text = convert_text_reverse(text_to_convert)
        logging.info(f"✨ Converted text: '{converted_text}'")
        print(f"✨ Converted text: '{converted_text}'")

        # שלב 7: כתוב את הטקסט המומר בחזרה ללוח
        logging.info("📝 Step 5: Copying converted text to clipboard")
        print("📝 Step 5: Copying converted text to clipboard")
        pyperclip.copy(converted_text)
        time.sleep(0.3) # המתן לעדכון הלוח

        # שלב 8: בצע "בחירת הכל" שוב (Ctrl+A) כדי שההדבקה תחליף את כל הטקסט
        logging.info("📝 Step 6: Selecting all text again (Ctrl+A)")
        print("📝 Step 6: Selecting all text again (Ctrl+A)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x41))  # VK_A
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x41))
        
        # המתן רגע קט כדי שהבחירה תתעדכן
        time.sleep(0.3)

        # שלב 9: בצע "הדבק" (Ctrl+V)
        logging.info("📋 Step 7: Pasting converted text (Ctrl+V)")
        print("📋 Step 7: Pasting converted text (Ctrl+V)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x56))  # VK_V
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x56))

        # המתן רגע קט כדי שההדבקה תתעדכן
        time.sleep(0.3)

        # שלב 10: שנה שפת הקלדה לאנגלית (Alt+Shift)
        logging.info("🌐 Step 8: Switching to English keyboard (Alt+Shift)")
        print("🌐 Step 8: Switching to English keyboard (Alt+Shift)")
        with keyboard_controller.pressed(keyboard.Key.alt):
            keyboard_controller.press(keyboard.Key.shift)
            keyboard_controller.release(keyboard.Key.shift)
            keyboard_controller.release(keyboard.Key.alt)

        # המתן רגע קט
        time.sleep(0.2)

        logging.info(f"✅ Reverse conversion completed: '{text_to_convert}' → '{converted_text}'")
        print(f"✅ Reverse conversion completed: '{text_to_convert}' → '{converted_text}'")
        
        # הוסף להיסטוריה
        timestamp = datetime.now().strftime("%H:%M:%S")
        conversion_history.append((text_to_convert, converted_text, timestamp))
        
        # שמור רק את 50 המרות האחרונות
        if len(conversion_history) > 50:
            conversion_history.pop(0)
            
    except Exception as e:
        logging.error(f"❌ Error during reverse conversion: {e}")
        print(f"❌ Error during reverse conversion: {e}")

# 5. הפונקציה הראשית שתופעל על ידי ה-Hotkey
def do_conversion_action():
    """מבצע את כל הפעולה: בחירת הכל, העתק, המר, הדבק."""
    logging.info("🔥 Hotkey Shift+Ctrl+[ activated!")
    print("🔥 Hotkey Shift+Ctrl+[ activated... performing conversion.")
    
    try:
        # שלב 1: בצע "בחירת הכל" (Ctrl+A)
        logging.info("📝 Step 1: Selecting all text (Ctrl+A)")
        print("📝 Step 1: Selecting all text (Ctrl+A)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x41))  # VK_A
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x41))
        
        # המתן רגע קט כדי שהבחירה תתעדכן
        time.sleep(0.3)
        
        # שלב 2: בצע "העתק" (Ctrl+C)
        logging.info("📋 Step 2: Copying text (Ctrl+C)")
        print("📋 Step 2: Copying text (Ctrl+C)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x43))  # VK_C
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x43))
        
        # המתן רגע קט כדי שלוח העריכה יתעדכן
        time.sleep(0.3)

        # שלב 3: קרא את הטקסט מלוח העריכה
        logging.info("📖 Step 3: Reading from clipboard")
        print("📖 Step 3: Reading from clipboard")
        try:
            text_to_convert = pyperclip.paste()
            logging.info(f"📄 Clipboard content: '{text_to_convert}'")
            if not text_to_convert:
                logging.warning("❌ No text selected or clipboard is empty.")
                print("❌ No text selected or clipboard is empty.")
                return
            
            print(f"📄 Original text: '{text_to_convert}'")
            
        except Exception as e:
            logging.error(f"❌ Error reading from clipboard: {e}")
            print(f"❌ Error reading from clipboard: {e}")
            return

        # שלב 4: בדוק אם הטקסט מכיל פקודות טרמינל או דברים לא רלוונטיים
        if any(word in text_to_convert.lower() for word in ['python', 'ps ', 'cmd', 'powershell', 'dir', 'ls', 'cd ']):
            logging.warning(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            print(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            return
            
        # שלב 5: בדוק אם הטקסט כבר בעברית
        if is_hebrew_text(text_to_convert):
            logging.warning(f"⚠️ Text is already in Hebrew: '{text_to_convert}'")
            print(f"⚠️ Text is already in Hebrew: '{text_to_convert}'")
            return
        
        # שלב 6: בצע את ההמרה
        logging.info("🔄 Step 4: Converting text")
        print("🔄 Step 4: Converting text")
        converted_text = convert_text(text_to_convert)
        logging.info(f"✨ Converted text: '{converted_text}'")
        print(f"✨ Converted text: '{converted_text}'")

        # שלב 7: כתוב את הטקסט המומר בחזרה ללוח
        logging.info("📝 Step 5: Copying converted text to clipboard")
        print("📝 Step 5: Copying converted text to clipboard")
        pyperclip.copy(converted_text)
        time.sleep(0.3) # המתן לעדכון הלוח

        # שלב 8: בצע "בחירת הכל" שוב (Ctrl+A) כדי שההדבקה תחליף את כל הטקסט
        logging.info("📝 Step 6: Selecting all text again (Ctrl+A)")
        print("📝 Step 6: Selecting all text again (Ctrl+A)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x41))  # VK_A
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x41))
        
        # המתן רגע קט כדי שהבחירה תתעדכן
        time.sleep(0.3)

        # שלב 9: בצע "הדבק" (Ctrl+V)
        logging.info("📋 Step 7: Pasting converted text (Ctrl+V)")
        print("📋 Step 7: Pasting converted text (Ctrl+V)")
        with keyboard_controller.pressed(keyboard.Key.ctrl):
            keyboard_controller.press(keyboard.KeyCode.from_vk(0x56))  # VK_V
            keyboard_controller.release(keyboard.KeyCode.from_vk(0x56))

        # המתן רגע קט כדי שההדבקה תתעדכן
        time.sleep(0.3)

        # שלב 10: שנה שפת הקלדה לעברית (Alt+Shift)
        logging.info("🌐 Step 8: Switching to Hebrew keyboard (Alt+Shift)")
        print("🌐 Step 8: Switching to Hebrew keyboard (Alt+Shift)")
        with keyboard_controller.pressed(keyboard.Key.alt):
            keyboard_controller.press(keyboard.Key.shift)
            keyboard_controller.release(keyboard.Key.shift)
            keyboard_controller.release(keyboard.Key.alt)

        # המתן רגע קט
        time.sleep(0.2)

        logging.info(f"✅ Conversion completed: '{text_to_convert}' → '{converted_text}'")
        print(f"✅ Conversion completed: '{text_to_convert}' → '{converted_text}'")
        
        # הוסף להיסטוריה
        timestamp = datetime.now().strftime("%H:%M:%S")
        conversion_history.append((text_to_convert, converted_text, timestamp))
        
        # שמור רק את 50 המרות האחרונות
        if len(conversion_history) > 50:
            conversion_history.pop(0)
            
    except Exception as e:
        logging.error(f"❌ Error during conversion: {e}")
        print(f"❌ Error during conversion: {e}")

# 6. פונקציית יציאה
def on_exit():
    """עוצר את ה-Listener וסוגר את הסקריפט."""
    print("🚪 Exit hotkey pressed. Shutting down...")
    icon.stop()
    return False  # מחזיר False כדי לעצור את הלולאה של ה-Listener

# 7. פונקציות עבור ה-Tray Icon
def show_splash_screen():
    """מציג splash screen עם לוגו וקרדיטים"""
    try:
        print("מציג splash screen...")
        splash = tk.Tk()
        splash.title("ממיר עברית")
        splash.geometry("500x400")
        splash.resizable(False, False)
        
        # מרכז את החלון
        splash.eval('tk::PlaceWindow . center')
        
        # רקע כחול
        splash.configure(bg='#0066cc')
        
        # כותרת ראשית
        title_label = tk.Label(splash, text="ממיר עברית", 
                              font=("Arial", 24, "bold"), 
                              fg="white", bg='#0066cc')
        title_label.pack(pady=20)
        
        # לוגו פשוט (מעגל עם טקסט)
        logo_frame = tk.Frame(splash, bg='#0066cc')
        logo_frame.pack(pady=20)
        
        # צור לוגו פשוט
        logo_canvas = tk.Canvas(logo_frame, width=100, height=100, bg='#0066cc', highlightthickness=0)
        logo_canvas.pack()
        
        # צור מעגל כחול עם מסגרת לבנה
        logo_canvas.create_oval(10, 10, 90, 90, fill='#004080', outline='white', width=3)
        
        # כתוב "עב" במרכז
        logo_canvas.create_text(50, 50, text="עב", fill='white', font=("Arial", 32, "bold"))
        
        # הודעה
        message_label = tk.Label(splash, text="מתחיל ממיר טקסט עברי...", 
                               font=("Arial", 12), 
                               fg="white", bg='#0066cc')
        message_label.pack(pady=10)
        
        # סטטוס
        status_label = tk.Label(splash, text="לחץ Shift+Ctrl+[ לעברית, Shift+Ctrl+] לאנגלית",
                              font=("Arial", 10),
                              fg="lightblue", bg='#0066cc')
        status_label.pack(pady=5)
        
        # קרדיטים
        credits_label = tk.Label(splash, text="נכתב ע\"י AI ורוני בן-אבי", 
                               font=("Arial", 10, "italic"), 
                               fg="lightgray", bg='#0066cc')
        credits_label.pack(pady=10)
        
        # גרסה
        version_label = tk.Label(splash, text="גרסה 1.05 אוקטובר 2025", 
                               font=("Arial", 9), 
                               fg="lightgray", bg='#0066cc')
        version_label.pack(pady=5)
        
        # סגור אחרי 5 שניות
        splash.after(5000, splash.destroy)
        splash.mainloop()
        print("Splash screen נסגר.")
    except Exception as e:
        print(f"שגיאה ב-splash screen: {e}")

def create_root_window():
    """יוצר חלון ראשי נסתר עבור Toplevel windows"""
    global root_window
    try:
        if root_window is None:
            root_window = tk.Tk()
            root_window.withdraw()  # הסתר את החלון הראשי
            print("חלון ראשי נוצר.")
    except Exception as e:
        print(f"שגיאה ביצירת חלון ראשי: {e}")

def create_image():
    """יוצר אייקון טוב יותר עבור ה-tray"""
    try:
        width = 64
        height = 64
        
        # צור תמונה עם רקע כחול בהיר
        image = Image.new('RGBA', (width, height), (0, 100, 200, 255))
        dc = ImageDraw.Draw(image)
        
        # צור מסגרת לבנה
        dc.ellipse((2, 2, 61, 61), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
        
        # צור רקע כחול בתוך המסגרת
        dc.ellipse((6, 6, 57, 57), fill=(0, 100, 200, 255))
        
        # כתוב "עב" בעברית גדולה
        dc.text((20, 18), "עב", fill=(255, 255, 255, 255))
        
        return image
    except Exception as e:
        print(f"שגיאה ביצירת אייקון: {e}")
        # אייקון ברירת מחדל
        return Image.new('RGB', (64, 64), "blue")

def show_settings():
    """מציג חלון הגדרות פשוט"""
    try:
        print("פותח חלון הגדרות...")
        
        def create_settings_window():
            try:
                # יצור חלון חדש
                settings_window = tk.Tk()
                settings_window.title("ממיר עברית - הגדרות")
                settings_window.geometry("500x400")
                settings_window.resizable(False, False)
                
                # מרכז את החלון
                settings_window.eval('tk::PlaceWindow . center')
                
                # כותרת
                title_label = tk.Label(settings_window, text="ממיר עברית - הגדרות", 
                                      font=("Arial", 16, "bold"))
                title_label.pack(pady=15)
                
                # מידע על מקשי הקיצור
                hotkey_frame = tk.LabelFrame(settings_window, text="מקשי קיצור", font=("Arial", 12, "bold"))
                hotkey_frame.pack(pady=10, padx=20, fill="x")
                
                tk.Label(hotkey_frame, text="Shift+Ctrl+[ - המרת טקסט אנגלי לעברית", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                tk.Label(hotkey_frame, text="Shift+Ctrl+] - המרת טקסט עברי לאנגלית", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                tk.Label(hotkey_frame, text="Alt+Q או Ctrl+Shift+Q - יציאה", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                
                # סטטיסטיקות
                stats_frame = tk.LabelFrame(settings_window, text="סטטיסטיקות", font=("Arial", 12, "bold"))
                stats_frame.pack(pady=10, padx=20, fill="x")
                
                tk.Label(stats_frame, text=f"סה\"כ המרות: {len(conversion_history)}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                
                # היסטוריה
                if conversion_history:
                    history_frame = tk.LabelFrame(settings_window, text="המרות אחרונות", font=("Arial", 12, "bold"))
                    history_frame.pack(pady=10, padx=20, fill="both", expand=True)
                    
                    history_text = tk.Text(history_frame, height=8, width=50, font=("Arial", 9))
                    history_text.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    for i, (original, converted, timestamp) in enumerate(conversion_history[-5:], 1):
                        history_text.insert(tk.END, f"{i}. [{timestamp}] {original} → {converted}\n")
                    
                    history_text.config(state=tk.DISABLED)
                
                # כפתור סגירה
                tk.Button(settings_window, text="סגור", 
                         command=settings_window.destroy, font=("Arial", 12)).pack(pady=15)
                
                print("חלון הגדרות נפתח.")
                
                # הפעל את החלון
                settings_window.mainloop()
                
            except Exception as e:
                print(f"שגיאה ביצירת חלון הגדרות: {e}")
        
        # הפעל את החלון בת'רד נפרד
        settings_thread = threading.Thread(target=create_settings_window, daemon=True)
        settings_thread.start()
        
    except Exception as e:
        print(f"שגיאה בחלון הגדרות: {e}")

def show_logs():
    """מציג חלון עם הלוגים"""
    try:
        print("פותח חלון לוגים...")
        
        def create_logs_window():
            try:
                # יצור חלון חדש
                logs_window = tk.Tk()
                logs_window.title("ממיר עברית - לוגים")
                logs_window.geometry("800x600")
                logs_window.resizable(True, True)
                
                # מרכז את החלון
                logs_window.eval('tk::PlaceWindow . center')
                
                # כותרת
                title_label = tk.Label(logs_window, text="ממיר עברית - לוגים", 
                                      font=("Arial", 16, "bold"))
                title_label.pack(pady=15)
                
                # אזור טקסט עם scroll
                logs_text = scrolledtext.ScrolledText(logs_window, height=30, width=90, font=("Consolas", 9))
                logs_text.pack(fill="both", expand=True, padx=20, pady=10)
                
                # קרא את קובץ הלוגים
                try:
                    if os.path.exists('hebrew_converter.log'):
                        with open('hebrew_converter.log', 'r', encoding='utf-8') as f:
                            log_content = f.read()
                            logs_text.insert(tk.END, log_content)
                    else:
                        logs_text.insert(tk.END, "קובץ הלוגים לא נמצא.")
                except Exception as e:
                    logs_text.insert(tk.END, f"שגיאה בקריאת הלוגים: {e}")
                
                logs_text.config(state=tk.DISABLED)
                
                # כפתור סגירה
                tk.Button(logs_window, text="סגור", 
                         command=logs_window.destroy, font=("Arial", 12)).pack(pady=15)
                
                print("חלון לוגים נפתח.")
                
                # הפעל את החלון
                logs_window.mainloop()
                
            except Exception as e:
                print(f"שגיאה ביצירת חלון לוגים: {e}")
        
        # הפעל את החלון בת'רד נפרד
        logs_thread = threading.Thread(target=create_logs_window, daemon=True)
        logs_thread.start()
        
    except Exception as e:
        print(f"שגיאה בחלון לוגים: {e}")

def show_status():
    """מציג חלון סטטוס פשוט"""
    try:
        print("פותח חלון סטטוס...")
        
        def create_status_window():
            try:
                # יצור חלון חדש
                status_window = tk.Tk()
                status_window.title("ממיר עברית - סטטוס")
                status_window.geometry("500x400")
                status_window.resizable(False, False)
                
                # מרכז את החלון
                status_window.eval('tk::PlaceWindow . center')
                
                # כותרת
                title_label = tk.Label(status_window, text="ממיר עברית - סטטוס", 
                                      font=("Arial", 16, "bold"))
                title_label.pack(pady=20)
                
                # סטטוס
                status_label = tk.Label(status_window, text="✅ התוכנה פועלת ברקע", 
                                      font=("Arial", 12), fg="green")
                status_label.pack(pady=10)
                
                # מידע על מקשי הקיצור
                hotkey_frame = tk.LabelFrame(status_window, text="מקשי קיצור", font=("Arial", 12, "bold"))
                hotkey_frame.pack(pady=10, padx=20, fill="x")
                
                tk.Label(hotkey_frame, text="Shift+Ctrl+[ - המרת טקסט אנגלי לעברית", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                tk.Label(hotkey_frame, text="Shift+Ctrl+] - המרת טקסט עברי לאנגלית", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                tk.Label(hotkey_frame, text="Alt+Q או Ctrl+Shift+Q - יציאה", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                
                # סטטיסטיקות
                stats_frame = tk.LabelFrame(status_window, text="סטטיסטיקות", font=("Arial", 12, "bold"))
                stats_frame.pack(pady=10, padx=20, fill="x")
                
                tk.Label(stats_frame, text=f"סה\"כ המרות: {len(conversion_history)}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                tk.Label(stats_frame, text=f"המרה אחרונה: {conversion_history[-1][2] if conversion_history else 'אין'}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
                
                # כפתורים
                button_frame = tk.Frame(status_window)
                button_frame.pack(pady=20)
                
                # כפתור לוגים
                logs_button = tk.Button(button_frame, text="הצג לוגים", 
                                      command=lambda: show_logs(), 
                                      font=("Arial", 12, "bold"),
                                      bg="blue", fg="white",
                                      width=12, height=2)
                logs_button.pack(side="left", padx=10)
                
                # כפתור סגירה גדול וברור
                close_button = tk.Button(button_frame, text="סגור", 
                                       command=status_window.destroy, 
                                       font=("Arial", 14, "bold"),
                                       bg="red", fg="white",
                                       width=10, height=2)
                close_button.pack(side="left", padx=10)
                
                print("כפתור סגור נוצר!")
                
                print("חלון סטטוס נפתח.")
                
                # הפעל את החלון
                status_window.mainloop()
                
            except Exception as e:
                print(f"שגיאה ביצירת חלון סטטוס: {e}")
        
        # הפעל את החלון בת'רד נפרד
        status_thread = threading.Thread(target=create_status_window, daemon=True)
        status_thread.start()
        
    except Exception as e:
        print(f"שגיאה בחלון סטטוס: {e}")

def quit_app():
    """יוצא מהאפליקציה"""
    print("יוצא מהאפליקציה...")
    icon.stop()
    sys.exit()

# 8. הגדרת ה-Tray Icon
icon = Icon("ממיר עברית", create_image(), 
           menu=Menu(
               MenuItem("הגדרות", show_settings),
               MenuItem("סטטוס", show_status),
               MenuItem("יציאה", quit_app)
           ))

# 9. הגדרת והפעלת ה-Listener הגלובלי
def start_hotkey_listener():
    """מתחיל את מאזין המקשים"""
    logging.info("ממיר עברית פועל...")
    print("ממיר עברית פועל...")
    print(" - לחץ [Shift+Ctrl+[] להמרת טקסט אנגלי לעברית")
    print(" - לחץ [Shift+Ctrl+]] להמרת טקסט עברי לאנגלית")
    print(" - ימין קליק על האייקון ליציאה")
    print("ממתין למקש קיצור...")

    # מאזין ללחיצות מקשים באופן גלובלי
    try:
        logging.info("Starting hotkey listener...")
        with keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+[': do_conversion_action,
                '<ctrl>+<shift>+]': do_reverse_conversion_action,
                '<ctrl>+<shift>+q': on_exit,
                '<alt>+q': on_exit
        }) as h:
            h.join()
    except Exception as e:
        logging.error(f"אירעה שגיאה: {e}")
        print(f"אירעה שגיאה: {e}")
        print("אנא וודא שיש לך הרשאות נדרשות.")

# 10. הפעלת האפליקציה
if __name__ == "__main__":
    try:
        print("מתחיל ממיר עברית...")
        logging.info("מתחיל ממיר עברית...")
        
        # הצג splash screen בהפעלה
        logging.info("מציג splash screen...")
        splash_thread = threading.Thread(target=show_splash_screen, daemon=True)
        splash_thread.start()
        
        # המתן קצת כדי שה-splash יופיע
        time.sleep(0.5)
        
        # הפעל את מאזין המקשים בת'רד נפרד
        logging.info("מתחיל hotkey listener...")
        hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
        hotkey_thread.start()
        
        # הפעל את ה-tray icon
        logging.info("מתחיל tray icon...")
        icon.run()
        
    except Exception as e:
        print(f"שגיאה קטלנית: {e}")
        logging.error(f"שגיאה קטלנית: {e}")
