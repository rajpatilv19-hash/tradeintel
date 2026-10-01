import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from predict import classify

BASE_DIR = Path(__file__).resolve().parent.parent
buyers = pd.read_csv(BASE_DIR / "data" / "buyers.csv")

# Text profile for each buyer
buyers["profile"] = (
    buyers["products_wanted"] + " " + buyers["packaging_preference"] + " " + buyers["category"]
)


def match_buyers(product_description, country, quantity_kg, packaging="", top_n=3):
    category, _, _ = classify(product_description)

    pool = buyers[buyers["country"].str.lower() == country.lower()].copy()
    if pool.empty:
        return category, pool

    # 1. Text similarity (TF-IDF + cosine)
    query = f"{product_description} {packaging} {category}"
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(pool["profile"].tolist() + [query])
    pool["text_score"] = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    # 2. Category match (same category = 1, otherwise 0)
    pool["category_score"] = (pool["category"] == category).astype(float)

    # 3. Quantity fit (1 if inside the buyer's range, otherwise 0)
    pool["qty_score"] = (
        (quantity_kg >= pool["min_qty_kg"]) & (quantity_kg <= pool["max_qty_kg"])
    ).astype(float)

    # Weighted final score
    pool["match_pct"] = (
        0.5 * pool["text_score"] + 0.3 * pool["category_score"] + 0.2 * pool["qty_score"]
    ) * 100

    cols = ["buyer_name", "buyer_type", "match_pct", "text_score", "category_score", "qty_score",
            "certifications_wanted"]
    ranked = pool.sort_values("match_pct", ascending=False)
    ranked = ranked[ranked["match_pct"] >= 40]  # drop weak matches
    return category, ranked.head(top_n)[cols]
    return category, pool.sort_values("match_pct", ascending=False).head(top_n)[cols]


if __name__ == "__main__":
    category, top = match_buyers(
        "Alphonso mango pulp frozen drums", "USA", 2000, packaging="frozen drums"
    )
    print(f"Category: {category}\n")
    for _, row in top.iterrows():
        print(f"{row['buyer_name']:32} {row['match_pct']:5.0f}% match  ({row['buyer_type']})")
        print(f"   needs: {row['certifications_wanted']}")