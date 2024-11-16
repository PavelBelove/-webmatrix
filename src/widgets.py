import customtkinter as ctk
import tkinter as tk

class LabelWithTooltip(ctk.CTkLabel):
    def __init__(self, *args, tooltip=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if tooltip:
            self.tooltip = tooltip
            self.tooltip_window = None
            
            self.bind("<Enter>", self.show_tooltip)
            self.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        
        label = tk.Label(
            self.tooltip_window,
            text=self.tooltip,
            justify=tk.LEFT,
            background="#2b2b2b",
            foreground="white",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=5
        )
        label.pack()
        
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class CheckboxWithTooltip(ctk.CTkCheckBox):
    def __init__(self, *args, tooltip=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if tooltip:
            self.tooltip = tooltip
            self.tooltip_window = None
            
            self.bind("<Enter>", self.show_tooltip)
            self.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x = self.winfo_rootx() + 25
        y = self.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self)
        self.tooltip_window.wm_overrideredirect(True)
        
        label = tk.Label(
            self.tooltip_window,
            text=self.tooltip,
            justify=tk.LEFT,
            background="#2b2b2b",
            foreground="white",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=5
        )
        label.pack()
        
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None 

class BetterTextbox(ctk.CTkTextbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Добавляем стандартные сочетания клавиш
        self.bind('<Control-a>', self._select_all)
        self.bind('<Control-A>', self._select_all)
        self.bind('<Control-v>', self._paste)
        self.bind('<Control-V>', self._paste)
        
    def _select_all(self, event):
        """Выделяет весь текст"""
        self.tag_add('sel', '1.0', 'end')
        return "break"
    
    def _paste(self, event):
        """Улучшенная вставка текста"""
        try:
            # Если есть выделение, удаляем его
            if self.tag_ranges('sel'):
                self.delete('sel.first', 'sel.last')
            
            # Вставляем текст из буфера обмена
            text = self.clipboard_get()
            self.insert('insert', text)
        except:
            pass
        return "break" 