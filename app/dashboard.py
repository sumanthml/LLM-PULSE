import streamlit as st
import pandas as pd
import ast

DATA_URL = "https://huggingface.co/datasets/sunny1820f/llm-pulse-data/raw/main/llm_pulse_telemetry.csv"

st.set_page_config(page_title="LLM-Pulse Core Terminal", page_icon="⚙️", layout="wide")

st.title("📊 LLM-Pulse: Multi-Source Market Intelligence Terminal")
st.markdown("---")

@st.cache_data(ttl=300)
def fetch_telemetry_lake():
    try:
        df = pd.read_csv(DATA_URL)
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
            return df.dropna(subset=["timestamp"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "timestamp", "source", "raw_text", "target_entity", "sentiment_label", "sentiment_score", "executive_summary", "semantic_vector"])

df = fetch_telemetry_lake()

st.sidebar.header("🎯 Pipeline Diagnostics & Filters")

if not df.empty:
    all_sources = df["source"].unique().tolist()
    selected_sources = st.sidebar.multiselect("Active Network Channels", all_sources, default=all_sources)
    confidence_cutoff = st.sidebar.slider("Minimum Model Certainty Threshold", 0.0, 1.0, 0.35, 0.05)
    
    mask = (df["source"].isin(selected_sources)) & (df["sentiment_score"] >= confidence_cutoff)
    filtered_df = df[mask]
else:
    filtered_df = df

tab1, tab2, tab3 = st.tabs(["📈 Executive Overview", "🔬 Volatility & Trend Tracking", "🔍 Semantic Vector Space Log Explorer"])

with tab1:
    if filtered_df.empty:
        st.info("No logs match your selected filter criteria.")
    else:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Ingested Records Tracked", len(filtered_df))
        kpi2.metric("Active Streams Detected", filtered_df["source"].nunique())
        kpi3.metric("Leading Mindshare Model", filtered_df["target_entity"].value_counts().index[0])
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔥 Dynamic Mindshare Mention Volume")
            st.bar_chart(filtered_df["target_entity"].value_counts())
        with c2:
            st.subheader("🌐 Volume Contribution by Source Channel")
            st.bar_chart(filtered_df["source"].value_counts())

with tab2:
    if filtered_df.empty:
        st.info("No records match your selected filter criteria.")
    else:
        st.subheader("🎭 Sentiment Distribution across Foundations")
        if "sentiment_label" in filtered_df.columns:
            ct = pd.crosstab(filtered_df["target_entity"], filtered_df["sentiment_label"])
            st.dataframe(ct, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🕒 Chronological Trend Matrix Log Distributions")
        filtered_df["Date"] = filtered_df["timestamp"].dt.date
        time_chart = filtered_df.groupby(["Date", "target_entity"]).size().unstack(fill_value=0)
        st.line_chart(time_chart)

with tab3:
    st.subheader("📂 Real-Time Vector Similarity Log Search Engine")
    if filtered_df.empty:
        st.info("No records match your selected filter criteria.")
    else:
        user_query = st.text_input("🔍 Contextual Semantic Search (e.g., enter 'error', 'amazing', or 'limit'):")
        display_df = filtered_df.copy().sort_values(by="timestamp", ascending=False)
        
        if user_query and "semantic_vector" in display_df.columns:
            from src.utils.vector_ops import compute_lightweight_token_hash
            query_vector = compute_lightweight_token_hash(user_query)
            
            def evaluate_vector_similarity(row_vec_str):
                try:
                    if pd.isna(row_vec_str):
                        return 0.0
                    r_vec = ast.literal_eval(str(row_vec_str))
                    return sum(q * r for q, r in zip(query_vector, r_vec))
                except Exception:
                    return 0.0
            
            display_df["Similarity_Score"] = display_df["semantic_vector"].apply(evaluate_vector_similarity)
            display_df = display_df.sort_values(by="Similarity_Score", ascending=False)
        
        output_cols = ["timestamp", "source", "target_entity", "sentiment_label", "sentiment_score", "executive_summary"]
        available_output = [col for col in output_cols if col in display_df.columns]
        st.dataframe(display_df[available_output], use_container_width=True)