import pyperclip
from pynput import keyboard
import time

# 1. הגדרת מפת המיפוי (אנגלית לעברית)
#    אותיות גדולות (CAPS) לא ממופות בכוונה, לפי הבקשה
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

# 3. פונקציה שבודקת אם הטקסט כבר בעברית
def is_hebrew_text(text):
    """
    בודק אם הטקסט מכיל אותיות עבריות.
    """
    hebrew_chars = 'אבגדהוזחטיכלמנסעפצקרשתךםןףץ'
    return any(char in hebrew_chars for char in text)

# 4. פונקציית ההמרה
def convert_text(text):
    """
    ממיר טקסט אנגלי לעברית לפי המיפוי,
    משאיר אותיות רישיות (CAPS) כפי שהן.
    """
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
    """
    מבצע את כל הפעולה: העתק, המר, הדבק.
    """
    print("🔥 Hotkey activated... performing conversion.")
    
    # שלב 1: בצע "העתק" (Ctrl+C)
    # אנחנו משתמשים ב"העתק" ולא ב"גזור" כי זה בטוח יותר.
    # אם טקסט מסומן, "הדבק" יחליף אותו, וזה משיג את אותה תוצאה.
    with keyboard_controller.pressed(keyboard.Key.ctrl):
        keyboard_controller.press('c')
        keyboard_controller.release('c')
    
    # המתן רגע קט כדי שלוח העריכה יתעדכן
    time.sleep(0.1)

    # שלב 2: קרא את הטקסט מלוח העריכה
    try:
        text_to_convert = pyperclip.paste()
        if not text_to_convert:
            print("❌ No text selected or clipboard is empty.")
            return
        
        # בדוק אם הטקסט מכיל פקודות טרמינל או דברים לא רלוונטיים
        if any(word in text_to_convert.lower() for word in ['python', 'ps ', 'cmd', 'powershell', 'dir', 'ls', 'cd ']):
            print(f"⚠️ Detected terminal command, skipping: '{text_to_convert[:50]}...'")
            return
            
    except Exception as e:
        print(f"❌ Error reading from clipboard: {e}")
        return

    # שלב 3: בדוק אם הטקסט כבר בעברית
    if is_hebrew_text(text_to_convert):
        print(f"⚠️ Text is already in Hebrew: '{text_to_convert}'")
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

    print(f"✅ Converted: '{text_to_convert}' -> '{converted_text}'")

# 6. פונקציית יציאה
def on_exit():
    """
    עוצר את ה-Listener וסוגר את הסקריפט.
    """
    print("🚪 Exit hotkey pressed. Shutting down...")
    return False  # מחזיר False כדי לעצור את הלולאה של ה-Listener

# 7. הגדרת והפעלת ה-Listener הגלובלי
print("Python LangOver script is running...")
print(f" - Press [Alt+H] to convert selected 'gibberish' text.")
print(f" - Press [Ctrl+Shift+Q] or [Alt+Q] to exit the script.")
print("Waiting for hotkey...")

# מאזין ללחיצות מקשים באופן גלובלי
# <alt>+h הוא מקש ההפעלה
# <ctrl>+<shift>+q או <alt>+q הם מקשי היציאה
try:
    with keyboard.GlobalHotKeys({
            '<alt>+h': do_conversion_action,
            '<ctrl>+<shift>+q': on_exit,
            '<alt>+q': on_exit
    }) as h:
        h.join()
except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure you have necessary permissions (e.g., Accessibility on macOS).")

print("Script terminated.")

