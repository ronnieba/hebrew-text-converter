import pyperclip
from pynput import keyboard
import time
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import os
from datetime import datetime
import logging
import json

# הגדרת לוגים
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hebrew_converter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
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
settings_window = None
hotkey_settings_file = "hotkey_settings.json"

# הגדרות מקשי קיצור ברירת מחדל
DEFAULT_HOTKEYS = {
    "convert": "<ctrl>+<alt>+h",
    "exit1": "<ctrl>+<shift>+q", 
    "exit2": "<alt>+q"
}

# משתנים גלובליים למפתחות קיצור
current_hotkeys = DEFAULT_HOTKEYS.copy()
hotkey_listener = None

# 3. פונקציות לניהול מקשי קיצור
def load_hotkey_settings():
    """טוען הגדרות מקשי קיצור מקובץ"""
    global current_hotkeys
    try:
        if os.path.exists(hotkey_settings_file):
            with open(hotkey_settings_file, 'r', encoding='utf-8') as f:
                saved_hotkeys = json.load(f)
                current_hotkeys.update(saved_hotkeys)
                logging.info(f"Loaded hotkey settings: {current_hotkeys}")
        else:
            logging.info("No hotkey settings file found, using defaults")
    except Exception as e:
        logging.error(f"Error loading hotkey settings: {e}")
        current_hotkeys = DEFAULT_HOTKEYS.copy()

