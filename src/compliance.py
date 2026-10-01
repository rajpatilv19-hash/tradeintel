from market import get_market_requirements

# Keywords that identify each document inside the `documents` column text.
# Key = the name shown to the user, value = words to look for in the rules text.
DOC_KEYWORDS = {
    "FDA facility registration": ["fda facility registration"],
    "Commercial invoice": ["commercial invoice"],
    "Packing list": ["packing list"],
    "Bill of lading": ["bill of lading"],
    "Phytosanitary certificate": ["phytosanitary certificate"],
    "Lab report": ["lab report", "aflatoxin lab report"],
    "Process filing (canned low-acid)": ["process filing"],
}


def required_documents(requirements):
    """Return the list of documents named in the rules for this category."""
    text = requirements["documents"].lower()
    needed = []
    for doc, words in DOC_KEYWORDS.items():
        if any(w in text for w in words):
            needed.append(doc)
    return needed


def screen_compliance(product_description, country, documents_held):
    result = get_market_requirements(product_description, country)
    if not result["found"]:
        return {**result, "status": "No rules available", "missing": [], "present": []}

    needed = required_documents(result["requirements"])
    held = {d.strip().lower() for d in documents_held}

    present = [d for d in needed if d.lower() in held]
    missing = [d for d in needed if d.lower() not in held]

    status = "Ready for further evaluation" if not missing else "Documents missing"
    return {**result, "needed": needed, "present": present, "missing": missing, "status": status}


if __name__ == "__main__":
    r = screen_compliance(
        "Alphonso mango pulp frozen drums",
        "USA",
        ["FDA facility registration", "Commercial invoice", "Packing list"],
    )
    print(f"Product : {r['product']} -> {r['category']}")
    print(f"Status  : {r['status']}")
    for d in r["present"]:
        print(f"  ✓ {d}")
    for d in r["missing"]:
        print(f"  ⚠ MISSING: {d}")
    print("\nWatch out for:", r["requirements"]["key_risks"])
    print("Note:", r["requirements"]["notes"])