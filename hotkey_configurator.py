import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard
import threading
import time
from settings_manager import settings_manager

class HotkeyConfigurator:
    """ממשק משתמש להגדרת מקשי קיצור"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.listening = False
        self.current_hotkey = None
        self.listener = None
        
        # רשימת מקשי קיצור זמינים
        self.available_hotkeys = [
            "<ctrl>+<alt>+h",
            "<ctrl>+<shift>+h", 
            "<alt>+h",
            "<ctrl>+h",
            "<f1>",
            "<f2>",
            "<f3>",
            "<f4>",
            "<f5>",
            "<f6>",
            "<f7>",
            "<f8>",
            "<f9>",
            "<f10>",
            "<f11>",
            "<f12>",
            "<ctrl>+<f1>",
            "<ctrl>+<f2>",
            "<ctrl>+<f3>",
            "<ctrl>+<f4>",
            "<ctrl>+<f5>",
            "<ctrl>+<f6>",
            "<ctrl>+<f7>",
            "<ctrl>+<f8>",
            "<ctrl>+<f9>",
            "<ctrl>+<f10>",
            "<ctrl>+<f11>",
            "<ctrl>+<f12>",
            "<alt>+<f1>",
            "<alt>+<f2>",
            "<alt>+<f3>",
            "<alt>+<f4>",
            "<alt>+<f5>",
            "<alt>+<f6>",
            "<alt>+<f7>",
            "<alt>+<f8>",
            "<alt>+<f9>",
            "<alt>+<f10>",
            "<alt>+<f11>",
            "<alt>+<f12>",
            "<ctrl>+<shift>+<f1>",
            "<ctrl>+<shift>+<f2>",
            "<ctrl>+<shift>+<f3>",
            "<ctrl>+<shift>+<f4>",
            "<ctrl>+<shift>+<f5>",
            "<ctrl>+<shift>+<f6>",
            "<ctrl>+<shift>+<f7>",
            "<ctrl>+<shift>+<f8>",
            "<ctrl>+<shift>+<f9>",
            "<ctrl>+<shift>+<f10>",
            "<ctrl>+<shift>+<f11>",
            "<ctrl>+<shift>+<f12>",
            "<ctrl>+<alt>+<f1>",
            "<ctrl>+<alt>+<f2>",
            "<ctrl>+<alt>+<f3>",
            "<ctrl>+<alt>+<f4>",
            "<ctrl>+<alt>+<f5>",
            "<ctrl>+<alt>+<f6>",
            "<ctrl>+<alt>+<f7>",
            "<ctrl>+<alt>+<f8>",
            "<ctrl>+<alt>+<f9>",
            "<ctrl>+<alt>+<f10>",
            "<ctrl>+<alt>+<f11>",
            "<ctrl>+<alt>+<f12>",
            "<ctrl>+<shift>+q",
            "<alt>+q",
            "<ctrl>+q",
            "<ctrl>+<alt>+q",
            "<ctrl>+<shift>+<alt>+q"
        ]
    
    def show_configurator(self):
        """מציג את חלון הגדרת מקשי הקיצור"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("הגדרת מקשי קיצור - ממיר עברית")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # מרכז את החלון
        self.window.eval('tk::PlaceWindow . center')
        
        # כותרת
        title_label = tk.Label(self.window, text="הגדרת מקשי קיצור", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=15)
        
        # הסבר
        info_label = tk.Label(self.window, 
                             text="בחר מקשי קיצור חדשים עבור הממיר. לחץ על 'האזן' כדי להקליד מקש חדש.",
                             font=("Arial", 10), wraplength=550)
        info_label.pack(pady=10)
        
        # מסגרת הגדרות המרה
        convert_frame = tk.LabelFrame(self.window, text="מקש המרה", 
                                     font=("Arial", 12, "bold"))
        convert_frame.pack(pady=10, padx=20, fill="x")
        
        # מקש המרה נוכחי
        tk.Label(convert_frame, text="מקש נוכחי:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        self.current_convert_var = tk.StringVar(value=settings_manager.get_hotkey("convert"))
        current_convert_label = tk.Label(convert_frame, textvariable=self.current_convert_var, 
                                        font=("Arial", 10, "bold"), fg="blue")
        current_convert_label.pack(anchor="w", padx=10, pady=2)
        
        # בחירת מקש המרה חדש
        convert_selection_frame = tk.Frame(convert_frame)
        convert_selection_frame.pack(fill="x", padx=10, pady=10)
        
        self.convert_var = tk.StringVar(value=settings_manager.get_hotkey("convert"))
        convert_combo = ttk.Combobox(convert_selection_frame, textvariable=self.convert_var, 
                                    values=self.available_hotkeys, state="readonly", width=30)
        convert_combo.pack(side="left", padx=(0, 10))
        
        self.convert_listen_btn = tk.Button(convert_selection_frame, text="האזן", 
                                           command=lambda: self.start_listening("convert"))
        self.convert_listen_btn.pack(side="left", padx=5)
        
        # מסגרת הגדרות יציאה
        exit_frame = tk.LabelFrame(self.window, text="מקשי יציאה", 
                                  font=("Arial", 12, "bold"))
        exit_frame.pack(pady=10, padx=20, fill="x")
        
        # מקשי יציאה נוכחיים
        tk.Label(exit_frame, text="מקשי יציאה נוכחיים:", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        current_exit_hotkeys = settings_manager.get_exit_hotkeys()
        self.current_exit_var = tk.StringVar(value=", ".join(current_exit_hotkeys))
        current_exit_label = tk.Label(exit_frame, textvariable=self.current_exit_var, 
                                     font=("Arial", 10, "bold"), fg="blue")
        current_exit_label.pack(anchor="w", padx=10, pady=2)
        
        # בחירת מקשי יציאה חדשים
        exit_selection_frame = tk.Frame(exit_frame)
        exit_selection_frame.pack(fill="x", padx=10, pady=10)
        
        self.exit_var = tk.StringVar(value=current_exit_hotkeys[0] if current_exit_hotkeys else "")
        exit_combo = ttk.Combobox(exit_selection_frame, textvariable=self.exit_var, 
                                 values=self.available_hotkeys, state="readonly", width=30)
        exit_combo.pack(side="left", padx=(0, 10))
        
        self.exit_listen_btn = tk.Button(exit_selection_frame, text="האזן", 
                                        command=lambda: self.start_listening("exit"))
        self.exit_listen_btn.pack(side="left", padx=5)
        
        # הוספת מקש יציאה נוסף
        self.add_exit_btn = tk.Button(exit_selection_frame, text="הוסף מקש", 
                                     command=self.add_exit_hotkey)
        self.add_exit_btn.pack(side="left", padx=5)
        
        # רשימת מקשי יציאה
        self.exit_listbox = tk.Listbox(exit_frame, height=3)
        self.exit_listbox.pack(fill="x", padx=10, pady=5)
        self.refresh_exit_list()
        
        # כפתור הסרה
        remove_exit_btn = tk.Button(exit_frame, text="הסר מקש נבחר", 
                                   command=self.remove_selected_exit)
        remove_exit_btn.pack(anchor="w", padx=10, pady=5)
        
        # כפתורים
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="שמור הגדרות", 
                            command=self.save_settings, font=("Arial", 10, "bold"))
        save_btn.pack(side="left", padx=10)
        
        reset_btn = tk.Button(button_frame, text="איפוס לברירת מחדל", 
                             command=self.reset_settings, font=("Arial", 10))
        reset_btn.pack(side="left", padx=10)
        
        close_btn = tk.Button(button_frame, text="סגור", 
                             command=self.close_window, font=("Arial", 10))
        close_btn.pack(side="left", padx=10)
        
        # סגור את החלון כשסוגרים
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
    
    def start_listening(self, action):
        """מתחיל להאזין למקש חדש"""
        if self.listening:
            self.stop_listening()
            return
        
        self.listening = True
        self.current_hotkey = action
        
        if action == "convert":
            self.convert_listen_btn.config(text="עצור", bg="red", fg="white")
        else:
            self.exit_listen_btn.config(text="עצור", bg="red", fg="white")
        
        # התחל להאזין למקשים
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()
        
        # הודעת הוראות
        messagebox.showinfo("האזנה למקשים", 
                           f"לחץ על מקשי הקיצור הרצויים עבור {action}.\n"
                           "לחץ על 'עצור' או סגור את החלון כדי לסיים.")
    
    def stop_listening(self):
        """עוצר את ההאזנה למקשים"""
        self.listening = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        if self.current_hotkey == "convert":
            self.convert_listen_btn.config(text="האזן", bg="SystemButtonFace", fg="black")
        else:
            self.exit_listen_btn.config(text="האזן", bg="SystemButtonFace", fg="black")
    
    def on_key_press(self, key):
        """מטפל בלחיצת מקש"""
        if not self.listening:
            return
        
        try:
            # המר את המקש לפורמט הנדרש
            hotkey_str = self.key_to_string(key)
            if hotkey_str:
                if self.current_hotkey == "convert":
                    self.convert_var.set(hotkey_str)
                else:
                    self.exit_var.set(hotkey_str)
                self.stop_listening()
        except Exception as e:
            print(f"שגיאה בהמרת מקש: {e}")
    
    def key_to_string(self, key):
        """ממיר מקש לפורמט מחרוזת"""
        try:
            # בדוק אם זה מקש מיוחד
            if hasattr(key, 'name'):
                if key.name in ['ctrl_l', 'ctrl_r']:
                    return '<ctrl>'
                elif key.name in ['alt_l', 'alt_r']:
                    return '<alt>'
                elif key.name in ['shift_l', 'shift_r']:
                    return '<shift>'
                elif key.name.startswith('f') and key.name[1:].isdigit():
                    return f'<{key.name}>'
                else:
                    return f'<{key.name}>'
            else:
                # מקש רגיל
                return f'<{key.char}>' if hasattr(key, 'char') and key.char else None
        except:
            return None
    
    def add_exit_hotkey(self):
        """מוסיף מקש יציאה חדש"""
        hotkey = self.exit_var.get()
        if hotkey and hotkey not in self.get_exit_hotkeys():
            self.exit_listbox.insert(tk.END, hotkey)
            self.exit_var.set("")
    
    def remove_selected_exit(self):
        """מסיר מקש יציאה נבחר"""
        selection = self.exit_listbox.curselection()
        if selection:
            self.exit_listbox.delete(selection[0])
    
    def get_exit_hotkeys(self):
        """מחזיר רשימת מקשי יציאה"""
        return [self.exit_listbox.get(i) for i in range(self.exit_listbox.size())]
    
    def refresh_exit_list(self):
        """מרענן את רשימת מקשי היציאה"""
        self.exit_listbox.delete(0, tk.END)
        current_hotkeys = settings_manager.get_exit_hotkeys()
        for hotkey in current_hotkeys:
            self.exit_listbox.insert(tk.END, hotkey)
    
    def save_settings(self):
        """שומר את ההגדרות החדשות"""
        try:
            # שמור מקש המרה
            convert_hotkey = self.convert_var.get()
            if convert_hotkey:
                settings_manager.set_hotkey("convert", convert_hotkey)
            
            # שמור מקשי יציאה
            exit_hotkeys = self.get_exit_hotkeys()
            if exit_hotkeys:
                settings_manager.set_hotkey("exit", exit_hotkeys)
            
            # עדכן את התצוגה
            self.current_convert_var.set(convert_hotkey)
            self.current_exit_var.set(", ".join(exit_hotkeys))
            
            messagebox.showinfo("הצלחה", "ההגדרות נשמרו בהצלחה!")
            return True
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשמירת ההגדרות: {e}")
            return False
    
    def reset_settings(self):
        """מחזיר הגדרות לברירת מחדל"""
        if messagebox.askyesno("אישור", "האם אתה בטוח שברצונך להחזיר את ההגדרות לברירת מחדל?"):
            settings_manager.reset_to_defaults()
            self.convert_var.set(settings_manager.get_hotkey("convert"))
            self.exit_var.set("")
            self.refresh_exit_list()
            self.current_convert_var.set(settings_manager.get_hotkey("convert"))
            self.current_exit_var.set(", ".join(settings_manager.get_exit_hotkeys()))
            messagebox.showinfo("הצלחה", "ההגדרות הוחזרו לברירת מחדל!")
    
    def close_window(self):
        """סוגר את החלון"""
        self.stop_listening()
        if self.window:
            self.window.destroy()
            self.window = None

# פונקציה עזר ליצירת חלון הגדרות
def show_hotkey_configurator(parent=None):
    """מציג את חלון הגדרת מקשי הקיצור"""
    configurator = HotkeyConfigurator(parent)
    configurator.show_configurator()
    return configurator