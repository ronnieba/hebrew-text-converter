#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
סקריפט התקנה אוטומטי לממיר עברית מתקדם
"""

import subprocess
import sys
import os

def install_requirements():
    """מתקין את התלויות הנדרשות"""
    print("🔧 מתקין תלויות...")
    
    requirements = [
        "pyperclip",
        "pynput", 
        "pystray",
        "Pillow"
    ]
    
    for package in requirements:
        try:
            print(f"מתקין {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} הותקן בהצלחה")
        except subprocess.CalledProcessError as e:
            print(f"❌ שגיאה בהתקנת {package}: {e}")
            return False
    
    return True

def test_installation():
    """בודק שההתקנה עבדה"""
    print("\n🧪 בודק התקנה...")
    
    try:
        import pyperclip
        print("✅ pyperclip זמין")
    except ImportError:
        print("❌ pyperclip לא זמין")
        return False
    
    try:
        import pynput
        print("✅ pynput זמין")
    except ImportError:
        print("❌ pynput לא זמין")
        return False
    
    try:
        import pystray
        print("✅ pystray זמין")
    except ImportError:
        print("❌ pystray לא זמין")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow זמין")
    except ImportError:
        print("❌ Pillow לא זמין")
        return False
    
    return True

def create_desktop_shortcut():
    """יוצר קיצור דרך על שולחן העבודה"""
    print("\n🖥️ יוצר קיצורי דרך...")
    
    # קובץ batch עבור Windows
    if os.name == 'nt':
        batch_content = """@echo off
cd /d "%~dp0"
python hebrew_converter_simple_advanced.py
pause
"""
        with open("הפעלת ממיר עברית.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ נוצר קיצור דרך: הפעלת ממיר עברית.bat")
    
    # קובץ shell עבור Linux/macOS
    else:
        shell_content = """#!/bin/bash
cd "$(dirname "$0")"
python3 hebrew_converter_simple_advanced.py
"""
        with open("הפעלת ממיר עברית.sh", "w", encoding="utf-8") as f:
            f.write(shell_content)
        os.chmod("הפעלת ממיר עברית.sh", 0o755)
        print("✅ נוצר קיצור דרך: הפעלת ממיר עברית.sh")

def main():
    """פונקציה ראשית"""
    print("="*60)
    print("התקנה אוטומטית - ממיר עברית מתקדם")
    print("="*60)
    
    # בדוק גרסת Python
    if sys.version_info < (3, 6):
        print("❌ נדרשת Python 3.6 או חדש יותר")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} זמין")
    
    # התקן תלויות
    if not install_requirements():
        print("❌ התקנת התלויות נכשלה")
        return False
    
    # בדוק התקנה
    if not test_installation():
        print("❌ בדיקת ההתקנה נכשלה")
        return False
    
    # צור קיצורי דרך
    create_desktop_shortcut()
    
    print("\n" + "="*60)
    print("🎉 ההתקנה הושלמה בהצלחה!")
    print("="*60)
    
    print("\nאיך להפעיל:")
    print("1. python3 quick_test.py - לבדיקה מהירה")
    print("2. python3 simple_hotkey_configurator.py - להגדרת מקשי קיצור")
    print("3. python3 hebrew_converter_simple_advanced.py - להפעלת הממיר")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ ההתקנה נכשלה. בדוק את ההודעות למעלה.")
        sys.exit(1)
    else:
        print("\n✅ הכל מוכן! תוכל להתחיל להשתמש בממיר.")