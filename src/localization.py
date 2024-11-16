from typing import Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Localization:
    translations: Dict[str, Dict[str, str]]
    current_language: str = "en"
    
    @classmethod
    def load(cls, path: str = "localization.json") -> "Localization":
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Объединяем загруженные данные с дефолтными
                for lang in DEFAULT_TRANSLATIONS:
                    if lang not in data:
                        data[lang] = {}
                    data[lang].update(DEFAULT_TRANSLATIONS[lang])
                return cls(translations=data)
        except FileNotFoundError:
            # Возвращаем базовые переводы если файл не найден
            return cls(translations=DEFAULT_TRANSLATIONS)
    
    def get(self, key: str) -> str:
        """Получает перевод по ключу"""
        translation = self.translations.get(self.current_language, {}).get(
            key, 
            self.translations["en"].get(key, key)
        )
        if translation == key:  # Если перевод не найден
            print(f"Warning: Missing translation for key '{key}'")
        return translation
    
    def save(self, path: str = "localization.json"):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.translations, f, indent=4, ensure_ascii=False)
    
    def update_translations(self):
        """Обновляет словарь переводов дефолтными значениями"""
        for lang in DEFAULT_TRANSLATIONS:
            if lang not in self.translations:
                self.translations[lang] = {}
            self.translations[lang].update(DEFAULT_TRANSLATIONS[lang])

# Базовые переводы
DEFAULT_TRANSLATIONS = {
    "en": {
        # Заголовки окон
        "window_title": "Browser Assistant",
        "error_title": "Error",
        "status_title": "Status",
        "new_profile_title": "New Profile",
        "edit_profile_title": "Edit Profile",
        
        # Основные кнопки
        "readme_button": "📖 README",
        "settings_button": "⚙️ Settings",
        "browse_button": "Browse",
        "run_button": "▶️ Run",
        "pause_button": "⏸️ Pause",
        "resume_button": "▶️ Resume",
        "ok": "OK",
        "cancel": "Cancel",
        "save": "Save",
        "apply": "Apply",
        
        # Метки полей
        "input_file": "Input file (Excel/CSV):",
        "output_file": "Output file:",
        "profile": "Profile:",
        "prompt": "Prompt:",
        "output_columns": "Output columns:",
        "model": "Model:",
        "temperature": "Temperature:",
        "parallel_browsers": "Parallel browsers:",
        
        # Чекбоксы
        "online_search": "Online search",
        "headless_mode": "Background mode",
        
        # Плейсхолдеры
        "file_select_placeholder": "Select file...",
        
        # Описания моделей
        "model_gpt4o_mini_desc": "Fast and economical version of GPT-4",
        "model_gpt4o_desc": "Full GPT-4o version - balance of speed and capabilities",
        "model_claude3_sonnet_desc": "Claude 3.5 Sonnet - fast and powerful model from Anthropic",
        
        # Подсказки
        "tooltip_temperature": "Model creativity (0 - strict answers, 1 - maximum creativity)",
        "tooltip_online_search": "Enable to check actual information on websites.\nDisable for quick data processing using only LLM.",
        "tooltip_headless": "Browsers will work in background mode.\nConvenient for background work, but harder to track model actions.",
        
        # Сообщения об ошибках
        "no_input_file": "Please select input file",
        "input_file_not_found": "Input file not found",
        "no_output_file": "Please select output file",
        "output_dir_error": "Error creating output directory",
        "no_prompt": "Please enter prompt",
        "no_columns": "Please specify output columns",
        "select_model": "Please select model",
        "no_openai_key": "OpenAI API key is required for this model.\nPlease add it in Settings.",
        "no_anthropic_key": "Anthropic API key is required for this model.\nPlease add it in Settings.",
        "invalid_model": "Invalid model selected",
        
        # Статусы обработки
        "processing": "Processing...",
        "paused": "Processing paused",
        "resumed": "Processing resumed",
        "completed": "Processing completed",
        "processing_error": "Error during processing: {error}",
        
        # Работа с профилями
        "create_profile": "➕ Create",
        "edit_profile": "✏️ Edit",
        "profile_exists": "Profile with this name already exists.\nDo you want to overwrite it?",
        "profile_save_error": "Error saving profile",
        "profile_saved": "Profile saved successfully"
    },
    "ru": {
        # Заголовки окон
        "window_title": "Browser Assistant",
        "error_title": "Ошибка",
        "status_title": "Статус",
        "new_profile_title": "Новый профиль",
        "edit_profile_title": "Редактирование профиля",
        
        # Основные кнопки
        "readme_button": "📖 README",
        "settings_button": "⚙️ Настройки",
        "browse_button": "Обзор",
        "run_button": "▶️ Запустить",
        "pause_button": "⏸️ Пауза",
        "resume_button": "▶️ Продолжить",
        "ok": "OK",
        "cancel": "Отмена",
        "save": "Сохранить",
        "apply": "Применить",
        
        # Метки полей
        "input_file": "Входной файл (Excel/CSV):",
        "output_file": "Выходной файл:",
        "profile": "Профиль:",
        "prompt": "Промпт:",
        "output_columns": "Выходные колонки:",
        "model": "Модель:",
        "temperature": "Температура:",
        "parallel_browsers": "Параллельные браузеры:",
        
        # Чекбоксы
        "online_search": "Онлайн поиск",
        "headless_mode": "Работа в фоне",
        
        # Плейсхолдеры
        "file_select_placeholder": "Выберите файл...",
        
        # Описания моделей
        "model_gpt4o_mini_desc": "Быстрая и экономичная версия GPT-4",
        "model_gpt4o_desc": "Полная версия GPT-4o - баланс скорости и возможностей",
        "model_claude3_sonnet_desc": "Claude 3.5 Sonnet - быстрая и мощная модель от Anthropic",
        
        # Подсказки
        "tooltip_temperature": "Креативность модели (0 - строгие ответы, 1 - максимальная креативность)",
        "tooltip_online_search": "Включите для проверки актуальной информации на сайтах.\nОтключите для быстрой обработки данных только через LLM.",
        "tooltip_headless": "Браузеры будут работать в свернутом режиме.\nУдобно для фоновой работы, но сложнее отслеживать действия модели.",
        
        # Сообщения об ошибках
        "no_input_file": "Выберите входной файл",
        "input_file_not_found": "Входной файл не найден",
        "no_output_file": "Выберите выходной файл",
        "output_dir_error": "Ошибка создания директории для выходного файла",
        "no_prompt": "Введите промпт",
        "no_columns": "Укажите выходные колонки",
        "select_model": "Выберите модель",
        "no_openai_key": "Для этой модели требуется ключ OpenAI API.\nДобавьте его в Настройках.",
        "no_anthropic_key": "Для этой модели требуется ключ Anthropic API.\nДобавьте его в Настройках.",
        "invalid_model": "Выбрана некорректная модель",
        
        # Статусы обработки
        "processing": "Обработка...",
        "paused": "Обработка приостановлена",
        "resumed": "Обработка возобновлена",
        "completed": "Обработка завершена",
        "processing_error": "Ошибка при обработке: {error}",
        
        # Работа с профилями
        "create_profile": "➕ Создать",
        "edit_profile": "✏️ Изменить",
        "profile_exists": "Профиль с таким именем уже существует.\nПерезаписать его?",
        "profile_save_error": "Ошибка сохранения профиля",
        "profile_saved": "Профиль успешно сохра��ен"
    }
} 