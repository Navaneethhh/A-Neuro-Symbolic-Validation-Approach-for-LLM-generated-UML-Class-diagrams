import re

PRIMITIVE_TYPES = {
    "string",
    "str",
    "integer",
    "int",
    "float",
    "double",
    "boolean",
    "bool",
    "date",
    "datetime",
    "time",
    "void",
    "long",
    "short",
    "byte",
    "char",
    "number",
    "real",
    "decimal",
}


def parse_member_line(clean_line: str) -> dict:
    """Parses a sanitized PlantUML member line into a method or attribute dict.

    UML standard: Methods strictly require parentheses '()'.
    """
    if " = " in clean_line or "=" in clean_line:
        clean_line = re.sub(r"\s*=\s*.*$", "", clean_line).strip()

    # An operation / method must have parameter parentheses
    is_method = "(" in clean_line and ")" in clean_line

    if is_method:
        if "):" in clean_line:
            parts = clean_line.split("):", 1)
            m_name = parts[0].strip() + ")"
            m_type = parts[1].strip()
        elif ":" in clean_line and clean_line.rfind(":") > clean_line.rfind(")"):
            idx = clean_line.rfind(":")
            m_name = clean_line[:idx].strip()
            m_type = clean_line[idx + 1 :].strip()
        else:
            m_name = clean_line
            m_type = None
        return {"kind": "method", "name": m_name, "type": m_type}

    else:
        # Attribute: either 'name : type' or Java-style 'type name'
        if ":" in clean_line:
            a_parts = clean_line.split(":", 1)
            a_name = a_parts[0].strip()
            a_type = a_parts[1].strip()
        elif " " in clean_line:
            a_parts = clean_line.split()
            # If the first token is a known primitive type, treat as 'type name'
            if a_parts[0].lower() in PRIMITIVE_TYPES:
                a_type = a_parts[0].strip()
                a_name = a_parts[1].strip()
            else:
                a_name = a_parts[0].strip()
                a_type = a_parts[1].strip()
        else:
            a_name = clean_line
            a_type = None
        return {"kind": "attribute", "name": a_name, "type": a_type}


def parse_puml_to_ast(puml_text: str) -> dict:
    if not puml_text or "@startuml" not in puml_text:
        return {"error": "Invalid or empty PlantUML text."}

    classes = []
    relationships = []
    lines = [
        line.strip()
        for line in puml_text.splitlines()
        if line.strip() and not line.strip().startswith("'")
    ]

    current_class = None
    in_note_block = False

    for line in lines:
        if (
            line.startswith("@startuml")
            or line.startswith("@enum")
            or line.startswith("@enduml")
            or line.startswith("skinparam")
        ):
            continue

        # Handle note blocks
        if line.startswith("note ") or line == "note":
            in_note_block = True
            continue
        if line == "end note" or line.startswith("end note"):
            in_note_block = False
            continue
        if in_note_block:
            continue

        if line.startswith("package ") or (line == "}" and not current_class):
            continue

        # 1. Flexible Class Matcher (capturing inline extends/implements)
        class_pattern = (
            r"^(abstract\s+class|class|interface|abstract|enum)\s+"
            r'(?:"([^"]+)"|([A-Za-z0-9_]+(?:<[A-Za-z0-9_,\s]+>)?))'
            r"(?:\s+as\s+([A-Za-z0-9_]+))?"
            r"(?:\s+(extends|implements)\s+([A-Za-z0-9_]+))?"
            r"(?:\s*<<[^>]+>>)*\s*(\{?)"
        )
        class_match = re.match(class_pattern, line)

        if class_match:
            (
                kind,
                quoted_name,
                plain_name,
                alias,
                inherit_type,
                parent_class,
                has_brace,
            ) = class_match.groups()
            kind_clean = "abstract" if "abstract" in kind else kind
            raw_title = (
                alias
                if alias
                else (plain_name.strip() if plain_name else quoted_name)
            )
            class_title = (
                re.sub(r"<.*?>", "", raw_title).strip()
                if raw_title
                else raw_title
            )

            new_class = {
                "name": kind_clean,
                "title": class_title,
                "members": [],
            }
            classes.append(new_class)

            # Auto-inject explicit generalization/realization relationship if inline extends/implements is present
            if parent_class:
                rel_arrow = "..|>" if inherit_type == "implements" else "--|>"
                relationships.append({
                    "name": "relationship",
                    "left": class_title,
                    "right": parent_class.strip(),
                    "leftMultiplicity": None,
                    "rightMultiplicity": None,
                    "arrow": rel_arrow,
                    "label": None,
                })

            if has_brace == "{":
                current_class = new_class
            else:
                current_class = None
            continue

        if line == "}" and current_class:
            current_class = None
            continue

        # 2. Standalone Member Syntax: ClassName : [-+]member
        standalone_match = re.match(r"^([A-Za-z0-9_<>\s]+)\s*:\s*(.*)$", line)
        if standalone_match and not any(
            k in line for k in ["--", "..", "->", "<-", "*--", "o--"]
        ):
            cls_name_raw, member_str = standalone_match.groups()
            cls_name = re.sub(r"<.*?>", "", cls_name_raw).strip()

            target_class = next(
                (c for c in classes if c["title"] == cls_name), None
            )
            if not target_class:
                target_class = {
                    "name": "class",
                    "title": cls_name,
                    "members": [],
                }
                classes.append(target_class)

            clean_line = re.sub(r"\{[a-zA-Z0-9_]+\}\s*", "", member_str).strip()
            clean_line = clean_line.lstrip("+-#~").strip()
            if " '" in clean_line:
                clean_line = clean_line.split(" '")[0].strip()

            target_class["members"].append(parse_member_line(clean_line))
            continue

        # 3. Parse Class Members Inside Braced Block
        if current_class:
            clean_line = re.sub(r"\{[a-zA-Z0-9_]+\}\s*", "", line).strip()
            clean_line = clean_line.lstrip("+-#~").strip()
            if " '" in clean_line:
                clean_line = clean_line.split(" '")[0].strip()

            if not clean_line or clean_line.startswith("'"):
                continue

            current_class["members"].append(parse_member_line(clean_line))
            continue

        # 4. Comprehensive Relationship Matcher
        rel_pattern = (
            r"^([A-Za-z0-9_<>\s]+)\s*"
            r'(?:"([^"]+)")?\s*'
            r"([<|*o\-\.a-z\[\]\>]+(?:\-\[[a-z]+\]\-|[a-z]+)?[<|*o\-\.a-z\[\]\>]*)\s*"
            r'(?:"([^"]+)")?\s*'
            r"([A-Za-z0-9_<>\s]+)"
            r"(?:\s*:\s*(.*))?$"
        )
        rel_match = re.match(rel_pattern, line)
        if rel_match:
            left, left_mult, arrow, right_mult, right, label = (
                rel_match.groups()
            )
            relationships.append({
                "name": "relationship",
                "left": re.sub(r"<.*?>", "", left).strip(),
                "right": re.sub(r"<.*?>", "", right).strip(),
                "leftMultiplicity": left_mult,
                "rightMultiplicity": right_mult,
                "arrow": arrow,
                "label": label.strip() if label else None,
            })

    return {"elements": classes + relationships}
