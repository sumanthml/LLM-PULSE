import streamlit as st
import pandas as pd

DATA_URL = "https://huggingface.co/datasets/sunny1820f/llm-pulse-data/raw/main/llm_pulse_telemetry.csv"

st.set_page_config(page_title="LLM-Pulse Core Terminal", page_icon="⚙️", layout="wide")

st.title("📊 LLM-Pulse: Real-Time Multi-Source Competition Telemetry")

@st.cache_data(ttl=300)
def fetch_telemetry_lake():
    try:
        df = pd.read_csv(DATA_URL)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        return df.dropna(subset=["timestamp"])
    except Exception:
        return pd.DataFrame(columns=["id", "timestamp", "source", "raw_text", "target_entity", "sentiment_label", "sentiment_score"])

df = fetch_telemetry_lake()

# Interactive Sidebar Configurations
st.sidebar.header("🎯 Pipeline Diagnostics & Filters")
st.sidebar.markdown("Use these parameters to isolate specific records in real time.")

# 1. Source System Filter Multi-Select
if not df.empty:
    all_sources = df["source"].unique().tolist()
    selected_sources = st.sidebar.multiselect("Filter Data Sources", all_sources, default=all_sources)
    
    # 2. ML Inference Score Slider
    confidence_cutoff = st.sidebar.slider("Minimum Model Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    
    # Apply Filtering Rules Dynamically
    mask = (df["source"].isin(selected_sources)) & (df["sentiment_score"] >= confidence_cutoff)
    filtered_df = df[mask]
else:
    filtered_df = df

# Structure Multi-Tab Terminal Layout
tab1, tab2, tab3 = st.tabs(["📈 Executive Overview", "🔬 Linguistic Sentiment Volatility", "📋 Relational Data Lake Logs"])

with tab1:
    if filtered_df.empty:
        st.info("No logs match your selected filter criteria.")
    else:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Ingested Records Tracked", len(filtered_df))
        kpi2.metric("Active Streams", filtered_df["source"].nunique())
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
    if not filtered_df.empty:
        st.subheader("🎭 Cross-Tabulation Model Sentiment Breakdown")
        ct = pd.crosstab(filtered_df["target_entity"], filtered_df["sentiment_label"])
        st.dataframe(ct, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🕒 Chronological Tracking Matrix")
        filtered_df["Date"] = filtered_df["timestamp"].dt.date
        time_chart = filtered_df.groupby(["Date", "target_entity"]).size().unstack(fill_value=0)
        st.line_chart(time_chart)

with tab3:
    st.subheader("📂 Real-Time Relational Data Frame Logs")
    if not filtered_df.empty:
        search_query = st.text_input("🔍 Search within text records:")
        display_df = filtered_df.sort_values(by="timestamp", ascending=False)
        if search_query:
            display_df = display_df[display_df["raw_text"].str.contains(search_query, case=False, na=False)]
        st.dataframe(display_df[["timestamp", "source", "target_entity", "sentiment_label", "sentiment_score", "raw_text"]], use_container_width=True)
    else:
        st.info("Data lake folder structures are empty.")