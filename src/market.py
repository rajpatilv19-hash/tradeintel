import pandas as pd
from pathlib import Path
from predict import classify

BASE_DIR = Path(__file__).resolve().parent.parent
rules = pd.read_csv(BASE_DIR / "data" / "market_rules.csv")


def get_market_requirements(product_description, country):
    """Classify the product, then look up the rules for that category and country."""
    category, method, keyword = classify(product_description)

    match = rules[
        (rules["country"].str.lower() == country.lower())
        & (rules["category"] == category)
    ]

    result = {
        "product": product_description,
        "country": country,
        "category": category,
        "classified_by": method,
        "matched_keyword": keyword,
        "found": not match.empty,
    }
    if not match.empty:
        result["requirements"] = match.iloc[0].drop(["country", "category"]).to_dict()
    return result


if __name__ == "__main__":
    for item in ["Alphonso mango pulp frozen drums", "Fresh Nashik onion", "Cumin seeds Gujarat"]:
        r = get_market_requirements(item, "USA")
        print("=" * 60)
        print(f"{r['product']}  ->  {r['category']} ({r['classified_by']})")
        if r["found"]:
            for k, v in r["requirements"].items():
                print(f"  {k:20}: {v}")
        else:
            print("  No rules found for this country and category.")