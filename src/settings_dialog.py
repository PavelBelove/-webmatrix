import customtkinter as ctk
from typing import Dict, Optional
from .config import APIKeys
from .localization import Localization

class APISettingsDialog:
    def __init__(self, parent, localization: "Localization", main_window=None):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(localization.get("settings_button"))
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        
        self.localization = localization
        self.main_window = main_window
        
        # Создаем фрейм с отступами
        self.frame = ctk.CTkFrame(self.dialog)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Выбор языка
        ctk.CTkLabel(
            self.frame,
            text=localization.get("language")
        ).pack(anchor="w", pady=(0, 5))
        
        self.language = ctk.CTkComboBox(
            self.frame,
            values=["English", "Русский"],
            command=self.change_language
        )
        self.language.pack(pady=(0, 15))
        self.language.set("Русский" if localization.current_language == "ru" else "English")
        
        # OpenAI API Key
        ctk.CTkLabel(
            self.frame,
            text="OpenAI API Key:"
        ).pack(anchor="w", pady=(0, 5))
        
        self.openai_key = ctk.CTkEntry(
            self.frame,
            width=500,
            placeholder_text="sk-..."
        )
        self.openai_key.pack(pady=(0, 15))
        
        # Anthropic API Key
        ctk.CTkLabel(
            self.frame,
            text="Anthropic API Key:"
        ).pack(anchor="w", pady=(0, 5))
        
        self.anthropic_key = ctk.CTkEntry(
            self.frame,
            width=500,
            placeholder_text="sk-ant-..."
        )
        self.anthropic_key.pack(pady=(0, 15))
        
        # Кнопки
        self.button_frame = ctk.CTkFrame(self.frame)
        self.button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            self.button_frame,
            text=localization.get("save_button"),
            command=self.save_and_close
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.button_frame,
            text=localization.get("cancel_button"),
            command=self.dialog.destroy
        ).pack(side="right", padx=5)
        
        # Загружаем текущие ключи
        self.load_keys()
        
        # Делаем окно модальным
        self.dialog.grab_set()
    
    def load_keys(self):
        """Загружает существующие ключи"""
        api_keys = APIKeys.load()
        if api_keys.openai:
            self.openai_key.insert(0, api_keys.openai)
        if api_keys.anthropic:
            self.anthropic_key.insert(0, api_keys.anthropic)
    
    def save_and_close(self):
        """Сохраняет ключи и закрывает окно"""
        api_keys = APIKeys(
            openai=self.openai_key.get().strip() or None,
            anthropic=self.anthropic_key.get().strip() or None
        )
        api_keys.save()
        self.dialog.destroy()
    
    def change_language(self, choice):
        """Меняет язык интерфейса"""
        self.localization.current_language = "ru" if choice == "Русский" else "en"
        self.localization.save()
        
        # Обновляем тексты в текущем окне
        self.dialog.title(self.localization.get("settings_button"))
        
        # Обновляем основной интерфейс если он есть
        if self.main_window:
            self.main_window.update_language() 