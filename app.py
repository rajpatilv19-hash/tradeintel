import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from compliance import screen_compliance
from matcher import match_buyers
from report import build_report

st.set_page_config(page_title="TradeIntel", page_icon="🚢", layout="wide")
st.title("🚢 TradeIntel")
st.caption("Export screening assistant for Indian agricultural exporters")

DOC_OPTIONS = [
    "FDA facility registration",
    "Commercial invoice",
    "Packing list",
    "Bill of lading",
    "Phytosanitary certificate",
    "Lab report",
    "Process filing (canned low-acid)",
]

# ---------- Input form ----------
with st.form("export_form"):
    c1, c2 = st.columns(2)
    with c1:
        product = st.text_input("Product description", "Alphonso mango pulp frozen drums")
        country = st.selectbox("Target country", ["USA"])
    with c2:
        quantity = st.number_input("Quantity (kg)", min_value=1, value=2000, step=100)
        packaging = st.text_input("Packaging", "frozen drums")
    docs = st.multiselect(
        "Documents you already have", DOC_OPTIONS,
        default=["Commercial invoice", "Packing list"],
    )
    submitted = st.form_submit_button("Run screening", type="primary")

# ---------- Results ----------
if submitted:
    if not product.strip():
        st.warning("Please enter a product description.")
        st.stop()

    comp = screen_compliance(product, country, docs)
    category, buyers_df = match_buyers(product, country, int(quantity), packaging=packaging)

    # Status banner
    if not comp["found"]:
        st.warning(f"No rules available for {category} in {country} yet. Verify with official sources.")
    elif comp["missing"]:
        st.warning("⚠️ Documents missing. Complete them before approaching buyers.")
    else:
        st.success(f"✅ Suitable for further evaluation in the {country} market.")

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Category", category)
    m2.metric("Classified by", "Lookup list" if comp["classified_by"] == "lookup" else "ML model")
    if comp["found"]:
        m3.metric("Documents ready", f"{len(comp['present'])} / {len(comp['needed'])}")

    if comp["classified_by"] == "model":
        st.info("This category was predicted by the ML model, not a known product name. Please verify it.")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Requirements", "✅ Compliance", "🤝 Buyers", "📄 Full report"]
    )

    with tab1:
        if comp["found"]:
            req = comp["requirements"]
            f1, f2, f3, f4, f5 = st.columns(5)
            f1.metric("FDA registration", req["fda_registration"])
            f2.metric("Prior notice", req["prior_notice"])
            f3.metric("FSVP", req["fsvp"])
            f4.metric("Phytosanitary", req["phytosanitary_cert"])
            f5.metric("Pesticide limits", req["pesticide_limits"])

            left, right = st.columns(2)
            with left:
                st.subheader("Labeling")
                for item in req["labeling"].split(";"):
                    st.markdown(f"- {item.strip()}")
            with right:
                st.subheader("Key risks")
                for item in req["key_risks"].split(";"):
                    st.markdown(f"- {item.strip()}")
            st.info(f"**Note:** {req['notes']}")
        else:
            st.write("No rules available.")

    with tab2:
        if comp["found"]:
            left, right = st.columns(2)
            with left:
                st.subheader("You have")
                if comp["present"]:
                    for d in comp["present"]:
                        st.success(f"✓ {d}")
                else:
                    st.write("None of the required documents selected.")
            with right:
                st.subheader("Missing")
                if comp["missing"]:
                    for d in comp["missing"]:
                        st.error(f"⚠ {d}")
                else:
                    st.write("Nothing missing.")
        else:
            st.write("Not available.")

    with tab3:
        if buyers_df.empty:
            st.write(f"No buyers in the database for {country}.")
        else:
            table = buyers_df[["buyer_name", "buyer_type", "match_pct",
                               "text_score", "category_score", "qty_score",
                               "certifications_wanted"]].rename(columns={
                "buyer_name": "Buyer", "buyer_type": "Type", "match_pct": "Match",
                "text_score": "Text", "category_score": "Category",
                "qty_score": "Quantity", "certifications_wanted": "Needs",
            })
            st.dataframe(
                table, hide_index=True, use_container_width=True,
                column_config={
                    "Match": st.column_config.ProgressColumn(
                        "Match", min_value=0, max_value=100, format="%.0f%%"),
                    "Text": st.column_config.NumberColumn(format="%.2f"),
                    "Category": st.column_config.NumberColumn(format="%.0f"),
                    "Quantity": st.column_config.NumberColumn(format="%.0f"),
                },
            )
            st.caption("Buyers are fictional samples. Match = 50% text similarity + 30% category + 20% quantity fit.")

    with tab4:
        report = build_report(product, country, int(quantity), packaging, docs)
        st.code(report, language=None)
        st.download_button("Download report (.txt)", report, file_name="tradeintel_report.txt")