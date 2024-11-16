import customtkinter as ctk
from typing import Optional, Dict, Any
from .config import Config, Profile, BrowserConfig
from .models import AVAILABLE_MODELS
from .widgets import LabelWithTooltip, CheckboxWithTooltip, BetterTextbox

class ProfileDialog:
    def __init__(self, parent, profile_name: Optional[str] = None, localization: "Localization" = None):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(
            localization.get("edit_profile_title" if profile_name else "new_profile_title")
        )
        self.dialog.geometry("700x800")
        self.dialog.transient(parent)
        
        self.localization = localization
        self.profile_name = profile_name
        self.result: Optional[Dict[str, Any]] = None
        
        # Основной контейнер с прокруткой
        self.main_frame = ctk.CTkScrollableFrame(self.dialog)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Название профиля
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("profile_name")
        ).pack(anchor="w", pady=(0, 5))
        
        self.name = ctk.CTkEntry(
            self.main_frame,
            width=600,
            placeholder_text=self.localization.get("profile_name_placeholder")
        )
        self.name.pack(pady=(0, 15))
        
        # Описание
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("profile_description")
        ).pack(anchor="w", pady=(0, 5))
        
        self.description = ctk.CTkEntry(
            self.main_frame,
            width=600,
            placeholder_text=self.localization.get("profile_description_placeholder")
        )
        self.description.pack(pady=(0, 15))
        
        # Входные колонки
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("input_columns")
        ).pack(anchor="w", pady=(0, 5))
        
        self.input_columns = ctk.CTkEntry(
            self.main_frame,
            width=600,
            placeholder_text=self.localization.get("input_columns_placeholder")
        )
        self.input_columns.pack(pady=(0, 15))
        
        # Промпт
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("prompt")
        ).pack(anchor="w", pady=(0, 5))
        
        self.prompt = BetterTextbox(
            self.main_frame,
            width=600,
            height=200
        )
        self.prompt.pack(pady=(0, 15))
        
        # Выходные колонки
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("output_columns")
        ).pack(anchor="w", pady=(0, 5))
        
        self.output_columns = BetterTextbox(
            self.main_frame,
            width=600,
            height=100
        )
        self.output_columns.pack(pady=(0, 15))
        
        # Модель
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("model")
        ).pack(anchor="w", pady=(0, 5))
        
        self.model = ctk.CTkComboBox(
            self.main_frame,
            values=[
                f"{k} - {self.localization.get(m.description_key)}" 
                for k, m in AVAILABLE_MODELS.items()
            ],
            width=600
        )
        self.model.pack(pady=(0, 15))
        
        # Настройки браузера
        browser_frame = ctk.CTkFrame(self.main_frame)
        browser_frame.pack(fill="x", pady=(0, 15))
        
        browser_left_frame = ctk.CTkFrame(browser_frame)
        browser_left_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            browser_left_frame,
            text=self.localization.get("parallel_browsers")
        ).pack(side="left", padx=5)
        
        self.parallel = ctk.CTkSlider(
            browser_left_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            width=100
        )
        self.parallel.pack(side="left", padx=5)
        self.parallel.set(3)
        
        self.parallel_label = ctk.CTkLabel(
            browser_left_frame,
            text="3"
        )
        self.parallel_label.pack(side="left", padx=5)
        
        # Переключатель режима в центр
        self.use_browser = CheckboxWithTooltip(
            browser_frame,
            text=self.localization.get("online_search"),
            tooltip=self.localization.get("tooltip_online_search"),
            command=self.toggle_browser_settings
        )
        self.use_browser.pack(side="left", padx=20)
        self.use_browser.select()
        
        # Работа в фоне справа
        self.headless = CheckboxWithTooltip(
            browser_frame,
            text=self.localization.get("headless_mode"),
            tooltip=self.localization.get("tooltip_headless")
        )
        self.headless.pack(side="right", padx=5)
        
        # Температура
        temp_frame = ctk.CTkFrame(self.main_frame)
        temp_frame.pack(fill="x", pady=(0, 15))
        
        LabelWithTooltip(
            temp_frame,
            text=self.localization.get("temperature"),
            tooltip=self.localization.get("tooltip_temperature")
        ).pack(side="left", padx=5)
        
        self.temperature = ctk.CTkSlider(
            temp_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            width=100
        )
        self.temperature.pack(side="left", padx=5)
        self.temperature.set(0)
        
        self.temp_label = ctk.CTkLabel(
            temp_frame,
            text="0.0"
        )
        self.temp_label.pack(side="left", padx=5)
        
        self.temperature.configure(
            command=lambda v: self.temp_label.configure(text=f"{float(v):.1f}")
        )
        
        # Кнопки
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(
            button_frame,
            text=self.localization.get("save_button"),
            command=self.save_and_close
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text=self.localization.get("cancel_button"),
            command=self.dialog.destroy
        ).pack(side="right", padx=5)
        
        # Если редактируем существующий профиль
        if profile_name:
            self.load_profile(profile_name)
        
        # Делаем окно модальным
        self.dialog.grab_set()
        
    def load_profile(self, profile_name: str):
        """Загружает данные профиля"""
        config = Config.load()
        profile = config.profiles[profile_name]
        
        self.name.insert(0, profile_name)
        self.description.insert(0, profile.description)
        self.input_columns.insert(0, ", ".join(profile.input_columns))
        self.prompt.insert("1.0", profile.prompt)
        self.output_columns.insert("1.0", "\n".join(profile.output_columns))
        
        # Находим полное название модели
        model_name = f"{profile.model} - {self.localization.get(AVAILABLE_MODELS[profile.model].description_key)}"
        self.model.set(model_name)
        
        if profile.browser_config:
            self.parallel.set(profile.browser_config.max_parallel)
            if profile.browser_config.headless:
                self.headless.select()
            else:
                self.headless.deselect()
        
        if hasattr(profile, 'temperature'):
            self.temperature.set(profile.temperature)
            self.temp_label.configure(text=f"{profile.temperature:.1f}")
    
    def toggle_browser_settings(self):
        """Включает/выключает настройки браузера"""
        enabled = bool(self.use_browser.get())
        state = "normal" if enabled else "disabled"
        
        self.parallel.configure(state=state)
        self.parallel_label.configure(state=state)
        self.headless.configure(state=state)
    
    def save_and_close(self):
        """Сохраняет профиль и закрывает окно"""
        # Получаем короткое имя модели из полного названия
        model_full = self.model.get()
        model_name = model_full.split(" - ")[0]
        
        profile_data = {
            "name": self.name.get().strip(),
            "description": self.description.get().strip(),
            "input_columns": [col.strip() for col in self.input_columns.get().split(",")],
            "prompt": self.prompt.get("1.0", "end").strip(),
            "output_columns": [
                col.strip() 
                for col in self.output_columns.get("1.0", "end").split("\n")
                if col.strip()
            ],
            "model": model_name,
            "temperature": float(self.temperature.get()),
            "browser_config": {
                "max_parallel": int(self.parallel.get()),
                "headless": bool(self.headless.get()),
                "timeout": 30
            },
            "use_browser": bool(self.use_browser.get())
        }
        
        # Сохраняем в конфиг
        config = Config.load()
        profile_name = self.name.get().strip()
        
        config.profiles[profile_name] = Profile(**profile_data)
        config.save()
        
        self.dialog.destroy() 