def save_hotkey_settings():
    """שומר הגדרות מקשי קיצור לקובץ"""
    try:
        with open(hotkey_settings_file, 'w', encoding='utf-8') as f:
            json.dump(current_hotkeys, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved hotkey settings: {current_hotkeys}")
    except Exception as e:
        logging.error(f"Error saving hotkey settings: {e}")

def validate_hotkey(hotkey_string):
    """בודק אם מקש קיצור תקין"""
    if not hotkey_string:
        return False, "מקש קיצור לא יכול להיות ריק"
    
    # בדיקה בסיסית של פורמט
    valid_modifiers = ['ctrl', 'alt', 'shift']
    parts = hotkey_string.lower().replace('<', '').replace('>', '').split('+')
    
    if len(parts) < 2:
        return False, "מקש קיצור חייב לכלול לפחות מודיפייר ומקש אחד"
    
    # בדוק מודיפיירים
    modifiers = parts[:-1]
    for mod in modifiers:
        if mod not in valid_modifiers:
            return False, f"מודיפייר לא תקין: {mod}"
    
    # בדוק שאין כפילויות
    if len(modifiers) != len(set(modifiers)):
        return False, "אין אפשרות להשתמש באותו מודיפייר פעמיים"
    
    return True, "תקין"

# 4. פונקציה שבודקת אם הטקסט כבר בעברית
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
        
        # בדוק אם הטקסט מכיל פקודות טרמינל או דברים לא רלוונטיים
        if any(word in text_to_convert.lower() for word in ['python', 'ps ', 'cmd', 'powershell', 'dir', 'ls', 'cd ']):
            logging.warning(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            return
            
    except Exception as e:
        logging.error(f"❌ Error reading from clipboard: {e}")
        return

    # שלב 3: בדוק אם הטקסט כבר בעברית
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
    
    # שמור רק את 50 המרות האחרונות
    if len(conversion_history) > 50:
        conversion_history.pop(0)

# 6. פונקציית יציאה
def on_exit():
    """עוצר את ה-Listener וסוגר את הסקריפט."""
    logging.info("🚪 Exit hotkey pressed. Shutting down...")
    icon.stop()
    return False  # מחזיר False כדי לעצור את הלולאה של ה-Listener

# 7. פונקציות עבור ה-Tray Icon
def show_splash_screen():
    """מציג splash screen בהפעלה"""
    try:
        logging.info("Showing splash screen...")
        splash = tk.Tk()
        splash.title("ממיר עברית")
        splash.geometry("400x200")
        splash.resizable(False, False)
        
        # מרכז את החלון
        splash.eval('tk::PlaceWindow . center')
        
        # רקע כחול
        splash.configure(bg='#0066cc')
        
        # כותרת
        title_label = tk.Label(splash, text="ממיר עברית", 
                              font=("Arial", 20, "bold"), 
                              fg="white", bg='#0066cc')
        title_label.pack(pady=30)
        
        # הודעה
        message_label = tk.Label(splash, text="מתחיל ממיר טקסט עברי...", 
                               font=("Arial", 12), 
                               fg="white", bg='#0066cc')
        message_label.pack(pady=10)
        
        # סטטוס
        status_label = tk.Label(splash, text="לחץ Ctrl+Alt+H להמרת טקסט", 
                              font=("Arial", 10), 
                              fg="lightblue", bg='#0066cc')
        status_label.pack(pady=5)
        
        # סגור אחרי 5 שניות
        splash.after(5000, splash.destroy)
        splash.mainloop()
        logging.info("Splash screen closed.")
    except Exception as e:
        logging.error(f"שגיאה ב-splash screen: {e}")

def create_image():
    """יוצר אייקון פשוט עבור ה-tray"""
    try:
        width = 64
        height = 64
        color1 = "blue"
        color2 = "white"
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        # השתמש בטקסט באנגלית במקום עברית
        dc.text((10, 20), "HE", fill=color2)
        dc.text((10, 40), "EN", fill=color2)
        
        return image
    except Exception as e:
        logging.error(f"שגיאה ביצירת אייקון: {e}")
        # אייקון ברירת מחדל
        return Image.new('RGB', (64, 64), "blue")

def close_settings_window():
    """סוגר את חלון ההגדרות"""
    try:
        global settings_window
        if settings_window:
            settings_window.destroy()
            settings_window = None
            logging.info("Settings window closed.")
    except Exception as e:
        logging.error(f"שגיאה בסגירת חלון הגדרות: {e}")

def show_settings():
    """מציג חלון הגדרות עם היסטוריית המרות"""
    global settings_window
    
    try:
        logging.info("Opening settings window...")
        
        # אם החלון כבר קיים, פשוט הרמה אותו
        if settings_window:
            try:
                settings_window.lift()
                settings_window.focus_force()
                return
            except:
                # אם יש בעיה עם החלון הקיים, אפס אותו
                settings_window = None
        
        settings_window = tk.Tk()
        settings_window.title("ממיר עברית - הגדרות")
        settings_window.geometry("700x600")
        settings_window.resizable(True, True)
        
        # מרכז את החלון
        settings_window.eval('tk::PlaceWindow . center')
        
        # כותרת
        title_label = tk.Label(settings_window, text="Hebrew Converter - Settings", 
                              font=("Tahoma", 16, "bold"))
        title_label.pack(pady=15)
        
        # הגדרות מקשי קיצור
        hotkey_frame = tk.LabelFrame(settings_window, text="הגדרות מקשי קיצור", font=("Tahoma", 10, "bold"))
        hotkey_frame.pack(pady=10, padx=20, fill="x")
        
        # משתנים למפתחות קיצור
        convert_hotkey_var = tk.StringVar(value=current_hotkeys["convert"])
        exit1_hotkey_var = tk.StringVar(value=current_hotkeys["exit1"])
        exit2_hotkey_var = tk.StringVar(value=current_hotkeys["exit2"])
        
        # תוויות ושדות קלט
        tk.Label(hotkey_frame, text="מקש המרה:", font=("Tahoma", 9)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        convert_entry = tk.Entry(hotkey_frame, textvariable=convert_hotkey_var, width=20, font=("Tahoma", 9))
        convert_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(hotkey_frame, text="מקש יציאה 1:", font=("Tahoma", 9)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        exit1_entry = tk.Entry(hotkey_frame, textvariable=exit1_hotkey_var, width=20, font=("Tahoma", 9))
        exit1_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(hotkey_frame, text="מקש יציאה 2:", font=("Tahoma", 9)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        exit2_entry = tk.Entry(hotkey_frame, textvariable=exit2_hotkey_var, width=20, font=("Tahoma", 9))
        exit2_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # הודעת עזרה
        help_label = tk.Label(hotkey_frame, 
                             text="דוגמאות: <ctrl>+<alt>+h, <shift>+<ctrl>+q, <alt>+q", 
                             font=("Tahoma", 8), fg="gray")
        help_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        
        # כפתור שמירה
        def save_hotkeys():
            global current_hotkeys
            new_convert = convert_hotkey_var.get().strip()
            new_exit1 = exit1_hotkey_var.get().strip()
            new_exit2 = exit2_hotkey_var.get().strip()
            
            # בדיקת תקינות
            is_valid, message = validate_hotkey(new_convert)
            if not is_valid:
                tk.messagebox.showerror("שגיאה", f"מקש המרה: {message}")
                return
                
            is_valid, message = validate_hotkey(new_exit1)
            if not is_valid:
                tk.messagebox.showerror("שגיאה", f"מקש יציאה 1: {message}")
                return
                
            is_valid, message = validate_hotkey(new_exit2)
            if not is_valid:
                tk.messagebox.showerror("שגיאה", f"מקש יציאה 2: {message}")
                return
            
            # עדכון המפתחות
            current_hotkeys["convert"] = new_convert
            current_hotkeys["exit1"] = new_exit1
            current_hotkeys["exit2"] = new_exit2
            
            # שמירה לקובץ
            save_hotkey_settings()
            
            # הודעה על הצלחה
            tk.messagebox.showinfo("הצלחה", "מקשי הקיצור נשמרו בהצלחה!\nיש להפעיל מחדש את התוכנה כדי שהשינויים ייכנסו לתוקף.")
            
        tk.Button(hotkey_frame, text="שמור מקשי קיצור", 
                 command=save_hotkeys, font=("Tahoma", 9)).grid(row=4, column=0, columnspan=2, pady=10)
        
        # היסטוריית המרות
        history_frame = tk.LabelFrame(settings_window, text="Conversion History", font=("Tahoma", 10, "bold"))
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # אזור טקסט עם scroll
        history_text = scrolledtext.ScrolledText(history_frame, height=15, width=70, font=("Tahoma", 9))
        history_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # הוסף את ההיסטוריה
        if conversion_history:
            for i, (original, converted, timestamp) in enumerate(conversion_history[-20:], 1):
                history_text.insert(tk.END, f"{i}. [{timestamp}]\n")
                history_text.insert(tk.END, f"   מקורי: {original}\n")
                history_text.insert(tk.END, f"   מומר: {converted}\n\n")
        else:
            history_text.insert(tk.END, "אין המרות עדיין. נסה להמיר טקסט!")
        
        history_text.config(state=tk.DISABLED)
        
        # כפתורים
        button_frame = tk.Frame(settings_window)
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Clear History", 
                 command=lambda: clear_history(history_text), font=("Tahoma", 9)).pack(side="left", padx=5)
        tk.Button(button_frame, text="Refresh", 
                 command=lambda: refresh_history(history_text), font=("Tahoma", 9)).pack(side="left", padx=5)
        tk.Button(button_frame, text="Close", 
                 command=close_settings_window, font=("Tahoma", 9)).pack(side="left", padx=5)
        
        # סגור את החלון כשסוגרים
        settings_window.protocol("WM_DELETE_WINDOW", close_settings_window)
        
        logging.info("Settings window opened successfully.")
        
    except Exception as e:
        logging.error(f"שגיאה בחלון הגדרות: {e}")
        print(f"שגיאה בחלון הגדרות: {e}")

def clear_history(text_widget):
    """מנקה את ההיסטוריה"""
    try:
        global conversion_history
        conversion_history.clear()
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "היסטוריה נוקתה!")
        text_widget.config(state=tk.DISABLED)
        logging.info("History cleared.")
    except Exception as e:
        logging.error(f"שגיאה בניקוי היסטוריה: {e}")

def refresh_history(text_widget):
    """מרענן את ההיסטוריה"""
    try:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        
        if conversion_history:
            for i, (original, converted, timestamp) in enumerate(conversion_history[-20:], 1):
                text_widget.insert(tk.END, f"{i}. [{timestamp}]\n")
                text_widget.insert(tk.END, f"   מקורי: {original}\n")
                text_widget.insert(tk.END, f"   מומר: {converted}\n\n")
        else:
            text_widget.insert(tk.END, "אין המרות עדיין. נסה להמיר טקסט!")
        
        text_widget.config(state=tk.DISABLED)
        logging.info("History refreshed.")
    except Exception as e:
        logging.error(f"שגיאה ברענון היסטוריה: {e}")

def close_status_window(status_window):
    """סוגר את חלון הסטטוס"""
    try:
        status_window.destroy()
        logging.info("Status window closed.")
    except Exception as e:
        logging.error(f"שגיאה בסגירת חלון סטטוס: {e}")

def show_status():
    """מציג חלון סטטוס"""
    try:
        logging.info("Opening status window...")
        status_window = tk.Tk()
        status_window.title("ממיר עברית - סטטוס")
        status_window.geometry("400x300")
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
        hotkey_label = tk.Label(status_window, text="מקשי קיצור:", 
                               font=("Arial", 11, "bold"))
        hotkey_label.pack(pady=(20, 5))
        
        tk.Label(status_window, text=f"{current_hotkeys['convert']} - המרת טקסט מסומן", 
                 font=("Arial", 10)).pack(pady=2)
        tk.Label(status_window, text=f"{current_hotkeys['exit1']} או {current_hotkeys['exit2']} - יציאה", 
                 font=("Arial", 10)).pack(pady=2)
        
        # סטטיסטיקות
        stats_label = tk.Label(status_window, text=f"מספר המרות: {len(conversion_history)}", 
                              font=("Arial", 10))
        stats_label.pack(pady=20)
        
        # כפתור סגירה
        tk.Button(status_window, text="סגור", 
                 command=lambda: close_status_window(status_window), font=("Arial", 10)).pack(pady=10)
        
        # סגור את החלון כשסוגרים
        status_window.protocol("WM_DELETE_WINDOW", lambda: close_status_window(status_window))
        
        logging.info("Status window opened successfully.")
        
    except Exception as e:
        logging.error(f"שגיאה בחלון סטטוס: {e}")

def quit_app():
    """יוצא מהאפליקציה"""
    logging.info("Quitting application...")
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
    global hotkey_listener
    logging.info("ממיר עברית פועל...")
    print("ממיר עברית פועל...")
    print(f" - לחץ [{current_hotkeys['convert']}] להמרת טקסט מסומן")
    print(f" - לחץ [{current_hotkeys['exit1']}] או [{current_hotkeys['exit2']}] ליציאה")
    print(" - ימין קליק על האייקון ליציאה")
    print("ממתין למקש קיצור...")

    # מאזין ללחיצות מקשים באופן גלובלי
    try:
        hotkey_dict = {
            current_hotkeys['convert']: do_conversion_action,
            current_hotkeys['exit1']: on_exit,
            current_hotkeys['exit2']: on_exit
        }
        
        hotkey_listener = keyboard.GlobalHotKeys(hotkey_dict)
        hotkey_listener.start()
        hotkey_listener.join()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        print("Please ensure you have necessary permissions.")

# 10. הפעלת האפליקציה
if __name__ == "__main__":
    try:
        logging.info("Starting Hebrew Converter...")
        
        # טען הגדרות מקשי קיצור
        load_hotkey_settings()
        
        # הצג splash screen בהפעלה
        splash_thread = threading.Thread(target=show_splash_screen, daemon=True)
        splash_thread.start()
        
        # המתן קצת כדי שה-splash יופיע
        time.sleep(0.5)
        
        # הפעל את מאזין המקשים בת'רד נפרד
        hotkey_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
        hotkey_thread.start()
        
        # הפעל את ה-tray icon
        icon.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
