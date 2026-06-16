from pathlib import Path

import logging

from pipeline.extract_concepts import ConceptExtractor
from pipeline.make_definitions import DefinitionsMaker
from pipeline.make_instructions import InstructionsMaker
from src.pipeline.settings import settings

logger = logging.getLogger(__name__)

STEPS = {
    'extract_concept': ConceptExtractor,
    'make_definitions': DefinitionsMaker,
    'make_instructions': InstructionsMaker
    }


class Pipeline:
    def __init__(self, input_file: str):
        self.steps = []
        self.input_file = Path(input_file)
        assert self.input_file.exists()

    
    # Метод добавления шага в pipeline
    def add_step(self, step_name):
        if step_name in STEPS:
            processor_class = STEPS[step_name]
            self.steps.append(processor_class)
            logger.info(f'В пайплайн добавлен шаг: {step_name}')
        else:
            raise ValueError(f'Шаг {step_name} отсутствует')
        
    def run(self):
        result = None
        for step in self.steps:
            print(f'Запущен этап: {type(step).__name__}')
            if result:
                step_instance = step(data=result)
                result, path = step_instance.run()
                logger.info(f'Результат щага сохранен по пути: {path}')
            else:
                step_instance = step(input_file=self.input_file)
                result, path = step_instance.run()
            if result is None: #TODO: исправить логику: если result None, то тогда не приходит два объекта строкой выше
                print(f'Не пришел ответ на шаге: {type(step).__name__}')
                return None
        return result


if __name__ == '__main__':

    # input_file = '/Users/andrejpihtin/учеба/комп_мага/InstructionTuningRussian/география10-11.pdf'
    # input_file = settings.pdf_path

    # input_file = '/Users/andrejpihtin/учеба/комп_мага/InstructionTuningRussian/src/pipeline/step_results/definitions.json'
    input_file = '/Users/andrejpihtin/учеба/комп_мага/InstructionTuningRussian/src/pipeline/step_results/definitions_11.json'
    pipe = Pipeline(input_file)

    # # Регистрация последовательности шагов
    # pipe.add_step('extract_concept')   # Извлекаем понятия
    # pipe.add_step('make_definitions') # Создаем дефиниции
    pipe.add_step('make_instructions') # Генерируем инструкции

    # Обрабатываем файл
    processed_data = pipe.run()
    print(processed_data)
