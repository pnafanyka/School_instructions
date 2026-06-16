import logging
import datetime as dt
from pathlib import Path

from typing import Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.pipeline.prompts import Prompt, PromptSettings


logger = logging.getLogger(__name__)

class ProjectSettings(BaseSettings, PromptSettings):
    # path settings
    path_root: Path = Path(__file__).parents[1]
    path_logs: Path = path_root / "logs"
    path_logs_file: Path = (
        path_logs / f"{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )

    instructions_process_batch: bool =  True
    batch_size: int = 15

    concepts_response_format: Optional[dict] ={
        "type": "json_object",
        "json_schema": {
            "type": "object",
            "properties": {
                "extracted_terms": {"type": "list"},
            },
            "required": ["extracted_terms"]
            }
        }
    
    definitions_response_format: Optional[dict] = {"type": "text"}

    instructions_response_format: Optional[dict] ={
        "type": "json_object",
        "json_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "str"},
                "answer": {"type": "str"}
            },
            "required": ["question", "answer"]
            }
        }

    concept_filtration_response_format: Optional[dict] ={
        "type": "json_object",
        "json_schema": {
            "type": "object",
            "properties": {"keep": {"type": "bool"}},
            "required": ["keep"]
         }
    }
    

    # PDF - учебника
    pdf_path: Optional[str] = '/Users/andrejpihtin/учеба/комп_мага/InstructionTuningRussian/география5-9.pdf'

    # logging setting
    log_level: int = logging.INFO

    # domain setting
    domain: Optional[str] = 'geography'

    #Названия файлов по умолчанию для сохранения промежуточных результатов
    concepts_file_name: Optional[str] = 'concepts.json'
    deleted_concepts_file_name: Optional[str] = 'deleted_concepts.json'
    definitions_file_name: Optional[str] = 'definitions.json'
    instructions_file_name: Optional[str] = 'instructions.json'

    # Setting examples for concept generation
    concept_gen_examples: Optional[tuple] = (
            "Input: Литосфера — твёрдая оболочка Земли. || Круговорот воды в природе || Формы рельефа: горы и равнины. Output: {'extracted_terms': ['Литосфера', 'Круговорот воды в природе', 'Формы рельефа', 'Горы', 'Равнины']}",
            "Input: Климатообразующие факторы и типы климата России. || Географическое положение и исследование Африки. Output: {'extracted_terms': ['Климатообразующие факторы', 'Типы климата России', 'Географическое положение Африки']}",
            "Input: Строение вулкана и типы извержений. || Урбанизация и расселение населения. Output: {'extracted_terms': ['Вулкан', 'Типы извержений', 'Урбанизация', 'Расселение населения']}",
            "Input: Отрасли мирового хозяйства: Промышленность, Сельское хозяйство, Транспорт. Output: {'extracted_terms': ['Отрасли мирового хозяйства', 'Промышленность', 'Сельское хозяйство', 'Транспорт']}"
        )
    
    filter_relevant_whole_notion_examples: Optional[str] = 'Строение коры земли - OK, но Строение - не подходит'# Нужна строка с примером, что такое полный пример, а что не полный: 'Строение клетки OK строение NO'
    filter_relevant_examples: Optional[str] = 'Урбанизация, морские течения, эрозия почвы'

    cognitive_categories: Optional[list] = [
        ['remember information','easy','identifying knowledge in long-term memory that corresponds to the presented material','Verification question in which some information is provided and it is necessary to determine whether it is correct or not (e.g.: "Верно ли, что митохондрии — это органоиды эукариотических клеток?" or "Верно ли, что митохондрии — это НЕ органоиды эукариотических клеток?").'],
        ['remember information','easy','identifying knowledge in long-term memory that corresponds to the presented material','Classification task: assign each given term to its correct category based on memorized facts (e.g., "Отнесите организмы: амёба, дуб, гриб к царствам: Протисты, Растения, Грибы"). Not MCQ.'],
        ['remember information','easy','retrieving relevant information from long-term memory','Constructed-response question providing no hints or accompanying information (e.g.: "Что такое митохондрия?").'],
        ['remember information','easy','retrieving relevant information from long-term memory','Fill-in-the-blank question/task providing several hints (e.g.: "Митохондрии — это органоиды эукариотических клеток, отвечающие за ___.").'],
        ['understand information','medium','converting from one form of representation (e.g., descriptive) to another (e.g., taxonomic)','Constructed-response question where information is presented in one form and must be represented in another form (e.g.: "Напишите таксономическую классификацию (тип, класс, отряд) для организма, описанного как: позвоночное с перьями, теплокровный метаболизм и передние конечности, модифицированные в крылья.").'],
        ['understand information','medium','finding a specific example of a concept or principle','Constructed-response question requiring an example (e.g.: "Приведите пример неорганического соединения и объясните, почему оно является неорганическим.").'],
        ['understand information','medium','determining that something belongs to a specific category (e.g., a concept or principle)','Constructed-response question providing a specific example where it is necessary to identify the corresponding concept or principle from a given list (e.g.: "Какое из перечисленных далее животных является ракообразным (ответ обоснуйте): краб, паук, муравей").'],
        ['understand information','medium','determining that something belongs to a specific category (e.g., a concept or principle)','Sorting question/task providing a set of examples/objects where it is necessary to determine which belong to the specified category and which do not, OR assign each example/object to one of several categories (e.g.: "Какие из перечисленных далее животных относятся к паукообразным: скорпион, клещ, муравей, стрекоза").'],
        ['understand information','medium','summarizing the general theme or main points','Constructed-response question related either to themes or to summaries/abstracts. Themes are more abstract than summaries. For example, in a constructed-response task a student might be asked to read a sentence and then write one to two key words for it (e.g.: "Шесть ног, хитиновый покров и метаморфоз — ключевые вехи их жизненного цикла. О ком идет речь в предложении?")'],
        ['understand information','medium','drawing a logical inference from the presented information','Completion question/task where the user is given a series of elements and must determine what comes next (e.g., "Пауки, клещи, скорпионы, ... Продолжите ряд и назовите общий класс этих животных.").'],
        ['understand information','medium','drawing a logical inference from the presented information','Hierarchical-analogy task: given a part-whole or category-example pair, complete the parallel pair (e.g., "Нейрон является структурной единицей нервной ткани, а нефрон (по аналогии) — структурной единицей _______"). Answer: one term.'],
        ['understand information','medium','drawing a logical inference from the presented information','Odd-one-out question/task where the user is given three or more items and must determine which one does not belong (e.g., "Пауки, клещи, муравьи, скорпионы - какое животное лишнее (ответ аргументируйте)"). The question must not be in multiple-choice format.'],
        ['understand information','medium','detecting correspondences between two ideas, objects, etc.','Matching question/task requiring demonstration of how each part of one object, idea, problem, or situation corresponds to (or maps onto) each part of another (e.g., "Сопоставьте структуры жабр рыбы и лёгких млекопитающих как органов газообмена: жаберные лепестки - альвеолы, жаберные дуги - бронхиальное дерево, кровеносные капилляры - капиллярная сеть вокруг альвеол. Объясните, как каждая пара обеспечивает эффективный газообмен.").'],
        ['understand information','medium','constructing a cause-effect model of a system','Reasoning question/task asking you to explain the cause of a given event (e.g., "Почему у растений, растущих в тени, листья обычно крупнее и тоньше, чем у растений на солнце (адоптивное значение)?").'],
        ['understand information','medium','constructing a cause-effect model of a system','Troubleshooting question/task asking the user to determine what might have gone wrong in a malfunctioning system (e.g., "В эксперименте по фотосинтезу лист элодеи помещают в воду под светом, но пузырьки кислорода не выделяются. Назовите любую возможную отсутствия газообразования.").'],
        ['understand information','medium','constructing a cause-effect model of a system','System modification question/task asking the user to modify a system to achieve a certain goal (e.g., "Как изменить состав почвы, чтобы растение быстрее зацвело?").'],
        ['understand information','medium','constructing a cause-effect model of a system','Prediction question/task asking how a change in one part of a system will affect another part (e.g., "Что произойдёт с численностью зайцев в лесу через 2 года, если резко сократить популяцию волков?").'],
        ['apply information','difficult','applying an operation to a familiar task','Algorithm execution question/task presenting a familiar problem solvable by a known procedure (e.g.: "Определите генотипы родителей по фенотипам потомства, используя решётку Пеннета: при скрещивании двух чёрных морских свинок в потомстве появилось 3 чёрных и 1 белый детёныш. Аллель чёрной окраски доминирует над белой.").'],
        ['apply information','difficult','applying an operation to an unfamiliar task','Algorithm execution question/task presenting an unfamiliar problem that must be solved. Begin by specifying the problem. Then ask to identify the procedure required to solve the problem, solve the problem using the chosen procedure (making adjustments as necessary), or generally both (e.g., "Вам дан препарат с неизвестными клетками, содержащими зелёные пластиды и крупную центральную вакуоль. Примените алгоритм дифференциации растительных и животных клеток по трём признакам и определите тип клеток.")'],
        ['remember information','easy','identifying knowledge in long-term memory that corresponds to the presented material','Sequencing task: arrange the given elements in the correct factual order (e.g., "Упорядочите этапы митоза: профазу, метафазу, анафазу, телофазу").'],
        ['understand information','medium','drawing a logical inference from the presented information','Pattern task: given 2-3 factual examples, name the shared principle they illustrate (e.g., "Что объединяет: испарение воды, плавление льда, сублимацию йода? Назовите одним термином").'],
        ['understand information','medium','drawing a logical inference from the presented information','Analogy-interpretation task: given a complete analogy, state the shared logical relation (e.g., "Митоз обеспечивает деление соматических клеток, а мейоз — деление половых клеток. Какой общий процесс лежит в основе сравнения этих двух терминов?").']
    ]

    category_groups_mask: Optional[list] = [
            (0, 4, 5, 7, 13, 17),   # ctr = 0
            (1, 6, 8, 14, 18, 21),      # ctr = 1
            (2, 9, 11, 15, 17, 19),     # ctr = 2 
            (3, 10, 12, 16, 18, 20)     # ctr = 3 
        ]
    bloom_task_types: Optional[dict] = {
        "easy":
            ["remember information; easy; identifying knowledge in long-term memory that corresponds to the presented material; Verification question in which some information is provided and it is necessary to determine whether it is correct or not (e.g.: ###_EXAMPLES_###').",
            "remember information; easy; identifying knowledge in long-term memory that corresponds to the presented material; Matching question/task presenting two lists, where it is necessary to determine how each element from one list corresponds to some element from the other list (e.g., ###_EXAMPLES_###). Each list must strictly include two or more elements (not only one option in each list!). But not a multiple-choice question (MCQ).",
            "remember information; easy; retrieving relevant information from long-term memory; Constructed-response question providing no hints or accompanying information (e.g.: ###_EXAMPLES_###).",
            "remember information; easy; retrieving relevant information from long-term memory; Fill-in-the-blank question/task providing several hints (e.g.: ###_EXAMPLES_###)."],
        "medium": 
            ["understand information; medium; converting from one form of representation (e.g., descriptive) to another (e.g., taxonomic); Constructed-response question where information is presented in one form and must be represented in another form (e.g.: ###_EXAMPLES_###).",
            "understand information; medium; finding a specific example of a concept or principle; Constructed-response question requiring an example (e.g.: ###_EXAMPLES_###).",
            "understand information; medium; determining that something belongs to a specific category (e.g., a concept or principle); Constructed-response question providing a specific example where it is necessary to identify the corresponding concept or principle from a given list (e.g.: ###_EXAMPLES_###).",
            "understand information; medium; determining that something belongs to a specific category (e.g., a concept or principle); Sorting question/task providing a set of examples/objects where it is necessary to determine which belong to the specified category and which do not, OR assign each example/object to one of several categories (e.g.: ###_EXAMPLES_###).",
            "understand information; medium; summarizing the general theme or main points; Constructed-response question related either to themes or to summaries/abstracts. Themes are more abstract than summaries. For example, in a constructed-response task a student might be asked to read a sentence and then write one to two key words for it (e.g.: ###_EXAMPLES_###)",
            "understand information; medium; drawing a logical inference from the presented information; Completion question/task where the user is given a series of elements and must determine what comes next (e.g., ###_EXAMPLES_###).",
            "understand information; medium; drawing a logical inference from the presented information; Analogy question/task where an analogy A is to B as C is to D is given (e.g., ###_EXAMPLES_###). In the given example the student's task is to devise or select the term that fits the blank and completes the analogy. The comparison should be carried out strictly within the field of one science, not between different sciences.",
            "understand information; medium; drawing a logical inference from the presented information; Odd-one-out question/task where the user is given three or more items and must determine which one does not belong (e.g., ###_EXAMPLES_###). The question must not be in multiple-choice format.",
            "understand information; medium; detecting correspondences between two ideas, objects, etc.; Matching question/task requiring demonstration of how each part of one object, idea, problem, or situation corresponds to (or maps onto) each part of another (e.g., ###_EXAMPLES_###).",
            "understand information; medium; constructing a cause-effect model of a system; Reasoning question/task asking you to explain the cause of a given event (e.g., ###_EXAMPLES_###).",
            "understand information; medium; constructing a cause-effect model of a system; Troubleshooting question/task asking the user to determine what might have gone wrong in a malfunctioning system (e.g., ###_EXAMPLES_###).",
            "understand information; medium; constructing a cause-effect model of a system; System modification question/task asking the user to modify a system to achieve a certain goal (e.g., ###_EXAMPLES_###).",
            "understand information; medium; constructing a cause-effect model of a system; Prediction question/task asking how a change in one part of a system will affect another part (e.g., ###_EXAMPLES_###)."],
        "difficult":
            ["apply information; difficult; applying an operation to a familiar task; Algorithm execution question/task presenting a familiar problem solvable by a known procedure (e.g.: ###_EXAMPLES_###).",
            "apply information; difficult; applying an operation to an unfamiliar task; Algorithm execution question/task presenting an unfamiliar problem that must be solved. Begin by specifying the problem. Then ask to identify the procedure required to solve the problem, solve the problem using the chosen procedure (making adjustments as necessary), or generally both (e.g., ###_EXAMPLES_###)"]
        }

    question_answer_examples: Optional[str] = '{"question": "Что такое глобус?",  "answer": "Глобус — это трехмерная уменьшенная модель Земли или другой планеты (а также небесной сферы), шарообразной формы, которая передает поверхность планеты с сохранением пропорций"}'
    #Setting examples for concept filtration
    concept_filter_examples: Optional[tuple] = (

    )

    definition_generation_examples: Optional[tuple] = (
        'Географические карты — это уменьшенное, обобщённое изображение земной поверхности на плоскости, выполненное в определённой проекции с помощью условных знаков.',
        'Минералы — это однородные по составу и строению природные химические соединения или элементы, образующиеся в результате геологических процессов и составляющие основу горных пород.',
        'Питание реки — это процесс поступления воды в речную систему из различных источников (дождевых, талых, ледниковых, подземных), который определяет её водный режим.'
    )

    filter_relevant_whole_notion_examples: Optional[tuple] = ()
    filter_relevant_whole_notion_examples: Optional[tuple] = ()

    # prompt settings
    @computed_field
    @property
    def concept_mining_prompt(self) -> Prompt:
        return self.get_prompt_by_name("basic_concept_mining")
    
    @computed_field
    @property
    def concept_definition_prompt(self) -> Prompt:
        return self.get_prompt_by_name("basic_concept_definition")
    
    @computed_field
    @property
    def generate_bloom_tasks_prompt(self) -> Prompt:
        return self.get_prompt_by_name("basic_generate_bloom_tasks")


# initialize settings
settings = ProjectSettings()

# Log both to console and file
settings.path_logs.mkdir(parents=True, exist_ok=True)
handlers = [
    logging.StreamHandler(),
    logging.FileHandler(settings.path_logs_file, encoding='utf-8'),
]
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d",
    handlers=handlers,
)