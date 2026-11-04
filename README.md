# Neuro-Symbolic UML Class Diagram Verification and Repair

An automated neuro-symbolic framework to generate, verify, repair, and arbitrate UML class diagrams from natural language requirements against formal Object Constraint Language (OCL) metamodel invariants.

---

## 📌 Project Overview

Large Language Models (LLMs) often generate UML class diagrams that exhibit syntactic omissions, invalid multiplicities, and broken referential integrity. This repository provides an automated pipeline that:

1. **Generates** PlantUML class diagrams from natural language requirement specifications using foundation models (Gemini 3.5 Flash, Llama 3.3 70B, Nemotron 120B).
2. **Parses** PlantUML syntax into structured Abstract Syntax Trees (ASTs).
3. **Verifies** diagrams deterministically against 8 core OMG UML metamodel invariants ($C_1$–$C_8$).
4. **Repairs** non-compliant diagrams through closed-loop symbolic diagnostic feedback prompts.
5. **Arbitrates** candidate diagrams to select canonical models via a multi-tier Structural Richness metric ($\mathcal{S}_R$).
6. **Evaluates** semantic fidelity against human-authored ground-truth reference models using precision, recall, and $F_1$ metrics.

---

## 📁 Repository Structure

- `project0.py` — Pipeline configuration and API client setup.
- `experiment_loop.py` — Executes generation passes, deterministic OCL checking, and iterative closed-loop repair.
- `ocl_checker.py` — Deterministic symbolic verification engine encoding metamodel invariants $C_1$–$C_8$.
- `parse_puml.py` — AST extractor isolating classes, attributes, operation signatures, relationships, and multiplicities.
- `select_best_diagrams.py` — Arbitrates candidate diagrams using post-repair OSR, structural richness ($\mathcal{S}_R$), and parsimony.
- `nl-snippets.txt` — 15 benchmark natural language specifications across 3 distinct domains (Library Management, Healthcare Informatics, and E-Commerce).
- `reference_models/` — 15 human-authored reference PlantUML diagrams constructed independently by software engineering experts.
- `Taxonomy-Examples.md` — Detailed three-tier structural violation taxonomy with concrete PlantUML snippets, AST diagnostic logs, and repair transformations.
- `experiment_results.json` — Evaluation logs, AST verification traces, violation counts, and OSR metrics across all iterations.
- `135_diagrams_raw.puml` — Full corpus of all 135 generated diagrams across 3 repeated runs ($15\text{ specifications} \times 3\text{ models} \times 3\text{ runs}$).
- `best_45_diagrams.puml` — Top 45 arbitrated diagrams selected across individual model runs.
- `canonical_15_models.puml` — Final 15 canonical domain models selected via multi-tier arbitration (one per specification).

---

## 🔬 Formal OCL Error Taxonomy & Artifacts

The structural failure modes observed across baseline and repaired generations are cataloged into a three-tier taxonomy based on failure etiology, severity, and repair methodology:

* **Type 1: Structural Omissions (Syntax-Level)** — Incomplete element signatures (e.g., missing multiplicity bounds $C_3$, missing operation return types $C_5$).
* **Type 2: Semantic Inconsistencies (Logic-Level)** — Conflicting structural statements (e.g., duplicate class identifiers $C_2$, inverted multiplicity bounds $C_4$, circular generalization graphs $C_7$).
* **Type 3: Referential Failures (Hallucination-Level)** — Invariant violations involving non-existent symbols (e.g., generalization endpoints referencing undeclared classifiers $C_8$).

The comprehensive artifact with before-and-after PlantUML snippets, diagnostic messages, and repair strategies is available in:

📄 **[`Taxonomy-Examples.md`](Taxonomy-Examples.md)**

---

## 🚀 Setup & Execution

### 1. Clone the Repository
```bash
git clone [https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git](https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git)
cd A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams
