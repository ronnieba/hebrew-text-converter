#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
דמו להגדרת מקשי קיצור - ממיר עברית
גרסה זו מציגה את יכולות מערכת ההגדרות החדשה
"""

from settings_manager import settings_manager
from simple_hotkey_configurator import SimpleHotkeyConfigurator

def main():
    """פונקציה ראשית להדגמת מערכת ההגדרות"""
    print("="*60)
    print("דמו מערכת הגדרת מקשי קיצור - ממיר עברית")
    print("="*60)
    
    # הצג הגדרות נוכחיות
    print("\nהגדרות נוכחיות:")
    print("-" * 30)
    
    current_convert = settings_manager.get_hotkey("convert")
    current_exit = settings_manager.get_exit_hotkeys()
    
    print(f"מקש המרה: {current_convert}")
    print(f"מקשי יציאה: {', '.join(current_exit)}")
    
    # הצג כל ההגדרות
    print("\nכל ההגדרות:")
    print("-" * 30)
    all_settings = settings_manager.get_all_settings()
    for category, settings in all_settings.items():
        print(f"\n{category}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    # הדגמת שינוי הגדרות
    print("\nהדגמת שינוי הגדרות:")
    print("-" * 30)
    
    # שמור הגדרות נוכחיות
    original_convert = current_convert
    original_exit = current_exit.copy()
    
    # שנה מקש המרה
    print(f"משנה מקש המרה מ-{original_convert} ל-<f1>")
    settings_manager.set_hotkey("convert", "<f1>")
    print(f"מקש המרה חדש: {settings_manager.get_hotkey('convert')}")
    
    # שנה מקשי יציאה
    print(f"משנה מקשי יציאה מ-{original_exit} ל-['<f2>', '<f3>']")
    settings_manager.set_hotkey("exit", ["<f2>", "<f3>"])
    print(f"מקשי יציאה חדשים: {settings_manager.get_exit_hotkeys()}")
    
    # החזר הגדרות מקוריות
    print("\nמחזיר הגדרות מקוריות...")
    settings_manager.set_hotkey("convert", original_convert)
    settings_manager.set_hotkey("exit", original_exit)
    print(f"מקש המרה: {settings_manager.get_hotkey('convert')}")
    print(f"מקשי יציאה: {settings_manager.get_exit_hotkeys()}")
    
    # הדגמת ממשק הגדרת מקשי קיצור
    print("\n" + "="*60)
    print("ממשק הגדרת מקשי קיצור")
    print("="*60)
    print("להפעלת ממשק הגדרת מקשי קיצור, הרץ:")
    print("python3 simple_hotkey_configurator.py")
    
    # הדגמת שימוש בממיר המתקדם
    print("\n" + "="*60)
    print("הפעלת ממיר מתקדם")
    print("="*60)
    print("להפעלת הממיר המתקדם, הרץ:")
    print("python3 hebrew_converter_simple_advanced.py")
    
    print("\n" + "="*60)
    print("הדמו הושלם בהצלחה!")
    print("="*60)

if __name__ == "__main__":
    main()