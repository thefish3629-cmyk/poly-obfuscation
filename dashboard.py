import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.postgres_store import PostgresStore
from src.analysis.reporter import Reporter
from src.storage.graph_store import GraphStore

st.set_page_config(page_title="Polymarket Obfuscation Detector", layout="wide")

st.title("Polymarket Obfuscation Detection Dashboard")

st.sidebar.header("Configuration")
min_risk_score = st.sidebar.slider("Minimum Risk Score", 0, 100, 25)


def load_data():
    store = PostgresStore()
    reporter = Reporter(store)
    summary = reporter.generate_executive_summary()
    flagged = reporter.risk_scorer.get_flagged_wallets(min_score=min_risk_score)
    return summary, flagged, store


try:
    summary, flagged_wallets, store = load_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    dist = summary.get("risk_distribution", {})
    
    with col1:
        st.metric("Total Wallets", summary.get("total_wallets_analyzed", 0))
    with col2:
        st.metric("Flagged Wallets", summary.get("flagged_wallets", 0))
    with col3:
        critical = dist.get("critical_risk", {}).get("count", 0)
        st.metric("Critical Risk", critical, delta="ALERT" if critical > 0 else None)
    with col4:
        high = dist.get("high_risk", {}).get("count", 0)
        st.metric("High Risk", high)
    
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Risk Distribution")
        risk_data = {
            "Category": ["Low (<25)", "Medium (25-50)", "High (50-75)", "Critical (>75)"],
            "Count": [
                dist.get("low_risk", {}).get("count", 0),
                dist.get("medium_risk", {}).get("count", 0),
                dist.get("high_risk", {}).get("count", 0),
                dist.get("critical_risk", {}).get("count", 0),
            ]
        }
        df_risk = pd.DataFrame(risk_data)
        st.bar_chart(df_risk.set_index("Category"))
    
    with col2:
        st.subheader("Top Flagged Wallets")
        if flagged_wallets:
            display_data = []
            for w in flagged_wallets[:20]:
                display_data.append({
                    "Address": w["address"][:20] + "...",
                    "Risk Score": f"{w['risk_score']:.1f}",
                    "Flags": len(w.get("flags", []))
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info("No wallets meet the risk threshold")
    
    st.divider()
    
    st.subheader("Detailed Flag Analysis")
    if flagged_wallets:
        selected = st.selectbox(
            "Select wallet to inspect",
            options=range(len(flagged_wallets)),
            format_func=lambda i: f"{flagged_wallets[i]['address'][:20]}... (Score: {flagged_wallets[i]['risk_score']:.1f})"
        )
        
        wallet = flagged_wallets[selected]
        wallet_report = Reporter(store).generate_wallet_report(wallet["address"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Flags:**")
            for flag in wallet_report.get("flags", []):
                st.write(f"- {flag['type']}: {flag['confidence']:.1f}% confidence")
        
        with col2:
            st.write("**Funding Sources:**")
            sources = wallet_report.get("funding_sources", [])
            if sources:
                for src in sources[:5]:
                    st.write(f"- {src['type']}: {src['from'][:20]}...")
            else:
                st.info("No funding data available")
    
    st.divider()
    
    st.subheader("Recommendations")
    for rec in summary.get("recommendations", []):
        if "CRITICAL" in rec or "ALERT" in rec:
            st.error(rec)
        elif "WARNING" in rec or "HIGH" in rec:
            st.warning(rec)
        else:
            st.info(rec)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure the database is running and data has been ingested.")
