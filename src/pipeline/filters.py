import logging

from pymystem3 import Mystem
import re
import json

from src.pipeline.llm_worker import LLM_Worker
from src.pipeline.settings import settings

logger = logging.getLogger(__name__)

class ConceptFiltrator(LLM_Worker):

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.mystem = Mystem()
        self.system_prompt = settings.get_prompt_by_name('prompt_basic_filter_concepts').text.format(
            domain = settings.domain,
            filter_relevant_examples = settings.filter_relevant_examples,
            filter_relevant_whole_notion_examples = settings.filter_relevant_whole_notion_examples
        )

    def clean_concept_text(self, text: str) -> str:
        # Удаляем всё в круглых скобках, чтобы укоротить слишком длинное
        text = re.sub(r'\s*\(.*?\)', '', text)
        # Удаляем множественные пробелы и стрипим
        return " ".join(text.split())


    def get_normalized_key(self, text: str) -> str:
        """
        Превращает концепт в нормализованный ключ для поиска дубликатов.
        """
        # Базовая очистка
        clean_text = self.clean_concept_text(text).lower()

        # Лемматизируем
        lemmas = self.mystem.lemmatize(clean_text)

        # Фильтрация: оставляем только слова длиной > 2 символов
        significant_words = [
            lemma.strip() for lemma in lemmas
            if lemma.strip() and len(lemma.strip()) > 2
        ]

        # Сортировка, чтобы не учитывать порядок слов
        significant_words.sort()

        return " ".join(significant_words)

    def deduplicate_concepts(self):
        logger.info('Начинается дедупликация концептов')
        deduplicated_data = {}
        stats = {
                "total_input": 0,
                "kept": 0,
                "deleted_short": 0,    # Слишком короткие (менее 3 букв после очистки)
                "deleted_duplicate": 0  # Дубликаты внутри домена
        }
        deduplicated_data = {}

        # Сет для хранения нормализованных ключей ВНУТРИ ДОМЕНА
        seen_lemmas_in_domain = set()
        for key, values in self.data.items():
            cleaned_terms_for_grade = []
            for term in values:
                stats["total_input"] += 1
                ## Очистка скобок для итогового сохранения
                display_term = self.clean_concept_text(term)
                # Получение ключа для проверки
                norm_key = self.get_normalized_key(term)
                # Проверка: если после очистки от инициалов и предлогов ничего не осталось
                # (или исходное слово было коротким, типа "pH" или "О")
                if not norm_key:
                    stats["deleted_short"] += 1
                    continue
                # Проверка на дубликат
                if norm_key in seen_lemmas_in_domain:
                    stats["deleted_duplicate"] += 1
                else:
                    seen_lemmas_in_domain.add(norm_key)
                    cleaned_terms_for_grade.append(display_term)
                    stats["kept"] += 1
                        # Сохраняем результат для класса, если список не пуст
            if cleaned_terms_for_grade:
                deduplicated_data[key] = cleaned_terms_for_grade
            else:
                logger.warning('После фильтрации не осталось концептов')
        logger.info(f'Статистика дедупликация: {stats}')
        return deduplicated_data

    def llm_filter_concepts(self, deduplicated_data: dict):
        logger.info('Начинается фильтрация концпетов при помощи LLM')
        deduplicated_data = self.deduplicate_concepts()
        data_kept = {}
        data_deleted = {}
        for key, values in deduplicated_data.items():
            concepts_to_keep = []
            deleted = []
            for term in values:
                response_text = self.generateLLMResponse(system_prompt=self.system_prompt, message=f'Input: {term}', response_format=settings.concept_filtration_response_format)

                try:
                    result = json.loads(response_text)
                    verdict = result.get("keep", "ERROR")
                    if verdict:
                        concepts_to_keep.append(term)
                        logger.info(f'Сохранили концепт: {term}')
                    else: 
                        deleted.append(term)
                        logger.warning(f'Удалили концепт: {term}')
                except json.JSONDecodeError:
                    logger.error(f'В ответе фильтрации концептов не прочитался json, концепт: <{term}>')
                    continue
            data_kept[key] = concepts_to_keep
            data_deleted[key] = deleted
        self._write_result(data=data_deleted, file_name=self.project_settings.deleted_concepts_file_name)
        logger.info(f'Удаленные концепты сохранены в файл: {self.project_settings.deleted_concepts_file_name}')
        return data_kept


    def run_concept_filtration(self):
        deduplicated_data = self.deduplicate_concepts()
        llm_filtered_data = self.llm_filter_concepts(deduplicated_data=deduplicated_data)
        return llm_filtered_data


class DefinitionsCleaner():

    def __init__(self, data: dict):
        self.data = data
        self.cjk_any = re.compile(r"[\u4e00-\u9fff]")
        self.pure_latin_seq = re.compile(r"\b[A-Za-z]{2,}\b")

        self.math_context = re.compile(r"[=+\-*/^×÷<>≈≤≥∝√∑∫∞]|\d")

        self.mixed_token = re.compile(
            r"(?<![A-Za-zА-Яа-яЁё])"
            r"(?=[A-Za-zА-Яа-яЁё]*[A-Za-z])"
            r"(?=[A-Za-zА-Яа-яЁё]*[А-Яа-яЁё])"
            r"[A-Za-zА-Яа-яЁё]+"
            r"(?![A-Za-zА-Яа-яЁё])"
        )

        self.scientific_patterns = [
            r"[A-Z][a-z]?\d*",
            r"\([IVX]+\)",
            r"\b[sSpPdDfF]-[а-яА-ЯЁё]+\b"
        ]

        self.latin_to_cyr = str.maketrans({
            "a":"а","c":"с","e":"е","o":"о","p":"р","x":"х","y":"у",
            "k":"к","m":"м","t":"т","h":"н","i":"и","l":"л",
            "A":"А","B":"В","C":"С","E":"Е","H":"Н","K":"К",
            "M":"М","O":"О","P":"Р","T":"Т","X":"Х","Y":"У",
        })

    def protect_patterns(self, text):
        protected = []
        result = text

        for pattern in self.scientific_patterns:
            for m in re.finditer(pattern, result):
                placeholder = f"__PROT_{len(protected)}__"
                protected.append(m.group())
                result = result.replace(m.group(), placeholder, 1)

        return result, protected


    def restore_patterns(self, text, protected):
        for i, p in enumerate(protected):
            text = text.replace(f"__PROT_{i}__", p)
        return text


    def fix_mixed(self, m):
        return m.group(0).translate(self.latin_to_cyr)


    def drop_latin(self, m, text):
        start, end = m.span()
        window = text[max(0, start-3):min(len(text), end+3)]

        if self.math_context.search(window):
            return m.group(0)

        return ""    

    def clean_text(self, text):

        orig = text

        # удалить иероглифы
        text = self.cjk_any.sub("", text)

        # защитить научные конструкции
        text, protected = self.protect_patterns(text)

        # исправить смешанные слова
        text = re.sub(self.mixed_token, self.fix_mixed, text)

        # удалить английские слова
        text = re.sub(self.pure_latin_seq, lambda m: self.drop_latin(m, text), text)

        # вернуть научные паттерны
        text = self.restore_patterns(text, protected)

        # нормализовать пробелы
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"\s+—\s+", " — ", text)

        text = text.strip()

        if text != orig:
            logger.warning(f"Было: {orig}")
            logger.warning(f"Стало: {text}")
        return text

    def run_definition_cleaning(self):
        cleaned_data = {}
        for grade in self.data:
            cleaned_data[grade] = [self.clean_text(t) for t in self.data[grade]]
        return cleaned_data


class InstructionFiltrator():
    pass