from compliance import screen_compliance
from matcher import match_buyers

DISCLAIMER = (
    "This report is a screening aid based on a curated sample dataset. "
    "It is not legal or customs advice. Verify all requirements with FDA, "
    "USDA-APHIS, and your customs broker."
)


def build_report(product, country, quantity_kg, packaging, documents_held):
    comp = screen_compliance(product, country, documents_held)
    category, top = match_buyers(product, country, quantity_kg, packaging=packaging)

    L = []
    L.append("=" * 60)
    L.append("TRADEINTEL EXPORT SCREENING REPORT")
    L.append("=" * 60)
    L.append(f"Product  : {product}")
    L.append(f"Target   : {country}")
    L.append(f"Quantity : {quantity_kg:,} kg   Packaging: {packaging}")

    # 1. Classification
    L.append("\n1. PRODUCT CLASSIFICATION")
    L.append(f"   Category: {category}  (decided by {comp['classified_by']})")

    # 2. Market requirements
    L.append("\n2. MARKET REQUIREMENTS")
    if comp["found"]:
        req = comp["requirements"]
        L.append(f"   Labeling  : {req['labeling']}")
        L.append(f"   Key risks : {req['key_risks']}")
        L.append(f"   Note      : {req['notes']}")
    else:
        L.append(f"   No rules available for {category} in {country}.")

    # 3. Compliance screening
    L.append("\n3. COMPLIANCE SCREENING")
    if comp["found"]:
        for d in comp["present"]:
            L.append(f"   [OK]      {d}")
        for d in comp["missing"]:
            L.append(f"   [MISSING] {d}")
    else:
        L.append("   Not available.")

    # 4. Buyer matching
    L.append("\n4. BUYER MATCHING (sample buyers)")
    if top.empty:
        L.append(f"   No buyers in the database for {country}.")
    else:
        for _, row in top.iterrows():
            L.append(f"   {row['buyer_name']:30} {row['match_pct']:3.0f}% match ({row['buyer_type']})")
            L.append(f"      needs: {row['certifications_wanted']}")

    # 5. Recommendation
    L.append("\n5. RECOMMENDATION")
    if not comp["found"]:
        rec = f"No rules for {category} in {country} yet. Verify requirements with official sources."
    elif comp["missing"]:
        rec = "Complete the missing documents before approaching buyers."
    else:
        rec = f"Suitable for further evaluation in the {country} market."
    L.append(f"   {rec}")

    L.append("\n" + DISCLAIMER)
    return "\n".join(L)


if __name__ == "__main__":
    print(build_report(
        product="Alphonso mango pulp frozen drums",
        country="USA",
        quantity_kg=2000,
        packaging="frozen drums",
        documents_held=["FDA facility registration", "Commercial invoice", "Packing list"],
    ))