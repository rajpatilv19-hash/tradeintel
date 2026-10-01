import re
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_MARKERS = [
    "pulp", "puree", "juice", "concentrate", "canned", "jam", "pickle",
    "squash", "candy", "syrup", "frozen", "dried", "dehydrated", "iqf",
    "paste", "sweetened", "tetra pack",
]

lookup = pd.read_csv(BASE_DIR / "data" / "product_lookup.csv")
lookup["keyword"] = lookup["keyword"].str.lower().str.strip()
lookup = lookup.sort_values(by="keyword", key=lambda s: s.str.len(), ascending=False)

model = joblib.load(BASE_DIR / "models" / "classifier.joblib")


def has_word(text, word):
    """True if `word` appears as a whole word (simple plural forms allowed)."""
    pattern = re.escape(word)
    if word.endswith("y"):
        pattern = re.escape(word[:-1]) + r"(?:y|ies)"
    else:
        pattern += r"(?:s|es)?"
    return re.search(r"\b" + pattern + r"\b", text) is not None

def classify(description):
    """Return (category, method, matched_keyword)."""
    text = description.lower()
    for keyword, category in zip(lookup["keyword"], lookup["category"]):
        if has_word(text, keyword):
            if category == "Fresh Fruit" and any(has_word(text, m) for m in PROCESSED_MARKERS):
                category = "Processed Fruit"
            return category, "lookup", keyword
    return model.predict([description])[0], "model", None


if __name__ == "__main__":
    tests = [
        ("Frozen guava pulp 20 kg", "Processed Fruit"),
        ("Fresh tomato hybrid grade A", "Vegetables"),
        ("Cumin seeds Gujarat", "Spices"),
        ("Raw peanuts in shell", "Nuts"),
        ("Fresh strawberries cold chain", "Fresh Fruit"),
        ("Mango juice 1 litre pack", "Processed Fruit"),
        ("Sweet potato fresh", "Vegetables"),
        ("Fresh radish white", "Vegetables"),       # not in lookup -> model
        ("Fresh dates Medjool", "Fresh Fruit"),     # not in lookup -> model
        ("Amaranth grain", "Cereals and Flour"),    # not in lookup -> model
    ]
    correct = 0
    for text, expected in tests:
        category, method, keyword = classify(text)
        ok = category == expected
        correct += ok
        print(f"{'OK ' if ok else 'ERR'} | {text:35} -> {category:18} via {method} ({keyword})")
    print(f"\n{correct}/{len(tests)} correct")