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

---

To run the project:
- Set up your .venv with uv sync
- Define all variables in settings.py
- Select desired steps in main.py (comment the odd lines)
- run main.py
