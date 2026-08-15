# ocl_checker.py

def check_c1(ast):
    """
    C1: Every class/interface/abstract class/enum must have at least one member or literal value.
    """
    classes = [e for e in ast.get("elements", []) if e.get("name") in ["class", "interface", "abstract", "enum"]]
    errors = []
    
    for cls in classes:
        members = cls.get("members", [])
        if len(members) == 0:
            errors.append(f"C1 Failed: Class/Interface '{cls.get('title')}' has no attributes or methods.")
            
    if errors:
        return False, errors
    return True, None


def check_c2(ast):
    """
    C2: Class names must be unique across the diagram.
    """
    classes = [e for e in ast.get("elements", []) if e.get("name") in ["class", "interface", "abstract", "enum"]]
    titles = [c.get("title") for c in classes if c.get("title")]
    
    seen = set()
    duplicates = set()
    for title in titles:
        if title in seen:
            duplicates.add(title)
        seen.add(title)
        
    if duplicates:
        return False, [f"C2 Failed: Duplicate class names detected: {', '.join(duplicates)}"]
    return True, None


def check_c3(ast):
    """
    C3: Attribute names within a class must be unique.
    """
    classes = [e for e in ast.get("elements", []) if e.get("name") in ["class", "interface", "abstract", "enum"]]
    errors = []
    
    for cls in classes:
        attrs = [m.get("name") for m in cls.get("members", []) if m.get("kind") == "attribute"]
        if len(attrs) != len(set(attrs)):
            errors.append(f"C3 Failed: Class '{cls.get('title')}' has duplicate attribute names.")
            
    if errors:
        return False, errors
    return True, None


def check_c4(ast):
    """
    C4: Every attribute in standard classes must have an explicit data type (Enums exempted).
    """
    classes = [e for e in ast.get("elements", []) if e.get("name") in ["class", "interface", "abstract"]]
    errors = []
    
    for cls in classes:
        for m in cls.get("members", []):
            if m.get("kind") == "attribute" and not m.get("type"):
                errors.append(f"C4 Failed: Attribute '{m.get('name')}' in class '{cls.get('title')}' lacks an explicit data type.")
                
    if errors:
        return False, errors
    return True, None


def check_c5(ast):
    """
    C5: Every method in standard classes/interfaces/abstract classes must have an explicit return type (Enums exempted).
    """
    classes = [e for e in ast.get("elements", []) if e.get("name") in ["class", "interface", "abstract"]]
    errors = []
    
    for cls in classes:
        for m in cls.get("members", []):
            if m.get("kind") == "method" and not m.get("type"):
                errors.append(f"C5 Failed: Method '{m.get('name')}' in class '{cls.get('title')}' lacks an explicit return type.")
                
    if errors:
        return False, errors
    return True, None


def check_c6(ast):
    """
    C6: Self-associations require a role label.
    """
    relationships = [e for e in ast.get("elements", []) if e.get("name") == "relationship"]
    errors = []
    
    for rel in relationships:
        if rel.get("left") == rel.get("right"):
            if not rel.get("label"):
                errors.append(f"C6 Failed: Self-association on '{rel.get('left')}' missing role name.")
                
    if errors:
        return False, errors
    return True, None


def check_c7(ast):
    """
    C7: Relationships (except inheritance <|-- and realization ..|>) must specify multiplicity bounds on both ends.
    """
    relationships = [e for e in ast.get("elements", []) if e.get("name") == "relationship"]
    errors = []
    
    for rel in relationships:
        arrow = rel.get("arrow", "")
        if "<|" in arrow or "|>" in arrow:
            continue
            
        if not rel.get("leftMultiplicity") or not rel.get("rightMultiplicity"):
            errors.append(f"C7 Failed: Relationship between '{rel.get('left')}' and '{rel.get('right')}' lacks explicit multiplicity bounds.")
            
    if errors:
        return False, errors
    return True, None


def check_c8(ast):
    """
    C8: Relationships must only target explicitly declared classes in the diagram.
    """
    declared_classes = {
        e.get("title") for e in ast.get("elements", []) 
        if e.get("name") in ["class", "interface", "abstract", "enum"]
    }
    
    relationships = [e for e in ast.get("elements", []) if e.get("name") == "relationship"]
    errors = []
    
    for rel in relationships:
        left, right = rel.get("left"), rel.get("right")
        if left not in declared_classes or right not in declared_classes:
            errors.append(f"C8 Failed: Relationship references undefined class ({left} or {right}).")
            
    if errors:
        return False, errors
    return True, None


def check_all_constraints(ast):
    results = {}
    all_errors = []

    checkers = [
        ("C1", check_c1),
        ("C2", check_c2),
        ("C3", check_c3),
        ("C4", check_c4),
        ("C5", check_c5),
        ("C6", check_c6),
        ("C7", check_c7),
        ("C8", check_c8)
    ]

    for rule_id, fn in checkers:
        passed, errors = fn(ast)
        results[rule_id] = passed
        if not passed and errors:
            all_errors.extend(errors)

    results["errors"] = all_errors
    results["all_passed"] = len(all_errors) == 0
    return results