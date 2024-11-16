import customtkinter as ctk
import json
from pathlib import Path
import asyncio
import webbrowser
import os
from typing import Optional, Dict, Any
from .data_processor import DataProcessor
from .config import Config
from .models import AVAILABLE_MODELS
from .widgets import LabelWithTooltip, CheckboxWithTooltip, BetterTextbox
from .localization import Localization
import tkinter as tk

class BrowserAssistantGUI:
    def __init__(self):
        self.config: Optional[Dict[str, Any]] = None
        self.localization = Localization.load()
        self.localization.update_translations()  # Обновляем переводы
        self.localization.current_language = "en"  # Английский по умолчанию
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(self.localization.get("window_title"))
        self.root.geometry("800x900")
        
        # Создаем основной контейнер с прокруткой
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель с кнопками
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            self.top_frame, 
            text=self.localization.get("readme_button"),
            command=self.open_readme
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.top_frame, 
            text=self.localization.get("settings_button"),
            command=self.open_settings
        ).pack(side="right", padx=5)
        
        # Выбор файлов
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.pack(fill="x", pady=10)
        
        file_label_frame = ctk.CTkFrame(self.file_frame)
        file_label_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(
            file_label_frame, 
            text=self.localization.get("input_file")
        ).pack(anchor="w", padx=5)
        
        input_frame = ctk.CTkFrame(self.file_frame)
        input_frame.pack(fill="x")
        self.input_file = ctk.CTkEntry(
            input_frame,
            placeholder_text=self.localization.get("file_select_placeholder")
        )
        self.input_file.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        ctk.CTkButton(
            input_frame,
            text=self.localization.get("browse_button"),
            width=100,  # Фиксированная ширина кнопки
            command=self.browse_input
        ).pack(side="right", padx=5)
        
        # Выходной файл
        output_label_frame = ctk.CTkFrame(self.file_frame)
        output_label_frame.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(
            output_label_frame,
            text=self.localization.get("output_file")
        ).pack(anchor="w", padx=5)
        
        output_frame = ctk.CTkFrame(self.file_frame)
        output_frame.pack(fill="x")
        self.output_file = ctk.CTkEntry(
            output_frame,
            placeholder_text=self.localization.get("file_select_placeholder")
        )
        self.output_file.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        ctk.CTkButton(
            output_frame,
            text=self.localization.get("browse_button"),
            width=100,  # Фиксированная ширина кнопки
            command=self.browse_output
        ).pack(side="right", padx=5)
        
        # Выбор профиля
        self.profile_frame = ctk.CTkFrame(self.main_frame)
        self.profile_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            self.profile_frame,
            text=self.localization.get("profile")
        ).pack(side="left", padx=5)
        
        self.profile_var = ctk.StringVar()
        self.profile_combo = ctk.CTkComboBox(
            self.profile_frame,
            variable=self.profile_var,
            width=400,
            command=self.on_profile_change
        )
        self.profile_combo.pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.profile_frame,
            text=self.localization.get("create_profile"),
            command=self.new_profile
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.profile_frame,
            text=self.localization.get("edit_profile"),
            command=self.edit_profile
        ).pack(side="left", padx=5)
        
        # Промпт
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("prompt")
        ).pack(anchor="w", padx=5)
        
        self.prompt = BetterTextbox(
            self.main_frame,
            height=200,
            width=780
        )
        self.prompt.pack(pady=5)
        
        # Выходные колонки
        ctk.CTkLabel(
            self.main_frame,
            text=self.localization.get("output_columns")
        ).pack(anchor="w", padx=5)
        
        self.columns = BetterTextbox(
            self.main_frame,
            height=100,
            width=780
        )
        self.columns.pack(pady=5)
        
        # Настройки
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.pack(fill="x", pady=10)
        
        # Выбор модели
        ctk.CTkLabel(
            self.settings_frame,
            text=self.localization.get("model")
        ).pack(side="left", padx=5)
        
        self.model_var = ctk.StringVar()
        self.model_combo = ctk.CTkComboBox(
            self.settings_frame,
            variable=self.model_var,
            values=[
                f"{k} - {self.localization.get(m.description_key)}" 
                for k, m in AVAILABLE_MODELS.items()
            ],
            width=400
        )
        self.model_combo.pack(side="left", padx=5)
        
        # Температура
        LabelWithTooltip(
            self.settings_frame,
            text=self.localization.get("temperature"),
            tooltip=self.localization.get("tooltip_temperature")
        ).pack(side="left", padx=(20, 5))
        
        self.temperature = ctk.CTkSlider(
            self.settings_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            width=100
        )
        self.temperature.pack(side="left", padx=5)
        self.temperature.set(0)
        
        self.temp_label = ctk.CTkLabel(
            self.settings_frame,
            text="0.0"
        )
        self.temp_label.pack(side="left", padx=5)
        
        # Добавляем обновление лейбла при изменении
        self.temperature.configure(
            command=lambda v: self.temp_label.configure(text=f"{float(v):.1f}")
        )
        
        # Параллельные браузеры
        self.browser_frame = ctk.CTkFrame(self.main_frame)
        self.browser_frame.pack(fill="x", pady=10)
        
        browser_left_frame = ctk.CTkFrame(self.browser_frame)
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
        
        # Добавляем переключатель режима в центр
        self.use_browser = CheckboxWithTooltip(
            self.browser_frame,
            text=self.localization.get("online_search"),
            tooltip=self.localization.get("tooltip_online_search"),
            command=self.toggle_browser_settings
        )
        self.use_browser.pack(side="left", padx=20)
        self.use_browser.select()
        
        # Работа в фоне справа
        self.headless_var = ctk.BooleanVar(value=True)
        self.headless = CheckboxWithTooltip(
            self.browser_frame,
            text=self.localization.get("headless_mode"),
            tooltip=self.localization.get("tooltip_headless"),
            variable=self.headless_var
        )
        self.headless.pack(side="right", padx=5)
        
        # Кнопки действий
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
        
        # Кнопка запуска
        self.run_button = ctk.CTkButton(
            self.button_frame,
            text=self.localization.get("run_button"),  # ▶️ Run
            command=self.run_process
        )
        self.run_button.pack(side="left", padx=5)
        
        # Кнопка паузы
        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text=self.localization.get("pause_button"),  # ⏸️ Pause
            command=self.toggle_pause,
            state="disabled"
        )
        self.pause_button.pack(side="left", padx=5)
        
        self.is_paused = False

        self.load_profiles()

    def open_readme(self):
        readme_path = Path(__file__).parent.parent / "README.md"
        if os.path.exists(readme_path):
            webbrowser.open(readme_path.as_uri())
        else:
            self.show_error('README.md не найден!')

    def open_settings(self):
        """Открывает окно настроек API ключей"""
        from .settings_dialog import APISettingsDialog
        APISettingsDialog(self.root, self.localization, self)

    def browse_input(self):
        filename = ctk.filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if filename:
            self.input_file.delete(0, "end")
            self.input_file.insert(0, filename)

    def browse_output(self):
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            self.output_file.delete(0, "end")
            self.output_file.insert(0, filename)

    def load_profiles(self):
        try:
            config = Config.load()
            profile_names = list(config.profiles.keys())
            self.profile_combo.configure(values=profile_names)
            if profile_names:
                self.profile_var.set(profile_names[0])
                self.load_profile(profile_names[0])
        except Exception as e:
            self.show_error(f'Ошибка загрузки профилей: {str(e)}')

    def load_profile(self, profile_name: str):
        config = Config.load()
        profile = config.profiles[profile_name]
        
        self.prompt.delete("1.0", "end")
        self.prompt.insert("1.0", profile.prompt)
        
        self.columns.delete("1.0", "end")
        self.columns.insert("1.0", '\n'.join(profile.output_columns))
        
        model_name = f"{profile.model} - {self.localization.get(AVAILABLE_MODELS[profile.model].description_key)}"
        self.model_var.set(model_name)
        
        if profile.browser_config:
            self.parallel.set(profile.browser_config.max_parallel)
            self.headless_var.set(profile.browser_config.headless)
        
        if hasattr(profile, 'temperature'):
            self.temperature.set(profile.temperature)
            self.temp_label.configure(text=f"{profile.temperature:.1f}")

    def on_profile_change(self, choice):
        if choice:
            self.load_profile(choice)

    def new_profile(self):
        """Создает новый профиль на основе текущих данных"""
        current_data = {
            "prompt": self.prompt.get("1.0", "end").strip(),
            "output_columns": self.columns.get("1.0", "end").strip().split("\n"),
            "model": self.model_var.get().split(" - ")[0],
            "temperature": float(self.temperature.get()),
            "use_browser": bool(self.use_browser.get()),
            "browser_config": {
                "max_parallel": int(self.parallel.get()),
                "headless": bool(self.headless_var.get()),
                "timeout": 30
            }
        }
        
        dialog = ProfileDialog(
            self.root, 
            current_data=current_data,
            localization=self.localization,
            on_save=self.on_profile_saved
        )
        dialog.show()
    
    def on_profile_saved(self, profile_name: str):
        """Вызывается после сохранения профиля"""
        self.load_profiles()  # Обновляем список профилей
        self.profile_var.set(profile_name)  # Выбираем новый профиль
        self.load_profile(profile_name)  # Загружаем его данные

    def edit_profile(self):
        """Редактирует ыбранный профиль"""
        if not self.profile_var.get():
            self.show_error(self.localization.get("select_profile_error"))
            return
        
        from .profile_dialog import ProfileDialog
        ProfileDialog(self.root, self.profile_var.get(), self.localization)
        self.load_profiles()

    def show_error(self, message: str):
        """Показывает окно с ошибкой"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.localization.get("error_title"))
        dialog.geometry("400x150")
        dialog.transient(self.root)
        
        # Центрируем относительно главного окна
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Сообщение об ошибке
        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=350  # Перенос длинных строк
        ).pack(expand=True, padx=20, pady=(20, 10))
        
        # Кнопка OK
        ctk.CTkButton(
            dialog,
            text=self.localization.get("ok"),
            command=dialog.destroy
        ).pack(pady=(0, 20))

        # Ждем, пока окно станет видимым
        dialog.wait_visibility()
        
        # Теперь делаем его модальным
        dialog.grab_set()
        
        # Ждем закрытия окна
        dialog.wait_window()

    async def run_processor(self):
        processor = None  # Объявляем переменную до try блока
        try:
            config = Config.load()
            processor = DataProcessor(config)
            await processor.process_data()
            self.show_error(self.localization.get("processing_complete"))
        except Exception as e:
            self.show_error(f'Ошибка при обработке: {str(e)}')
        finally:
            if processor:
                await processor.browser_manager.cleanup()

    def run_process(self):
        """Запускает процесс обработки"""
        # Проверяем входной файл
        if not self.input_file.get():
            self.show_error(self.localization.get("no_input_file"))
            return
        
        if not os.path.exists(self.input_file.get()):
            self.show_error(self.localization.get("input_file_not_found"))
            return
        
        # Проверяем выходной файл
        if not self.output_file.get():
            self.show_error(self.localization.get("no_output_file"))
            return
        
        try:
            # Побуем создать директорию для выходного файла если её нет
            output_dir = os.path.dirname(self.output_file.get())
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        except Exception:
            self.show_error(self.localization.get("output_dir_error"))
            return
        
        # Проверяем наличие промпта и колонок
        if not self.prompt.get("1.0", "end").strip():
            self.show_error(self.localization.get("no_prompt"))
            return
            
        if not self.columns.get("1.0", "end").strip():
            self.show_error(self.localization.get("no_columns"))
            return
        
        # Проверяем модель и API ключи
        try:
            model_name = self.model_var.get().split(" - ")[0].strip()
            if not model_name:
                self.show_error(self.localization.get("select_model"))
                return
                
            model_config = AVAILABLE_MODELS[model_name]
            config = Config.load()
            
            if model_config.provider == "openai" and not config.api_keys.openai:
                self.show_error(self.localization.get("no_openai_key"))
                return
            elif model_config.provider == "anthropic" and not config.api_keys.anthropic:
                self.show_error(self.localization.get("no_anthropic_key"))
                return
            
            # Активируем кнопку паузы
            self.pause_button.configure(state="normal")
            
            # Запускаем обработку
            asyncio.run(self.run_processor())
            
        except KeyError:
            self.show_error(self.localization.get("invalid_model"))
        except Exception as e:
            self.show_error(str(e))
        finally:
            # Деактивируем кнопку паузы
            self.pause_button.configure(state="disabled")

    def run(self):
        self.root.mainloop()

    def toggle_browser_settings(self):
        """Включает/выключает настройки браузра"""
        enabled = bool(self.use_browser.get())
        state = "normal" if enabled else "disabled"
        
        self.parallel.configure(state=state)
        self.parallel_label.configure(state=state)
        self.headless.configure(state=state)

    def update_language(self):
        """Обновляет все тексты в интерфейсе"""
        self.root.title(self.localization.get("window_title"))
        
        # Обновляем все текстовые элементы
        for widget in [
            (self.top_frame.winfo_children()[0], "readme_button"),
            (self.top_frame.winfo_children()[-1], "settings_button"),
            # ... и так далее для всех текстовых элементов
        ]:
            if isinstance(widget[0], ctk.CTkButton):
                widget[0].configure(text=self.localization.get(widget[1]))
        
        # Обновляем метки
        for label, key in [
            (self.file_label_frame.winfo_children()[0], "input_file"),
            (self.output_label_frame.winfo_children()[0], "output_file"),
            # ... и так далее для всех меток
        ]:
            label.configure(text=self.localization.get(key))
        
        # Обновляем плейсхолдеры
        self.input_file.configure(
            placeholder_text=self.localization.get("file_select_placeholder")
        )
        self.output_file.configure(
            placeholder_text=self.localization.get("file_select_placeholder")
        )
        
        # Обновляем чекбоксы и их подсказки
        self.use_browser.configure(
            text=self.localization.get("online_search"),
            tooltip=self.localization.get("tooltip_online_search")
        )
        self.headless.configure(
            text=self.localization.get("headless_mode"),
            tooltip=self.localization.get("tooltip_headless")
        )

    def toggle_pause(self):
        """Переключает состояние паузы"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.configure(
                text=self.localization.get("resume_button")
            )
            self.show_status(self.localization.get("paused"))
        else:
            self.pause_button.configure(
                text=self.localization.get("pause_button")
            )
            self.show_status(self.localization.get("resumed"))

    def show_status(self, message: str):
        """Показывает статусное сообщение"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.localization.get("status_title"))
        dialog.geometry("400x150")
        dialog.transient(self.root)
        
        # Центрируем относительно главного окна
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Сообщение
        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=350
        ).pack(expand=True, padx=20, pady=(20, 10))
        
        # Кнопка OK
        ctk.CTkButton(
            dialog,
            text=self.localization.get("ok"),
            command=dialog.destroy
        ).pack(pady=(0, 20))

        dialog.wait_visibility()
        dialog.grab_set()
        dialog.wait_window()