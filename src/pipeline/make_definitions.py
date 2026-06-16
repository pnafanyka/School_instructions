from typing import Optional
from pathlib import Path
import logging

from src.pipeline.llm_worker import LLM_Worker
from src.pipeline.dummy import dummy_definitions
from src.pipeline.filters import DefinitionsCleaner
from src.pipeline.settings import settings

logger = logging.getLogger(__name__)


class DefinitionsMaker(LLM_Worker):

    def __init__(self, input_file: Optional[Path] = None, data: Optional[dict] = None):
        super().__init__()
        self.input_file = input_file
        self.data = data
        if not data and not self.input_file:
              raise ValueError("Необходимо задать либо путь к файлу, либо словарь данных.")
        self.system_prompt = settings.get_prompt_by_name("prompt_basic_concept_definition").text.format(
            domain=settings.domain,
            examples=settings.definition_generation_examples
        )

    def generate_definition_by_llm(self, data):
        result = {}
        for k, v in data.items():
            logger.info(f'Началась генерация для: {k}')
            result[k] = []
            for concept in v:
                response_text = self.generateLLMResponse(system_prompt=self.system_prompt, message=f'Term to define: {concept}', response_format=settings.definitions_response_format)
                if not response_text:
                    logger.warning('Пустой ответ, переходим дальше')
                    continue #TODO: добавить сюда ретраи вместо continue
                logger.info(f'Концепт: {concept}. Определение: {response_text}')
                
                if response_text:
                    result[k].append(response_text.strip())

        return result

    def run(self):
        if not self.data and self.input_file:
            data = self.read_json(self.input_file)
        elif not self.input_file and not self.data:
            raise Exception("Не переданы данные для обработки на шаге создания дефениций") 
        else: 
            data =self.data
        if self.validate_data(data):
            result = self.generate_definition_by_llm(data)
            # result = dummy_definitions()
            cleaner = DefinitionsCleaner(data=result)
            cleaned_result = cleaner.run_definition_cleaning()
            save_path = self._write_result(cleaned_result, settings.definitions_file_name)
            return result, save_path
        else:
            return None, None