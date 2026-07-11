# 📊 LLM-Pulse: Multi-Source Serverless MLOps Telemetry & Sentiment Analytics Engine

[![CI/CD Quality Gate Checks](https://github.com/sumanthml/LLM-PULSE/actions/workflows/pipeline.yml/badge.svg)](https://github.com/sumanthml/LLM-PULSE/actions)
[![Data Lake Registry](https://img.shields.io/badge/Data%20Lake-Hugging%20Face%20Hub-yellow.svg)](https://huggingface.co/datasets/sunny1820f/llm-pulse-data)
[![Live Analytics UI](https://img.shields.io/badge/Production%20UI-Streamlit%20Cloud-red.svg)](https://llm-pulse.streamlit.app)
[![Python Version Target](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Security Compliance](https://img.shields.io/badge/Security-CVE--2025--32434%20Patched-green.svg)](https://nvd.nist.gov/vuln/detail/CVE-2025-32434)

LLM-Pulse is a production-grade, 24/7 event-driven Natural Language Processing (NLP) telemetry pipeline engineered to track public developer mindshare, adoption kinetics, and sentiment architectures across major foundational AI ecosystems (OpenAI, Anthropic, Google Gemini, Meta Llama). 

Operating on a zero-cost serverless pattern, the platform ingests real-time unstructured streams across 6 network channels, enforces data integrity via rigorous Pydantic V2 contracts, routes components using quantized dual-stage transformer cascades, computes real-time mathematical population drift scores, and runs an in-memory L2-normalized semantic vector distance explorer.

---

## 🏗️ Decoupled System Architecture Blueprint

The platform explicitly follows the **Single Responsibility Principle (SRP)** and isolates ingestion operations from memory-heavy deep-learning transformations and long-running UI states to maximize throughput on free cloud tiers.

```text
                  [ 6 DISTRIBUTED INGESTION NETWORKS ]
    (HackerNews REST API, Reddit Anonymous Scrapers, 4 Tech RSS XML Streams)
                                     │
                                     ▼
                      [ src/utils/validator.py ]
         ──► Strict Pydantic V2 Schema Validation Contract Gate
         ──► Regex Trailing-Symbol Truncation & ISO Time Coercion
                                     │
                                     ▼ (Serverless Event-Cron Loop)
                       [ src/nlp_engine.py ]
         ──► High-Density Keyword Token Pre-Filtering Screen (RAM Saver)
         ──► Stage 1: Zero-Shot Context Entity Classifier (MNLI)
         ──► Stage 2: Twitter-RoBERTa Sentiment Extraction (Quantized CPU)
         ──► Stage 3: Feature Enrichment & Summary Generation
                                     │
                                     ▼
                    [ src/utils/drift_detector.py ]
         ──► Categorical Population Stability Index (PSI) Vector Math
         ──► Epsilon Smoothing Factor Guard against log(0) Infinities
                                     │
                                     ▼
                      [ src/data_storage.py ]
         ──► Non-Destructive Incremental Upsert Logic (Key Deduplication)
         ──► Secure Git-backed Serialization to Hugging Face Hub Data Lake
                                     │
                                     ▼
                      [ app/dashboard.py UI ]
         ──► Streamlit Terminal Presentation Layer with Multi-Tab UI
         ──► Time-To-Live (TTL = 300s) Local Micro-Caching Wrapper
         ──► Real-Time Algebraic L2-Normalized Cosine Similarity Search
