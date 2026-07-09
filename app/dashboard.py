import streamlit as st
import pandas as pd

# Target data path inside your versioned data lake
DATA_URL = "https://huggingface.co/datasets/sunny1820f/llm-pulse-data/raw/main/llm_pulse_telemetry.csv"

st.set_page_config(
    page_title="LLM-Pulse: GenAI Sentiment Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 LLM-Pulse: Continuous Sentiment Analytics Engine")
st.markdown("""
This production-grade MLOps system tracks and runs sentiment analysis on developer discussions 
regarding the Generative AI ecosystem. **Pipeline Status: Active 24/7 (via GitHub Actions & Hugging Face)**.
""")

@st.cache_data(ttl=600)  # Caches for 10 minutes to protect network bandwidth constraints
def load_pipeline_data():
    """
    Fetches the latest telemetry updates directly from the versioned Hugging Face data lake.
    """
    try:
        # Read data schema safely
        df = pd.read_csv(DATA_URL)
        
        if not df.empty and "timestamp" in df.columns:
            # Safely cast ISO timestamp strings into explicit datetime indices
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
            df = df.dropna(subset=["timestamp"])
        return df
    except Exception as e:
        st.error(f"Could not connect to the Hugging Face Data Lake: {e}")
        return pd.DataFrame(columns=["id", "timestamp", "source", "raw_text", "target_entity", "sentiment_label", "sentiment_score"])

df = load_pipeline_data()

if df.empty:
    st.info("The Data Lake is currently initializing. Once your background GitHub Actions cron completes its first workflow run, live insights will populate below.")
else:
    # High-Yield Operations KPI Rows
    total_records = len(df)
    last_updated = df["timestamp"].max().strftime('%Y-%m-%d %H:%M:%S') if not df.empty else "N/A"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Logged Event Tracks", value=total_records)
    with col2:
        st.metric(label="Pipeline Validation Gate", value="Pydantic V2 Strict")
    with col3:
        st.metric(label="Last Execution Sync (UTC)", value=last_updated)
        
    st.markdown("---")
    
    # Dual Visualization Analytics Layout
    left_chart_col, right_chart_col = st.columns(2)
    
    with left_chart_col:
        st.subheader("🔥 Ecosystem Conversation Volume")
        if "target_entity" in df.columns:
            mention_counts = df["target_entity"].value_counts()
            st.bar_chart(mention_counts)
        
    with right_chart_col:
        st.subheader("🎭 Sentiment Distribution across Mentions")
        if "target_entity" in df.columns and "sentiment_label" in df.columns:
            sentiment_crosstab = pd.crosstab(df["target_entity"], df["sentiment_label"])
            st.dataframe(sentiment_crosstab, use_container_width=True)

    st.markdown("---")
    
    # Telemetry Log Frame Viewer
    st.subheader("📋 Live Consolidated Inference Feed")
    display_cols = ["timestamp", "target_entity", "sentiment_label", "sentiment_score", "raw_text"]
    available_cols = [c for c in display_cols if c in df.columns]
    
    st.dataframe(
        df[available_cols].sort_values(by="timestamp", ascending=False),
        use_container_width=True
    )