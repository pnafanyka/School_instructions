from typing import Optional
import logging 
import json
from pathlib import Path
from operator import itemgetter

from src.pipeline.llm_worker import LLM_Worker
from src.pipeline.dummy import dummy_instructions
from src.pipeline.settings import settings

logger = logging.getLogger(__name__)

class InstructionsMaker(LLM_Worker):

    def __init__(self, input_file: Optional[Path] = None, data: Optional[dict] = None):
        super().__init__()
        self.input_file = input_file
        self.data = data
        if not data and not self.input_file:
              raise ValueError("Необходимо задать либо путь к файлу, либо словарь данных c прошлого шага.")
        self.file_name = settings.instructions_file_name
    
    def validate_output_json(self, str_obj: str):
        try:
            obj = json.loads(str_obj)
        except:
            logger.warning(f'В ответе не json-объект: {str_obj}')
            return False, {'out': str_obj}
        
        if 'answer' in obj.keys() and 'question' in obj.keys():
            if isinstance(obj['answer'], str) and isinstance(obj['question'], str):
                return True, obj
            else: 
                logger.warning(f'В значениях не str: {obj}')
                return False, {'out': obj}
        else:
            logger.warning(f'Не хватило ключей: {obj}')
            return False, {'out': obj}

    def new_generate_instructions(self, parsed): 
        logger.info("Началась генерация инструкций")
        result = {}
        gen_id = 1
        for el in parsed:
            result[el] = []
            if settings.instructions_process_batch:
                pass
            for idx, definition in enumerate(parsed[el]): 
                category_group_idx = idx % 4
                getter = itemgetter(*settings.category_groups_mask[category_group_idx]) # itemgetter по маске забирает только элементы с нужным индексом из списка
                for category in getter(settings.cognitive_categories):
                    system_prompt = settings.get_prompt_by_name("prompt_generate_instruction_and_answer").text.format(
                        domain=settings.domain,
                        cognitive_skill=category[0],
                        skill_level=category[1],
                        skill_definition=category[2], 
                        question_format=category[3],
                        question_answer_examples=settings.question_answer_examples
                    )
                    response_text = self.generateLLMResponse(system_prompt=system_prompt, message=f'Definition: {definition}', response_format=settings.instructions_response_format)
                    if not response_text:
                        logger.warning('Пустой ответ, переходим дальше')
                        continue #TODO: добавить сюда ретраи
                    flag, validation = self.validate_output_json(response_text)
                    if flag: # добаляем в словарь еще уникальный id, определение и когн. категорию
                        validation['success'] = True
                        validation['id'] = gen_id
                        validation['state'] = category
                        validation['definition'] = definition

                        result[el].append(validation)
                        gen_id += 1
                    else:
                        validation['success'] = False
                        validation['id'] = gen_id
                        validation['state'] = category
                        validation['definition'] = definition

                        result[el].append(validation)
                        gen_id += 1
        return result


    def run(self):
        if not self.data and self.input_file:
            self.data = self.read_json(self.input_file)
        elif not self.input_file and not self.data:
            raise Exception("Не переданы данные для обработки на шаге создания инструкций") 
        if self.validate_data(self.data):
            result = self.new_generate_instructions(self.data)
            save_path = self._write_result(result, self.file_name)
            return result, save_path
        else:
            return None, None