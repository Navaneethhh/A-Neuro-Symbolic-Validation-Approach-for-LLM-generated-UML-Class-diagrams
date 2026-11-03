# Neuro-Symbolic UML Class Diagram Verification and Repair

An automated neuro-symbolic framework to generate, verify, repair, and arbitrate UML class diagrams from natural language requirements against formal OCL metamodel constraints.

---

## 📌 Project Overview

Large Language Models (LLMs) often generate UML diagrams with missing attributes, broken multiplicities, and semantic errors. This project provides an automated pipeline that:

1. **Generates** PlantUML class diagrams from natural language requirement snippets using foundation models (Gemini 3.5 Flash, Llama 3.3 70B, Nemotron 120B).
2. **Parses** PlantUML syntax into structured Abstract Syntax Trees (ASTs).
3. **Verifies** diagrams deterministically against 8 core OCL metamodel constraints ($C_1$–$C_8$).
4. **Repairs** failing diagrams using an automated, closed-loop diagnostic feedback mechanism.
5. **Arbitrates** and selects canonical domain models based on a multi-tier Structural Richness score ($\mathcal{S}_R$).

---

## 📁 Repository Structure

- `project0.py` — Pipeline configuration and API client setup.
- `experiment_loop.py` — Executes generation, deterministic OCL checking, and iterative self-repair across runs.
- `ocl_checker.py` — Deterministic symbolic verifier encoding constraints $C_1$–$C_8$.
- `parse_puml.py` — AST extractor parsing structural elements, relationships, and members from PlantUML.
- `select_best_diagrams.py` — Ranks and arbitrates candidate diagrams using OCL compliance and structural richness ($\mathcal{S}_R$).
- `nl-snippets.txt` — 15 benchmark natural language requirement specifications across 3 distinct domains (Library Management, Healthcare, E-Commerce).
- `OCL Violation Taxonamy-Examples.md` — Detailed three-level error taxonomy accompanied by concrete PlantUML examples, diagnostic traces, and repair transformations.
- `experiment_results.json` — Evaluation logs, syntax verification traces, violation counts, and OSR metrics across all iterations.
- `135 - Diagrams (3 runs).puml` — Comprehensive repository of all 135 generated diagrams across 3 full experimental runs ($15\text{ snippets} \times 3\text{ models} \times 3\text{ runs}$).
- `Best-45-Diagrams.puml` — Top 45 arbitrated diagrams selected across all runs with priority given to high-performing models (Groq Llama 3.3 70B dominant).
- `best_15_results.puml` — Canonical 15 benchmark diagrams selected via tournament arbitration (one optimal model per snippet).

---

## 🔬 Formal OCL Error Taxonomy & Artifacts

In response to reviewer feedback emphasizing the need for concrete illustrations of structural defects:

> **Reviewer Note:** *"The three-level error taxonomy is relevant and could be illustrated with examples."*

The complete taxonomy—spanning **Syntactic/Structural Malformations**, **Relational/Multiplicity Defects**, and **Semantic/Typing Inconsistencies**—is documented in:

📄 **[`OCL Violation Taxonamy-Examples.md`](OCL%20Violation%20Taxonamy-Examples.md)**

This document provides:
- The formal OCL invariants for all constraints ($C_1$ through $C_8$).
- Side-by-side **Before vs. After** PlantUML code snippets showing actual LLM failure modes.
- Exact diagnostic feedback strings produced by `ocl_checker.py`.
- Automated symbolic repair transitions executed during the closed-loop process.

---

## 🚀 Set Up

###  Clone the Repository
```bash
git clone [https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git](https://github.com/Navaneethhh/A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams.git)
cd A-Neuro-Symbolic-Validation-Approach-for-LLM-generated-UML-Class-diagrams
