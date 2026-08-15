# Neuro-Symbolic UML Class Diagram Verification and Repair

An automated neuro-symbolic framework to generate, verify, repair, and select UML class diagrams from natural language requirements against formal OCL metamodel constraints.

---

## 📌 Project Overview

Large Language Models (LLMs) often generate UML diagrams with missing attributes, broken multiplicities, and semantic errors. This project provides an automated pipeline that:

1. **Generates** PlantUML class diagrams from natural language requirement snippets using foundation models (Gemini 3.5 Flash, Llama 3.3 70B, Nemotron 120B).
2. **Parses** PlantUML syntax into Abstract Syntax Trees (ASTs).
3. **Verifies** the diagrams deterministically against 8 core OCL metamodel constraints ($C_1$–$C_8$).
4. **Repairs** failing diagrams using an automated closed-loop diagnostic feedback mechanism.
5. **Arbitrates** and selects the best canonical domain models based on a Structural Richness score ($\mathcal{S}_R$).

---

## 📁 Repository Structure

* `project0.py` — Pipeline configuration and API key setup.
* `experiment_loop.py` — Runs the generation, OCL checking, and iterative self-repair loop.
* `ocl_checker.py` — Deterministic verifier for OCL constraints ($C_1$–$C_8$).
* `parse_puml.py` — Extracts AST components from PlantUML diagrams.
* `select_best_diagrams.py` — Ranks and selects the highest-scoring compliant diagrams using Structural Richness ($\mathcal{S}_R$).
* `nl-snippets.txt` / `nl-snippets1.txt` — 15 benchmark natural language requirement specifications across 3 domains.
* `experiment_results.json` — Evaluation logs, violation counts, and OSR metrics.
* `experiment_output.puml` — Initial and repaired PlantUML diagrams.
* `best_15_results.puml` — Final canonical diagrams selected by arbitration.

---

## 🚀 How to Set Up and Run

### Step 1: Clone the Repository
```bash
git clone [https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git](https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git)
cd A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams

Step 2: Set Up Virtual Environment & Dependencies
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install requests google-generativeai groq openai
Step 3: Add Your API Keys
Open project0.py in your text editor and insert your active API keys:

Python
GEMINI_API_KEY = "your_google_gemini_api_key_here"
GROQ_API_KEY = "your_groq_api_key_here"
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
Step 4: Run the Experiment Pipeline
Run the closed-loop generation, verification, and repair process:

Bash
python experiment_loop.py
This tests all requirement snippets, verifies OCL constraints, triggers the self-repair loop for non-compliant models, and saves results to experiment_results.json.

Step 5: Select the Best Diagrams
Run the candidate arbitrator to score and select canonical diagrams:

Bash
python select_best_diagrams.py
