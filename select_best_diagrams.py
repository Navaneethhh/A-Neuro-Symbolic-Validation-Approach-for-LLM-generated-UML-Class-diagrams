import json
import os

INPUT_JSON_FILE = "experiment_results.json"
OUTPUT_BEST_PUML_FILE = "best_15_results.puml"


def calculate_richness_score(parsed_ast):
    """
    Computes the structural richness score from the parsed AST.
    More complete, descriptive models get a higher score.
    """
    if not parsed_ast or not isinstance(parsed_ast, dict):
        return 0

    classes = parsed_ast.get("classes", [])
    if not classes:
        return 0

    num_classes = len(classes)
    num_attrs = sum(len(c.get("attributes", [])) for c in classes)
    num_methods = sum(len(c.get("methods", [])) for c in classes)

    relationships = parsed_ast.get("relationships", [])
    num_rels = len(relationships)

    # Bonus for explicit relationship markers (*--, o--, <|--)
    advanced_rel_bonus = 0
    for rel in relationships:
        rel_type = rel.get("type", "")
        if any(marker in rel_type for marker in ["*--", "--*", "o--", "--o", "<|--", "--|>"]):
            advanced_rel_bonus += 1

    # Weighted Richness Score
    richness_score = (
        (num_classes * 3) +
        (num_attrs * 2) +
        (num_methods * 2) +
        (num_rels * 2) +
        advanced_rel_bonus
    )
    return richness_score


def select_best_15():
    if not os.path.exists(INPUT_JSON_FILE):
        print(f"❌ Error: '{INPUT_JSON_FILE}' not found. Run experiment_loop.py first!")
        return

    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    if not all_results:
        print(f"❌ Error: '{INPUT_JSON_FILE}' is empty.")
        return

    # 1. Group records strictly by (domain, snippet_id)
    snippet_groups = {}
    for entry in all_results:
        key = (entry.get("domain", "General"), entry.get("snippet_id", "unknown"))
        if key not in snippet_groups:
            snippet_groups[key] = []
        snippet_groups[key].append(entry)

    winning_diagrams = []

    print("\n" + "=" * 80)
    print(f"{'SNIPPET KEY':<22} | {'SELECTED WINNER':<26} | {'STATUS':<6} | {'RICHNESS':<8}")
    print("=" * 80)

    # 2. Process each isolated snippet group
    for (domain, snippet_id), candidates in snippet_groups.items():
        # Prefer models that achieved full PASS status (all 8 constraints passed)
        compliant_candidates = [c for c in candidates if c.get("status") == "PASS"]

        # Fallback: take the candidate(s) with highest passed count if none passed 100%
        if not compliant_candidates:
            max_passed = max(c.get("passed", 0) for c in candidates)
            compliant_candidates = [c for c in candidates if c.get("passed", 0) == max_passed]

        # Calculate Richness Score for the candidates
        for cand in compliant_candidates:
            ast_data = cand.get("parsed_ast", {})
            cand["richness_score"] = calculate_richness_score(ast_data)

        # Sort descending by richness score -> highest richness wins
        compliant_candidates.sort(key=lambda x: x["richness_score"], reverse=True)
        winner = compliant_candidates[0]
        winning_diagrams.append(winner)

        group_label = f"{domain} - {snippet_id}"
        print(f"{group_label:<22} | {winner['model']:<26} | {winner['status']:<6} | {winner['richness_score']:<8}")

    print("=" * 80)

    # 3. Save all 15 winning diagrams into a single consolidated .puml file
    with open(OUTPUT_BEST_PUML_FILE, "w", encoding="utf-8") as f:
        for item in winning_diagrams:
            header = (
                f"' ==========================================================\n"
                f"' SNIPPET: {item['snippet_id']} | DOMAIN: {item['domain']}\n"
                f"' WINNING MODEL: {item['model']}\n"
                f"' OCL ACCURACY: {item['accuracy_pct']} ({item['score_str']}) | RICHNESS SCORE: {item['richness_score']}\n"
                f"' LOOPS USED: {item['loops_used']}\n"
                f"' ==========================================================\n"
            )
            f.write(header)
            f.write(item.get("puml", "").strip() + "\n\n")

    print(f"\n Successfully exported all {len(winning_diagrams)} best diagrams to '{OUTPUT_BEST_PUML_FILE}'!\n")


if __name__ == "__main__":
    select_best_15()