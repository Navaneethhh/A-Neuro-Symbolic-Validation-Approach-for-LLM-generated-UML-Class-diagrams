# experiment_loop.py
import time
import json
import os
from ocl_checker import check_all_constraints
from project0 import generate_puml, extract_puml
from parse_puml import parse_puml_to_ast

SNIPPETS_FILE = "nl-snippets.txt"
OUTPUT_PUML_FILE = "experiment_output.puml"
OUTPUT_JSON_FILE = "experiment_results.json"

MODELS = [
    "Gemini 1.5 Pro", 
    "Llama 3.3 70B (Groq)", 
    "Nemotron 120B (OpenRouter)"
]


def load_snippets(filepath):
    """Reads requirement snippets from nl-snippets.txt (supports line-separated or JSON array)."""
    if not os.path.exists(filepath):
        print(f"⚠️ Warning: Snippet file '{filepath}' not found.")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return []

    if content.startswith("[") and content.endswith("]"):
        try:
            return json.loads(content)
        except Exception:
            pass

    lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
    snippets = []
    for idx, line in enumerate(lines, 1):
        snippets.append({
            "id": f"snippet_{idx:02d}",
            "domain": "General",
            "text": line
        })
    return snippets


def safe_generate_and_extract(prompt, model_name):
    """Safely invokes LLM API and extracts clean PlantUML code string."""
    try:
        raw_res = generate_puml(prompt, model_name=model_name)
        if isinstance(raw_res, dict):
            raw_res = raw_res.get("content") or raw_res.get("text") or str(raw_res)
        elif not isinstance(raw_res, str):
            raw_res = str(raw_res) if raw_res is not None else ""

        clean_puml = extract_puml(raw_res)
        return clean_puml, None
    except Exception as e:
        return "", str(e)


