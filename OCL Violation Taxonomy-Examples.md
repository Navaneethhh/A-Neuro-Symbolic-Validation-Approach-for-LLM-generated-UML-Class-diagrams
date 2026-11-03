### File 2: Save as `TAXONOMY_EXAMPLES.md`

```markdown
# OCL Violation Taxonomy: Concrete Examples and Diagnostic Traces

This document details the three-tier failure taxonomy of Object Constraint Language (OCL) violations observed in LLM-generated UML class diagrams, including raw PlantUML failure snippets, verifier diagnostic logs, and compliant repairs.

---

## Summary Matrix

| Tier & Type | Invariant & UML Rule | Baseline Output (Violation) | Verifier AST Diagnostic | Repaired Output (Compliant) | Resolution Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_3$ (Multiplicity Completeness)**: Association ends must define multiplicity bounds. | `Member -- Book : borrows` | `[VIOLATION C3] Association 'Member -- Book' is missing multiplicity bounds on both association ends.` | `Member "0..1" -- "0..5" Book : borrows` | Automated re-prompting or Grammar-Constrained Decoding (GCD). |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_5$ (Operation Completeness)**: Every operation must declare an explicit return type. | `+ calculateFine()` | `[VIOLATION C5] Operation 'calculateFine' has no declared return type.` | `+ calculateFine(): Double` | Schema enforcement or single-pass self-repair prompting. |
| **Type 2: Semantic Inconsistency** *(Logic-Level)* | **$C_4$ (Multiplicity Validity)**: Lower multiplicity bound cannot exceed upper bound ($lower \le upper$). | `Order "5..1" -- "1" Item` | `[VIOLATION C4] Invalid multiplicity '5..1': lower bound (5) > upper bound (1).` | `Order "1..5" -- "1" Item` | Symbolic constraint reasoning and range inversion correction. |
| **Type 2: Semantic Inconsistency** *(Logic-Level)* | **$C_7$ (Acyclic Inheritance)**: Generalization graph must be a Directed Acyclic Graph (DAG). | `User <\|-- Patient`<br>`Patient <\|-- User` | `[VIOLATION C7] Cyclic inheritance detected: 'User' <-> 'Patient'. Generalization must be acyclic.` | `User <\|-- Patient` | AST cycle detection feedback breaking the dependency loop. |
| **Type 3: Referential Failure** *(Hallucination-Level)* | **$C_8$ (Referential Integrity)**: Generalization endpoints must reference declared classes. | `Invoice --\|> BillingEntity`<br>*(where `BillingEntity` is undeclared)* | `[VIOLATION C8] Referential failure: Generalization target 'BillingEntity' is not defined in model.` | `Invoice --\|> Order`<br>*(or declare `class BillingEntity`)* | Symbol table cross-reference feedback prompting entity declaration or link repair. |

---

## Detailed Tier Analyses

### Type 1: Structural Omissions (Syntax-Level)

Structural omissions occur when an LLM successfully identifies domain entities and relational connections but omits required syntactic specifications such as return types or association multiplicities.

#### Example: Missing Association Multiplicities ($C_3$)
* **Failure Snippet:**
  ```plantuml
  @startuml
  class Patient {
    - patientId: String
    - name: String
  }
  class Appointment {
    - appointmentDate: Date
  }
  Patient -- Appointment : schedules
  @enduml
