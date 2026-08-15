# Neuro-Symbolic UML Class Diagram Verification

An automated framework to evaluate and repair LLM-generated UML class diagrams against formal Object Constraint Language (OCL) metamodel constraints[cite: 3].

## Overview

Large Language Models often produce structurally invalid UML diagrams[cite: 3]. This project implements a neuro-symbolic pipeline that:
1. **Generates** PlantUML diagrams from natural language requirements using LLMs (Gemini 3.5 Flash, Llama 3.3 70B, Nemotron 120B)[cite: 3].
2. **Parses** PlantUML into an Abstract Syntax Tree (AST)[cite: 3].
3. **Verifies** the model against 8 core OCL metamodel invariants ($C_1$–$C_8$)[cite: 3].
4. **Repairs** syntactic and semantic violations via a closed-loop diagnostic feedback mechanism[cite: 3].
5. **Arbitrates** valid candidate models using a Structural Richness score ($\mathcal{S}_R$) to select the optimal canonical model[cite: 3].

---

## Evaluated Constraints ($C_1$–$C_8$)

* **$C_1$**: Non-empty class bodies ($\ge 1$ attribute)[cite: 3]
* **$C_2$**: Unique class names[cite: 3]
* **$C_3$**: Multiplicity completeness on all association ends[cite: 3]
* **$C_4$**: Valid multiplicity bounds (lower $\le$ upper)[cite: 3]
* **$C_5$**: Declared return types for all operations[cite: 3]
* **$C_6$**: Explicit role names in self-associations[cite: 3]
* **$C_7$**: Acyclic inheritance hierarchies[cite: 3]
* **$C_8$**: Referential integrity on generalization endpoints[cite: 3]

---

## Repository Structure

```text
├── nl-snippets.txt          # Benchmark NL requirement specifications (15 snippets across 3 domains)
├── parse_puml.py            # PlantUML parser to extract AST and structural primitives
├── ocl_checker.py           # Deterministic Python verifier for OCL constraints (C1–C8)
├── experiment_loop.py       # Closed-loop generation, verification, and self-repair pipeline
├── select_best_diagrams.py  # Multi-model arbitrator based on Structural Richness (SR)
├── project0.py              # Main execution script / orchestration
├── experiment_results.json  # Comprehensive benchmark metrics, evaluations, and OSR logs
├── experiment_output.puml   # Raw and repaired PlantUML generation outputs
└── best_15_results.puml     # Selected canonical domain diagrams