def run_experiment_pipeline():
    snippets = load_snippets(SNIPPETS_FILE)

    if not snippets:
        print(f"❌ Error: No valid requirement snippets loaded from '{SNIPPETS_FILE}'.")
        return

    total_runs = len(snippets) * len(MODELS)
    print("=" * 85)
    print(f"   NEURO-SYMBOLIC PIPELINE ({len(snippets)} Snippets x {len(MODELS)} Models = {total_runs} Executions)   ")
    print("=" * 85)

    experiment_results = []
    combined_puml_output = ""

    system_instruction = (
        "You are a UML modeling expert. Given natural language requirements, generate a complete UML class diagram in PlantUML syntax.\n"
        "Mandatory Modeling Rules:\n"
        "1. EVERY attribute must have an explicit data type (e.g., - customerId : String).\n"
        "2. EVERY method must have an explicit return type (e.g., + calculateTotal() : double).\n"
        "3. EVERY relationship between classes MUST include explicit multiplicity bounds on both ends (e.g., Customer \"1\" -- \"0..*\" Order).\n"
        "4. Self-associations MUST include a role label.\n"
        "Output ONLY valid PlantUML code enclosed inside @startuml and @enduml."
    )

    run_count = 0

    for snippet in snippets:
        snippet_id = snippet.get("id", "unknown")
        domain = snippet.get("domain", "General")
        req_text = snippet.get("text", "")

        print(f"\n[{snippet_id}] ({domain}): \"{req_text[:65]}...\"")

        for model_name in MODELS:
            run_count += 1
            current_prompt = f"{system_instruction}\n\nRequirements: {req_text}"

            # Initial Generation (Iteration 0)
            puml_clean, err_msg = safe_generate_and_extract(current_prompt, model_name)

            if err_msg or not puml_clean.strip():
                record = {
                    "model": model_name,
                    "snippet_id": snippet_id,
                    "domain": domain,
                    "initial_errors": 8,
                    "loops_used": 0,
                    "post_loop_errors": 8,
                    "passed": 0,
                    "score_str": "0/8",
                    "accuracy_pct": "0.0%",
                    "status": "FAIL (API Error)",
                    "puml": "",
                    "parsed_ast": {}
                }
                experiment_results.append(record)
                continue

            # Check Initial OCL
            initial_ast = parse_puml_to_ast(puml_clean)
            initial_eval = check_all_constraints(initial_ast)
            initial_err_list = initial_eval.get("errors", [])
            initial_err_count = len(initial_err_list)

            # Feedback Loop Execution
            final_puml = puml_clean
            final_eval = initial_eval
            final_ast = initial_ast
            loops_used = 0

            if not initial_eval.get("all_passed", False):
                loops_used = 1
                error_list = "\n- ".join(initial_err_list)

                feedback_prompt = (
                    f"Requirements: {req_text}\n\n"
                    f"Your previous PlantUML attempt failed formal OCL constraints:\n"
                    f"- {error_list}\n\n"
                    f"Please regenerate the PlantUML diagram to strictly fix these structural errors:\n"
                    f"- Ensure EVERY attribute has an explicit primitive type (e.g., name : String)\n"
                    f"- Ensure EVERY method has an explicit return type (e.g., placeOrder() : void)\n"
                    f"- Ensure EVERY relationship has explicit multiplicity bounds on both ends.\n"
                    f"Output ONLY valid PlantUML code enclosed inside @startuml and @enduml."
                )

                time.sleep(3)

                puml_retry_clean, _ = safe_generate_and_extract(feedback_prompt, model_name)
                if puml_retry_clean.strip():
                    final_puml = puml_retry_clean
                    final_ast = parse_puml_to_ast(final_puml)
                    final_eval = check_all_constraints(final_ast)

            # Metrics Calculation
            final_err_list = final_eval.get("errors", [])
            post_loop_errors = len(final_err_list) if loops_used > 0 else 0
            
            passed_count = sum(1 for k in ['C1','C2','C3','C4','C5','C6','C7','C8'] if final_eval.get(k, False))
            accuracy = (passed_count / 8.0) * 100.0
            status = "PASS" if final_eval.get("all_passed", False) else "FAIL"

            record = {
                "model": model_name,
                "snippet_id": snippet_id,
                "domain": domain,
                "initial_errors": initial_err_count,
                "loops_used": loops_used,
                "post_loop_errors": post_loop_errors,
                "passed": passed_count,
                "score_str": f"{passed_count}/8",
                "accuracy_pct": f"{accuracy:.1f}%",
                "status": status,
                "puml": final_puml,
                "parsed_ast": final_ast
            }
            experiment_results.append(record)

            combined_puml_output += f"/' Snippet: {snippet_id} | Model: {model_name} | Status: {status} ({passed_count}/8) '/\n"
            combined_puml_output += f"{final_puml}\n\n"

            time.sleep(2)

    # Console Summary Display
    print("\n" + "=" * 95)
    print(f"{'SNIPPET':<10} | {'AI MODEL':<26} | {'INIT ERR':<8} | {'LOOPS USED':<10} | {'POST ERR':<8} | {'SCORE':<6} | {'ACCURACY (%)'}")
    print("=" * 95)

    for r in experiment_results:
        print(f"{r['snippet_id']:<10} | {r['model']:<26} | {r['initial_errors']:<8} | {r['loops_used']:<10} | {r['post_loop_errors']:<8} | {r['score_str']:<6} | {r['accuracy_pct']}")

    print("=" * 95)

    # Model Overall Performance Aggregation
    print("\n" + "=" * 85)
    print("   MODEL ACCURACY OVERALL AGGREGATE SUMMARY   ")
    print("=" * 85)
    for model_name in MODELS:
        m_recs = [r for r in experiment_results if r["model"] == model_name]
        if not m_recs:
            continue
        tot_passed = sum(r["passed"] for r in m_recs)
        tot_possible = len(m_recs) * 8
        model_acc = (tot_passed / float(tot_possible)) * 100.0
        passed_100 = sum(1 for r in m_recs if r["status"] == "PASS")
        repaired = sum(1 for r in m_recs if r["loops_used"] > 0 and r["status"] == "PASS")

        print(f"Model: {model_name:<28} | Fully Compliant Diagrams: {passed_100}/{len(m_recs)} | Overall Accuracy: ({tot_passed}/{tot_possible}) x 100 = {model_acc:.1f}% | Repaired: {repaired}")
    print("=" * 85)

    # Save Output Files
    with open(OUTPUT_PUML_FILE, "w", encoding="utf-8") as f:
        f.write(combined_puml_output)

    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(experiment_results, f, indent=2)

    print(f"\nSaved all results to '{OUTPUT_PUML_FILE}' and '{OUTPUT_JSON_FILE}'.")


if __name__ == "__main__":
    run_experiment_pipeline()