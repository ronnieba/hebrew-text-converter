import json
import os
from settings_manager import settings_manager

class SimpleHotkeyConfigurator:
    """ממשק פשוט להגדרת מקשי קיצור ללא GUI"""
    
    def __init__(self):
        self.available_hotkeys = [
            "<ctrl>+<alt>+h",
            "<ctrl>+<shift>+h", 
            "<alt>+h",
            "<ctrl>+h",
            "<f1>", "<f2>", "<f3>", "<f4>", "<f5>", "<f6>",
            "<f7>", "<f8>", "<f9>", "<f10>", "<f11>", "<f12>",
            "<ctrl>+<f1>", "<ctrl>+<f2>", "<ctrl>+<f3>", "<ctrl>+<f4>",
            "<ctrl>+<f5>", "<ctrl>+<f6>", "<ctrl>+<f7>", "<ctrl>+<f8>",
            "<ctrl>+<f9>", "<ctrl>+<f10>", "<ctrl>+<f11>", "<ctrl>+<f12>",
            "<alt>+<f1>", "<alt>+<f2>", "<alt>+<f3>", "<alt>+<f4>",
            "<alt>+<f5>", "<alt>+<f6>", "<alt>+<f7>", "<alt>+<f8>",
            "<alt>+<f9>", "<alt>+<f10>", "<alt>+<f11>", "<alt>+<f12>",
            "<ctrl>+<shift>+<f1>", "<ctrl>+<shift>+<f2>", "<ctrl>+<shift>+<f3>",
            "<ctrl>+<shift>+<f4>", "<ctrl>+<shift>+<f5>", "<ctrl>+<shift>+<f6>",
            "<ctrl>+<shift>+<f7>", "<ctrl>+<shift>+<f8>", "<ctrl>+<shift>+<f9>",
            "<ctrl>+<shift>+<f10>", "<ctrl>+<shift>+<f11>", "<ctrl>+<shift>+<f12>",
            "<ctrl>+<alt>+<f1>", "<ctrl>+<alt>+<f2>", "<ctrl>+<alt>+<f3>",
            "<ctrl>+<alt>+<f4>", "<ctrl>+<alt>+<f5>", "<ctrl>+<alt>+<f6>",
            "<ctrl>+<alt>+<f7>", "<ctrl>+<alt>+<f8>", "<ctrl>+<alt>+<f9>",
            "<ctrl>+<alt>+<f10>", "<ctrl>+<alt>+<f11>", "<ctrl>+<alt>+<f12>",
            "<ctrl>+<shift>+q", "<alt>+q", "<ctrl>+q", "<ctrl>+<alt>+q",
            "<ctrl>+<shift>+<alt>+q"
        ]
    
    def show_menu(self):
        """מציג תפריט הגדרת מקשי קיצור"""
        while True:
            print("\n" + "="*50)
            print("הגדרת מקשי קיצור - ממיר עברית")
            print("="*50)
            
            # הצג הגדרות נוכחיות
            current_convert = settings_manager.get_hotkey("convert")
            current_exit = settings_manager.get_exit_hotkeys()
            
            print(f"\nמקש המרה נוכחי: {current_convert}")
            print(f"מקשי יציאה נוכחיים: {', '.join(current_exit)}")
            
            print("\nאפשרויות:")
            print("1. שנה מקש המרה")
            print("2. שנה מקשי יציאה")
            print("3. הצג כל המקשים הזמינים")
            print("4. איפוס לברירת מחדל")
            print("5. שמור וצא")
            print("0. צא בלי לשמור")
            
            try:
                choice = input("\nבחר אפשרות (0-5): ").strip()
            except EOFError:
                choice = "0"
            
            if choice == "1":
                self.change_convert_hotkey()
            elif choice == "2":
                self.change_exit_hotkeys()
            elif choice == "3":
                self.show_available_hotkeys()
            elif choice == "4":
                self.reset_to_defaults()
            elif choice == "5":
                if self.save_settings():
                    print("ההגדרות נשמרו בהצלחה!")
                    break
            elif choice == "0":
                print("יציאה בלי לשמור...")
                break
            else:
                print("אפשרות לא חוקית, נסה שוב.")
    
    def change_convert_hotkey(self):
        """משנה את מקש ההמרה"""
        print("\nמקשי המרה זמינים:")
        for i, hotkey in enumerate(self.available_hotkeys[:20], 1):  # הצג רק 20 ראשונים
            print(f"{i:2d}. {hotkey}")
        
        print(f"... ועוד {len(self.available_hotkeys) - 20} מקשים")
        
        while True:
            choice = input("\nבחר מספר (או הקלד מקש ישירות): ").strip()
            
            # בדוק אם זה מספר
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.available_hotkeys):
                    new_hotkey = self.available_hotkeys[idx]
                    break
                else:
                    print("מספר לא חוקי, נסה שוב.")
            else:
                # בדוק אם זה מקש חוקי
                if choice in self.available_hotkeys:
                    new_hotkey = choice
                    break
                else:
                    print("מקש לא חוקי, נסה שוב.")
        
        # שמור את המקש החדש
        if settings_manager.set_hotkey("convert", new_hotkey):
            print(f"מקש המרה שונה ל: {new_hotkey}")
        else:
            print("שגיאה בשמירת המקש החדש.")
    
    def change_exit_hotkeys(self):
        """משנה את מקשי היציאה"""
        print("\nמקשי יציאה זמינים:")
        for i, hotkey in enumerate(self.available_hotkeys[:20], 1):
            print(f"{i:2d}. {hotkey}")
        
        print(f"... ועוד {len(self.available_hotkeys) - 20} מקשים")
        
        exit_hotkeys = []
        print("\nהוסף מקשי יציאה (הקלד 'סיום' כשסיימת):")
        
        while True:
            choice = input(f"מקש יציאה {len(exit_hotkeys) + 1}: ").strip()
            
            if choice.lower() in ['סיום', 'done', 'exit', 'quit']:
                break
            
            if choice in self.available_hotkeys:
                if choice not in exit_hotkeys:
                    exit_hotkeys.append(choice)
                    print(f"נוסף: {choice}")
                else:
                    print("מקש זה כבר קיים.")
            else:
                print("מקש לא חוקי, נסה שוב.")
        
        if exit_hotkeys:
            if settings_manager.set_hotkey("exit", exit_hotkeys):
                print(f"מקשי יציאה שונו ל: {', '.join(exit_hotkeys)}")
            else:
                print("שגיאה בשמירת מקשי היציאה.")
        else:
            print("לא נוספו מקשי יציאה.")
    
    def show_available_hotkeys(self):
        """מציג את כל המקשים הזמינים"""
        print("\nכל המקשים הזמינים:")
        print("-" * 40)
        
        for i, hotkey in enumerate(self.available_hotkeys, 1):
            print(f"{i:2d}. {hotkey}")
            if i % 10 == 0:  # הפסקה כל 10 מקשים
                try:
                    input("לחץ Enter להמשך...")
                except EOFError:
                    break
        
        try:
            input("\nלחץ Enter לחזרה לתפריט...")
        except EOFError:
            pass
    
    def reset_to_defaults(self):
        """מחזיר הגדרות לברירת מחדל"""
        confirm = input("האם אתה בטוח שברצונך להחזיר את ההגדרות לברירת מחדל? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', 'כן']:
            if settings_manager.reset_to_defaults():
                print("ההגדרות הוחזרו לברירת מחדל!")
            else:
                print("שגיאה באיפוס ההגדרות.")
        else:
            print("איפוס בוטל.")
    
    def save_settings(self):
        """שומר את ההגדרות"""
        return settings_manager.save_settings()

def main():
    """פונקציה ראשית"""
    configurator = SimpleHotkeyConfigurator()
    configurator.show_menu()

if __name__ == "__main__":
    main()