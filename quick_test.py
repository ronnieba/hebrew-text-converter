#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
בדיקה מהירה של מערכת ההגדרות
"""

def test_settings_system():
    """בודק את מערכת ההגדרות"""
    print("="*50)
    print("בדיקה מהירה - מערכת הגדרת מקשי קיצור")
    print("="*50)
    
    try:
        # בדיקת טעינת מנהל ההגדרות
        from settings_manager import settings_manager
        print("✅ מנהל ההגדרות נטען בהצלחה")
        
        # בדיקת הגדרות נוכחיות
        convert_hotkey = settings_manager.get_hotkey("convert")
        exit_hotkeys = settings_manager.get_exit_hotkeys()
        
        print(f"✅ מקש המרה נוכחי: {convert_hotkey}")
        print(f"✅ מקשי יציאה נוכחיים: {', '.join(exit_hotkeys)}")
        
        # בדיקת שינוי הגדרות
        print("\n🔧 בודק שינוי הגדרות...")
        original_convert = convert_hotkey
        
        # שנה מקש המרה
        settings_manager.set_hotkey("convert", "<f5>")
        new_convert = settings_manager.get_hotkey("convert")
        print(f"✅ שינוי מקש המרה: {original_convert} -> {new_convert}")
        
        # החזר הגדרות מקוריות
        settings_manager.set_hotkey("convert", original_convert)
        restored_convert = settings_manager.get_hotkey("convert")
        print(f"✅ החזרת הגדרות: {restored_convert}")
        
        # בדיקת שמירה לקובץ
        if settings_manager.save_settings():
            print("✅ הגדרות נשמרו לקובץ בהצלחה")
        else:
            print("❌ שגיאה בשמירת הגדרות")
        
        # בדיקת טעינת ממשק הגדרת מקשי קיצור
        print("\n🔧 בודק ממשק הגדרת מקשי קיצור...")
        from simple_hotkey_configurator import SimpleHotkeyConfigurator
        configurator = SimpleHotkeyConfigurator()
        print("✅ ממשק הגדרת מקשי קיצור נטען בהצלחה")
        
        print("\n" + "="*50)
        print("🎉 כל הבדיקות עברו בהצלחה!")
        print("המערכת מוכנה לשימוש")
        print("="*50)
        
        return True
        
    except ImportError as e:
        print(f"❌ שגיאה בטעינת מודולים: {e}")
        print("ודא שהתקנת את כל התלויות הנדרשות")
        return False
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        return False

def show_usage_instructions():
    """מציג הוראות שימוש"""
    print("\n" + "="*50)
    print("הוראות שימוש")
    print("="*50)
    
    print("\n1. להגדרת מקשי קיצור:")
    print("   python3 simple_hotkey_configurator.py")
    
    print("\n2. להפעלת הממיר המתקדם:")
    print("   python3 hebrew_converter_simple_advanced.py")
    
    print("\n3. לדמו המערכת:")
    print("   python3 hotkey_settings_demo.py")
    
    print("\n4. לבדיקה מהירה:")
    print("   python3 quick_test.py")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    success = test_settings_system()
    
    if success:
        show_usage_instructions()
    else:
        print("\n❌ יש בעיות במערכת. בדוק את ההתקנה.")