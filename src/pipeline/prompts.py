from pydantic import BaseModel, Field

class Prompt(BaseModel):
    text: str
    name: str


class PromptSettings(BaseModel):

    prompt_basic_concept_mining: str = Field(
        default=(
            '''/no_think You are an expert in {domain}. Your task is to extract domain-specific terms from the given phrase.
            Extraction rules:
            - **Language**: Write in RUSSIAN language only.
            - **Source fidelity**: Extract ONLY terms explicitly present in the original phrase.
            - **No expansion**: Do not add new terms or extend meaning beyond the text.
            - **Holistic concepts**: Treat multi-word {domain} concepts as single terms (e.g., "lymphatic system" as one term).
            - **Separator**: Separate extracted terms with a period only.
            - **Domain focus**: Remove non-domain modifiers (e.g., phrases in parentheses unrelated to {domain}).
            - **No invention**: Never invent or infer terms absent from the source text.
            - **Conjunction handling**: Split terms connected by commas or conjunctions into separate period-delimited entries.
            - **Domain relevance**: Exclude terms unrelated to {domain}.
            - **Compound concepts**: Preserve composite domain concepts as single units (e.g., "gas exchange in the lungs" stays intact).
            - **Specialization**: Exclude general scientific terms (e.g., "research methods", "analysis", "safety rules"); keep only narrow domain-specific terms.
            - **Case normalization**: Convert all extracted terms to nominative case.
            - **Empty result**: If no valid terms exist, return a single space.
            - **Exclusion**: Never include the word "research" ("исследование") in extracted terms.
            - **Output format**: Return ONLY extracted terms in JSON-list; do not reproduce source phrases.
            Examples: {examples}
            '''
        ),
        exclude=True,
    )

    prompt_basic_concept_definition: str = Field(
        default=(
            '''/no_think You are an expert in {domain}. Your task is to write a strict and concise definition for the term.
            Definition requirements:
            - **Language**: Write in RUSSIAN language only.
            - **Style**: Encyclopedic, Wikipedia-like.
            - **Briefness**: The length of definintion should be maximum one to two sentences.
            - **Content**: Core essence only; no examples, explanations, or historical context.
            - **Template**: Start the definition with the exact template "... — это..." followed by your definition.
            - **No additions**: Do not include any text before or after the definition.
            -Examples: {examples}
            '''
        ),
        exclude=True,
    )

    prompt_basic_generate_bloom_tasks: str = Field(
        default=(
            '''/no_think You are a middle school {domain} teacher, previously you tought children about some concepts. Now you need to write a question, which tests
            an ability of a student to {cognitive_skill} (level: {skill_level}). Make a question which allows you to evaluate a skill levell of {skill_definition}
            Question template:
            {question_format}
            While making a question, follow strict rules:
            - **Language**: Write in RUSSIAN language only.
            - **Data limitation**: Question should be made on a base of given concept definition, you are not allowed to use any outside information.
            - **Clarity**: The question must be precise and relevant, without logical errors.
            - **Question only**: Question shouldn't include or refer to any texts, plots, pictures etc. Student can only see a question.
            - **Template**: You should strictly follow a question template.
            - **NO answer**: You shouldn't write any answer or clue inside your question.
            - **NO answer options**: This is not a multi-class classification question, so don't suggest any ansver options.
            - **Briefness**: The length of the question should not exceed two sentences.
            '''
        ),
        exclude=True,
    )

    prompt_basic_generate_bloom_answer: str = Field(
        default=(
            '''You are a {domain} expert. Your task is to write a strict and concise answer to the question. 
                    Rules:
                    - **Language**: Write in RUSSIAN language only.
                    - **Briefness**: Answer length no more than one to two sentences.
                    - **Vocabulary adequacy**: When in your answer you use some special to {domain} terms, make sure that they are included in the **concept list**. Don't use any difficult concepts if they are not included in the **concept list**.
                    - **Clarity**: The answer must be precise and relevant, without logical and factual errors.
                    **concept list**: {concept_set}
                    '''
        ),
        exclude=True
    )

    prompt_generate_instruction_and_answer: str = Field(
        default=(
            """
            '''/no_think You are a middle school {domain} teacher, previously you tought children about some concepts. Write a question-answer pair, which tests
            an ability of a student to {cognitive_skill} (level: {skill_level}). Make a question which allows you to evaluate a level of the skill ({skill_definition}). Question template: {question_format}
            Answer with JSON in the following format: 
            {{"question": "", "answer": ""}}
            While making pairs, follow strict rules:
            - **Language**: Write in RUSSIAN language only.
            - **Data limitation**: Question should be made on a base of given concept definition, you are not allowed to use any outside information.
            - **Clarity**: The question must be precise and relevant, without logical errors.
            - **Question only**: Question shouldn't include or refer to any texts, plots, pictures etc. Student can only see a question.
            - **Template**: You should strictly follow a question template.
            - **NO answer**: You shouldn't write any answer or clue inside your question.
            - **NO answer options**: This is not a multi-class classification question, so don't suggest any ansver options.
            - **Briefness**: The length of the question should not exceed two sentences.
            Examples: 
            {question_answer_examples}
            """
        ),
        exclude=True
    )
    
    prompt_basic_filter_concepts: str = Field(
        default=(
            """You are an expert curriculum evaluator for the subject "{domain}".
            Your task is to filter a list of extracted terms, deciding which ones are valid scientific concepts worth learning and which are noise.

            You must output a strictly valid JSON object with a single boolean field:
            {{"keep": true}}  OR  {{"keep": false}}

            ### CRITERIA FOR "keep": true

            1. **Core Concepts:** Fundamental terms, laws, theories, phenomena, and objects studied in {domain}.
            2. **Natural Processes:** Biological processes occurring in nature (e.g., {filter_relevant_examples}).
            3. **Specifics:** Terms that are specific enough to define a topic (e.g., {filter_relevant_whole_notion_examples}).

            ### CRITERIA FOR "keep": false (DELETE IMMEDIATELY)

            1. **Learning Activities (The "Student Action" Rule):** Any term describing what a student *does* rather than what they *study*.
            - DELETE: "Наблюдение", "Измерение, "Вычисление", "Нахождение", "Сравнение", "Описание", ...
            2. **Classroom Logistics & Meta-Data:**
            - DELETE: "Лабораторная работа", "Демонстрация", "Опыт" (as a generic activity), "Правила безопасности", "Домашняя работа", "ГДЗ".
            - DELETE: Parsing artifacts like "Раздел 1", "Глава 3", "Страница 10", URLs, single letters, initials.
            3. **Too General / Non-Domain:**
            - DELETE: General words lacking context: "Список", "Таблица", "Система", "Проблема", "Факт", "Гипотеза" (unless specific like "Гипотеза Авогадро"), "Объект", "Тело" (unless something like "Физическое тело").
            - DELETE: "Экскурсия", "Парк", "Сквер", "Оборудование" (generic)."""
        ),
        exclude=True
    )

    def get_prompt_by_name(self, prompt_name: str):
        text = (
            getattr(self, f"prompt_{prompt_name}"
            if not prompt_name.startswith("prompt_")
            else prompt_name
            )
        )
        return Prompt(text=text, name=prompt_name)
