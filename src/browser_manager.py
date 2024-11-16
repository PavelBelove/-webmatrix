from browser_use import Agent, Controller
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, config: "Config"):
        self.config = config
        self.controllers = [
            Controller(headless=config.browser_config.headless) 
            for _ in range(config.browser_config.max_parallel)
        ]
        self.semaphore = asyncio.Semaphore(config.browser_config.max_parallel)
        
        self.llm = ChatOpenAI(
            api_key=config.openai_key,
            model="gpt-4-turbo-preview",
            temperature=0
        )
    
    async def process_item(self, item: Dict[str, Any], prompt: str, controller_idx: int) -> Dict[str, Any]:
        """Process single item using browser"""
        async with self.semaphore:
            # Replace variables in prompt
            formatted_prompt = prompt
            for key, value in item.items():
                formatted_prompt = formatted_prompt.replace(f"{{{key}}}", str(value))
            
            agent = Agent(
                task=formatted_prompt,
                llm=self.llm,
                controller=self.controllers[controller_idx]
            )
            
            try:
                result, _ = await agent.run()
                return {**item, **result}
            except Exception as e:
                logger.error(f"Error processing item {item}: {str(e)}")
                return None
    
    async def cleanup(self):
        """Close all browser instances"""
        for controller in self.controllers:
            await controller.close() 