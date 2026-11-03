# OCL Violation Taxonomy: Concrete Examples and Diagnostic Traces

This document catalogs the three-tier taxonomy of Object Constraint Language (OCL) violations observed in LLM-generated UML class diagrams. For each constraint ($C_1$ through $C_8$), we provide the formal metamodel rule, a representative baseline failure snippet in PlantUML syntax, the exact diagnostic error trace produced by our Abstract Syntax Tree (AST) symbolic verifier, the compliant post-repair code, and the corresponding remediation strategy.

---

## 1. Summary Matrix

| Tier & Type | Invariant & UML Rule | Baseline Output (Violation) | Verifier AST Diagnostic | Repaired Output (Compliant) | Resolution Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_1$ (Non-Empty Class Bodies)**: Every declared class must contain $\ge 1$ attribute. | `class Book {}` | `[VIOLATION C1] Class 'Book' has an empty body (ownedAttribute->size() == 0).` | `class Book {`<br>`  - isbn: String`<br>`}` | Re-prompting for entity attribute extraction. |
| **Type 2: Semantic Inconsistency** *(Logic-Level)* | **$C_2$ (Name Uniqueness)**: Class names within the package namespace must be unique. | `class Account { - id: String }`<br>`class Account { - type: String }` | `[VIOLATION C2] Duplicate classifier identifier detected: 'Account' declared multiple times.` | `class Account { - id: String }`<br>`class AccountType { - type: String }` | Symbolic deduplication and qualifier disambiguation. |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_3$ (Multiplicity Completeness)**: Association ends must declare explicit lower/upper bounds. | `Member -- Book : borrows` | `[VIOLATION C3] Association 'Member -- Book' lacks explicit multiplicity bounds on both ends.` | `Member "0..1" -- "0..5" Book : borrows` | Automated re-prompting or Grammar-Constrained Decoding (GCD). |
| **Type 2: Semantic Inconsistency** *(Logic-Level)* | **$C_4$ (Multiplicity Validity)**: Multiplicity bounds must satisfy $lower \le upper$. | `Order "5..1" -- "1" Item` | `[VIOLATION C4] Invalid multiplicity '5..1': lower bound (5) > upper bound (1).` | `Order "1..5" -- "1" Item` | Range inversion correction via symbolic feedback. |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_5$ (Operation Completeness)**: Every operation must declare an explicit return type. | `+ calculateFine()` | `[VIOLATION C5] Operation 'calculateFine' has no declared return type.` | `+ calculateFine(): Double` | Schema enforcement or single-pass self-repair prompting. |
| **Type 1: Structural Omission** *(Syntax-Level)* | **$C_6$ (Role Names in Self-Associations)**: Endpoints of reflexive associations must specify distinct role names. | `Employee "1" -- "*" Employee : manages` | `[VIOLATION C6] Self-association on 'Employee' lacks explicit memberEnd role names.` | `Employee "1" supervisor -- "*" supervisee Employee : manages` | Explicit role annotation prompting. |
| **Type 2: Semantic Inconsistency** *(Logic-Level)* | **$C_7$ (Acyclic Inheritance)**: Generalization hierarchies must form a Directed Acyclic Graph (DAG). | `User <\|-- Patient`<br>`Patient <\|-- User` | `[VIOLATION C7] Cyclic inheritance detected: 'User' <-> 'Patient'. Generalization must be acyclic.` | `User <\|-- Patient` | AST cycle detection feedback breaking the dependency loop. |
| **Type 3: Referential Failure** *(Hallucination-Level)* | **$C_8$ (Referential Integrity)**: Generalization endpoints must reference declared classifiers. | `Invoice --\|> BillingEntity`<br>*(where `BillingEntity` is undeclared)* | `[VIOLATION C8] Referential failure: Generalization target 'BillingEntity' is not defined in model.` | `Invoice --\|> Order`<br>*(or declare `class BillingEntity`)* | Symbol table cross-reference prompting entity declaration or link repair. |

---

## 2. Type 1: Structural Omissions (Syntax-Level)

Structural omissions represent incomplete declarations where domain concepts were correctly identified by the LLM, but required syntactic elements were omitted during token generation.

### Constraint $C_1$: Non-Empty Class Bodies
* **Formal OCL Rule:** `context Class inv: self.ownedAttribute->size() > 0`
* **Baseline Violation:**
  ```plantuml
  @startuml
  class LibraryCatalog {
  }
  class Book {
    - title: String
  }
  @enduml
