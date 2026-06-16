# 📚 Synthetic Educational Dataset Generator (Bloom’s Taxonomy Pipeline)

A pipeline for automatic generation of structured learning materials — concepts, definitions, and instruction-level tasks aligned with Bloom’s taxonomy — from PDF textbooks.

---

## 🌟 Overview

This project extracts domain-specific concepts from educational PDFs, generates precise definitions, and produces *question–answer pairs* covering cognitive levels from Bloom’s Taxonomy.

**Output example:**
```json
{
  "5 класс": [
    {
      "id": 1,
      "question": "Верно ли, что литосфера — твёрдая оболочка Земли?",
      "answer": "Верно.",
      "state": ["remember information", "easy", "identifying knowledge...", "Verification question..."],
      "definition": "Литосфера — твёрдая оболочка Земли...",
      "success": true
    }
  ]
}
```
---

### Project setup:
- Set up your .venv with uv sync
- Define all variables in settings.py
- Select desired steps in main.py (comment the odd lines)
```
    input_file = 'definitions_11.json'
    pipe = Pipeline(input_file)

    # # Регистрация последовательности шагов
    # pipe.add_step('extract_concept')   # Извлекаем понятия
    # pipe.add_step('make_definitions') # Создаем дефиниции
    pipe.add_step('make_instructions') # Генерируем инструкции

    # Обрабатываем файл
    processed_data = pipe.run()
    print(processed_data)
```
- run main.py
