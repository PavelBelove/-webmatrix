import asyncio
import json
from browser_use import Agent, Controller
from langchain_openai import ChatOpenAI
import pandas as pd
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanySearcher:
    def __init__(self, config_path: str = "config.json", max_parallel: int = 3):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.max_parallel = max_parallel
        self.companies_data = []
        self.semaphore = asyncio.Semaphore(max_parallel)
        
        # Создаем пул контроллеров
        self.controllers = [
            Controller(headless=True) for _ in range(max_parallel)
        ]
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1"
        )

    async def analyze_company(self, company: Dict, controller_idx: int) -> Dict[str, Any]:
        """Анализирует одну компанию"""
        async with self.semaphore:
            analysis_agent = Agent(
                task=f"""
                Follow these steps exactly:
                1. Type '{company['website']}' in the browser and press Enter
                2. Wait for the page to load
                3. If the page blocks access:
                   - Skip this company and continue with the next one
                4. Look for company information:
                   - Check footer links first (they often have location info)
                   - Look for "Contact", "About", "Locations", "Global Presence"
                   - Check for office locations in Brazil and Argentina
                5. If main page doesn't have enough info:
                   - Try "Contact" or "About" pages
                   - Look for "Global" or "International" sections
                6. Return as JSON with fields:
                   - has_offices (boolean)
                   - brazil_office (boolean)
                   - argentina_office (boolean)
                   - all_locations (list of strings)
                   - brief (string, max 500 chars)
                7. If blocked or error occurs, return:
                   {{"error": "access_blocked"}}
                """,
                llm=self.llm,
                controller=self.controllers[controller_idx]
            )
            
            try:
                company_data, _ = await analysis_agent.run()
                
                if isinstance(company_data, dict) and company_data.get('error') == 'access_blocked':
                    logger.warning(f"Access blocked for {company['website']}, skipping...")
                    return None
                
                return {
                    "name": company['name'],
                    "website": company['website'],
                    "has_offices": company_data.get('has_offices', False),
                    "brazil_office": company_data.get('brazil_office', False),
                    "argentina_office": company_data.get('argentina_office', False),
                    "all_locations": ", ".join(company_data.get('all_locations', [])),
                    "brief": company_data.get('brief', "Analysis failed")
                }
            except Exception as e:
                logger.error(f"Error analyzing {company['website']}: {str(e)}")
                return None

    async def search_and_analyze_companies(self, search_query: str) -> List[Dict[str, Any]]:
        """Ищет и анализирует компании для заданного региона"""
        logger.info(f"Starting search for: {search_query}")
        
        # Используем первый контроллер для поиска
        search_agent = Agent(
            task=f"""
            Follow these steps exactly:
            1. Type 'https://www.google.com' in the browser and press Enter
            2. Wait for the page to load
            3. Search for "{search_query} companies list directory"
            4. IMPORTANT: Avoid high-risk websites that often block bots:
               - Avoid F6S, Crunchbase, LinkedIn, AngelList
               - Prefer local business directories, government sites, or local fintech/retail associations
               - Look for comprehensive lists, not just "top" companies
            5. If a page blocks access or seems risky:
               - Go back to Google results
               - Try another source from the results
               - Repeat until you find an accessible source
            6. From the found source, extract as many companies as possible (not just top 5)
            7. For each company collect:
               - Company name
               - Official website URL (not social media profiles)
            8. Return the data as a JSON list with fields: name, website
            9. If no data was extracted, return to step 3 and try different search terms like:
               - "{search_query} business directory"
               - "{search_query} company registry"
               - "list of {search_query}"
            """,
            llm=self.llm,
            controller=self.controllers[0]
        )
        
        try:
            companies_data, _ = await search_agent.run()
            logger.info(f"Found companies: {companies_data}")
            
            if not companies_data:
                return []
            
            # Распределяем компании по контроллерам
            tasks = []
            for i, company in enumerate(companies_data):
                if 'website' not in company or not company['website']:
                    continue
                controller_idx = i % self.max_parallel
                tasks.append(self.analyze_company(company, controller_idx))
            
            # Запускаем анализ параллельно
            results = await asyncio.gather(*tasks)
            return [r for r in results if r is not None]
            
        except Exception as e:
            logger.error(f"Error in search process: {str(e)}")
            return []

    async def search_companies(self):
        """Основной метод поиска компаний"""
        tasks = []
        for query in self.config["search_queries"]:
            tasks.append(self.search_and_analyze_companies(query))
        
        results = await asyncio.gather(*tasks)
        for result_list in results:
            if result_list:
                self.companies_data.extend(result_list)

    def save_to_excel(self, filename: str = "companies_data.xlsx"):
        """Сохраняет результаты в Excel"""
        if not self.companies_data:
            logger.warning("No data to save")
            return
            
        df = pd.DataFrame(self.companies_data)
        df.to_excel(filename, index=False)
        logger.info(f"Results saved to {filename}")

    async def cleanup(self):
        """Закрывает все браузеры"""
        for controller in self.controllers:
            await controller.close()

async def main():
    load_dotenv()
    
    searcher = CompanySearcher(max_parallel=3)  # Запускаем 3 параллельных процесса
    try:
        await searcher.search_companies()
        searcher.save_to_excel()
    finally:
        await searcher.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 