import pymupdf
import re
import logging
from typing import Optional
from pathlib import Path
import json

from src.pipeline.llm_worker import LLM_Worker
from src.pipeline.dummy import dummy_concepts
from src.pipeline.filters import ConceptFiltrator

from src.pipeline.settings import settings

logger = logging.getLogger(__name__)

class ConceptExtractor(LLM_Worker):

    def __init__(self, batch_size=15, input_file: Optional[Path] = None):
        super().__init__()
        self.batch_size = batch_size
        self.input_file = input_file
        self.system_prompt = settings.get_prompt_by_name("prompt_basic_concept_mining").text.format(
                    domain = settings.domain,
                    examples = settings.concept_gen_examples
                )
        
    
    ####### два метода ниже отвечают за парсинг пдф-файла с материалами
    def _pdf2text(self):
        """
        парсинг .pdf файла
        """
        doc = pymupdf.open(self.input_file)
        result = []
        for page in doc:
            p = page.get_text('text')
            result.append(p)
        text = '\n'.join(result)
        return text
    
    
    def _parse_program(self):
        text = self._pdf2text()
        classes_dict = {}

        clean_text = re.sub(r'=+ Page \d+ =+', '', text)
        clean_text = re.sub(r'Федеральная рабочая программа.*?\n', '', clean_text)
        clean_text = re.sub(r'СОДЕРЖАНИЕ ОБУЧЕНИЯ', '', clean_text)
        clean_text = re.sub(r'\*\*', '', clean_text)
        clean_text = clean_text.split('ПРЕДМЕТНЫЕ РЕЗУЛЬТАТЫ')[0]
        
        class_blocks = re.split(r'(\d+)\s+КЛАСС', clean_text)
        
        for i in range(1, len(class_blocks), 2):
            class_num = class_blocks[i]
            class_content = class_blocks[i+1] if i+1 < len(class_blocks) else ""
            class_content = ' '.join(class_content.split())
            class_content_list = re.split(r'\.|\?', class_content)

            classes_dict[f"{class_num} класс"] = class_content_list

        return classes_dict
    #########
    

    def parseByLLM(self, data):
        result = {}
        all_seen_terms = set()

        for class_name, phrases_list in data.items():
            result[class_name] = []
            logger.info(f'Началась генерация для: {class_name}')
            
            for i in range(0, len(phrases_list), self.batch_size):
                batch = phrases_list[i:i + self.batch_size]
                phrases_text = '||'.join(batch)
                
                response_text = self.generateLLMResponse(system_prompt=self.system_prompt, message=f'Phrases: {phrases_text}', response_format=settings.concepts_response_format)
                if not response_text:
                    logger.warning('Пустой ответ, переходим дальше')
                    continue #TODO: добавить сюда ретраи
                logger.info(f'Извлеченные концепты: {response_text}')
                try:
                    response_obj = json.loads(response_text)

                    if isinstance(response_obj, dict):
                        concept_list = response_obj.get('extracted_terms', None)
                        if not concept_list:
                            logger.warning('Получил пустой concept_list')
                            continue
                        logger.info(f'Извлек следующие концепты: {concept_list}')                        
                    elif isinstance(response_obj, list):
                        if not response_obj:
                            logger.warning('Получил пустой response_obj')
                            continue
                        logger.info(f'Извлек следующие концепты: {response_obj}') 
                    else:
                        logger.warning('Пришел неопознанный ответ')
                        continue
                except Exception as e:
                    logger.warning(f'Ошибка в чтении json-строки')
                    continue
                for concept in concept_list:
                    concept = concept.strip().lower()
                    if concept not in all_seen_terms:
                        result[class_name].append(concept)
                        all_seen_terms.add(concept)
        return result


    def run(self):
        if '.json' in self.input_file._str:
            data = self.read_json(self.input_file)
        elif '.pdf' in self.input_file._str:
            data = self._parse_program()
            # data = dummy_concepts()
        if self.validate_data(data):
            result = self.parseByLLM(data)
            filtrator = ConceptFiltrator(data = result)
            filtered_result = filtrator.run_concept_filtration()
            save_path = self._write_result(filtered_result, settings.concepts_file_name)
            return result, save_path
        else:
            return None, None