from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage
import pandas as pd
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

from .browser_manager import BrowserManager
from .config import Config
from .models import get_model

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.profile = config.profiles[config.profile_name]
        self.model = get_model(config)
        self.browser_manager = None
        if self.profile.use_browser:
            self.browser_manager = BrowserManager(config)

    async def process_item_offline(self, item: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Обработка одной записи в офлайн режиме (только LLM)"""
        try:
            # Подставляем переменные в промпт
            formatted_prompt = prompt
            for key, value in item.items():
                formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
            
            # Отправляем запрос к модели
            response = await self.model.agenerate(
                messages=[[HumanMessage(content=formatted_prompt)]]
            )
            
            # Парсим JSON ответ
            result = json.loads(response.generations[0][0].text)
            return {**item, **result}
            
        except Exception as e:
            logger.error(f"Error processing item {item}: {str(e)}")
            return None

    async def process_data(self):
        """Основной метод обработки данных"""
        # Загружаем входные данные
        df = pd.read_excel(self.config.input_file) if self.config.input_file.suffix == '.xlsx' \
            else pd.read_csv(self.config.input_file)
        
        # Проверяем наличие необходимых колонок
        missing_columns = [col for col in self.profile.input_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Обрабатываем записи
        tasks = []
        for idx, row in df.iterrows():
            if self.profile.use_browser:
                # Онлайн режим с браузером
                controller_idx = idx % self.profile.browser_config.max_parallel
                tasks.append(
                    self.browser_manager.process_item(
                        row.to_dict(),
                        self.profile.prompt,
                        controller_idx
                    )
                )
            else:
                # Офлайн режим только с LLM
                tasks.append(
                    self.process_item_offline(
                        row.to_dict(),
                        self.profile.prompt
                    )
                )
        
        results = await asyncio.gather(*tasks)
        results = [r for r in results if r is not None]
        
        # Сохраняем результаты
        if results:
            output_df = pd.DataFrame(results)
            # Оставляем только нужные колонки в нужном порядке
            all_columns = df.columns.tolist() + self.profile.output_columns
            output_df = output_df[all_columns]
            output_df.to_excel(self.config.output_file, index=False)
            logger.info(f"Results saved to {self.config.output_file}")
        else:
            logger.warning("No results to save")

    async def cleanup(self):
        """Очистка ресурсов"""
        if self.browser_manager:
            await self.browser_manager.cleanup() 