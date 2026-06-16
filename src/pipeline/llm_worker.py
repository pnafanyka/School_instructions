import openai 
import json
import os
from dotenv import load_dotenv
import logging
from typing import Optional
from abc import abstractmethod


from src.pipeline.settings import settings


logger = logging.getLogger(__name__)

class LLM_Worker():

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("BASE_URL")
        self.project_settings = settings
        if api_key is None or base_url is None:
            logger.error('Переменные окружения не заданы или заданы некорректно. Проверьте API_KEY и BASE_URL')
            return None
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30
            )
        

    def validate_data(self, data):
        """
        Валидация JSON данных
        Проверяет, что данные - словарь, все значения - списки, 
        и эти списки содержат только строки
        """
        logger.info('Валидация json, переданного на вход')

        if not isinstance(data, dict):
            logger.error('❌ Ошибка: данные должны быть словарем')
            return False
        
        # Проверяем, что все значения - списки
        if not all(isinstance(data[key], list) for key in data.keys()):
            logger.error('❌ Ошибка: все значения должны быть списками')
            return False
        
        # Проверяем, что все элементы списков - строки
        for key, value_list in data.items():
            if not all(isinstance(item, str) for item in value_list):
                logger.error(f'❌ Ошибка в ключе "{key}": все элементы списка должны быть строками')
                return False
        
        logger.info('✅ JSON валидный')
        return True


    @staticmethod
    def read_json(file_path: str):
        parsed = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                parsed = json.load(f)
        except Exception as e:
            logger.error(f'Ошибка чтения json-файла: {e}')
        return parsed
    

    def _write_result(self, data, file_name):
        # Путь к папке step_results (на одном уровне с текущим файлом)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'step_results')
        
        # Создаем папку, если её нет
        os.makedirs(folder_path, exist_ok=True)
        
        # Сохраняем файл
        filepath = os.path.join(folder_path, file_name)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
        logger.info(f'✅ JSON сохранен: {filepath}')
        return filepath

    def generateLLMResponse(self, system_prompt: Optional[str],  message: str, response_format: dict, model: Optional[str] = None, tokenizer: Optional[str] = None):
        if system_prompt is None:
            system_prompt = self.system_prompt
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                messages=[
                    {"role": "system", "content": system_prompt}, #Reminder: при работе с Qwen3 проверять, что в систем_промптах есть /no_think
                    {"role": "user", "content": message}
                    ],
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                response_format=response_format
            )
            return response.choices[0].message.content
        except openai.APITimeoutError:
            logger.warning('Генерация завершена по таймауту')
            return None
        except Exception as e:
            logger.error(f'Ошибка при генерации: {e}')
            return None