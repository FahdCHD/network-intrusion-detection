# Network Intrusion Detection using Machine Learning

A machine learning project that classifies network traffic as **normal** or **attack** using the NSL-KDD dataset. Implements both Random Forest and Logistic Regression models, deployed as an interactive Streamlit web application.

## Problem Statement

Network intrusion detection is a critical cybersecurity challenge. Traditional rule-based Intrusion Detection Systems (IDS) rely on static signatures and may miss novel or subtle attack patterns. This project applies machine learning to automatically learn patterns that distinguish normal network traffic from malicious connections, enabling more adaptive and generalized threat detection.

## Dataset

**NSL-KDD** (Network Security Laboratory - Knowledge Discovery in Databases)
- **Size:** 22,544 network connection records in the test set
- **Features:** 41 network features (duration, protocol type, service, bytes transferred, connection flags, error rates, etc.)
- **Target:** Binary classification
  - `normal` (9,711 samples, 43%)
  - `anomaly` (12,833 samples, 57%)
- **Source:** [University of New Brunswick](https://www.unb.ca/cic/datasets/nsl.html) — cleaned and refined version of the original KDD Cup 1999 dataset

### Feature Engineering

Raw features are preprocessed as follows:
- **Categorical encoding:** `protocol_type`, `service`, and `flag` are one-hot encoded (expanding to 116 total features)
- **Numeric scaling:** StandardScaler normalizes all numeric features to zero mean, unit variance
- **Missing values:** NSL-KDD is clean; no imputation required

## Approach

### 1. Data Exploration
- Analyzed class distribution (mild imbalance, 57/43) — no special handling needed
- Identified 3 categorical features requiring encoding
- Examined feature ranges and distributions

### 2. Preprocessing
- One-hot encoded categorical columns → 116 total features
- Scaled numeric features using StandardScaler
- Stratified 80/20 train/test split (preserves class ratios)

### 3. Model Selection
Trained two baseline models for comparison:

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|-----|
| Logistic Regression | 95.4% | 0.952 | 0.967 | 0.960 |
| **Random Forest** | **98.8%** | **0.991** | **0.989** | **0.990** |

**Random Forest outperformed** on all metrics, particularly on recall (catching 99% of actual attacks), which is critical in security applications.

### 4. Evaluation

**Random Forest Confusion Matrix (test set, 4,509 samples):**
```
                Predicted Normal  Predicted Anomaly
Actual Normal   1918              24  (false positives)
Actual Anomaly  29                2538 (true positives)
```

**Security Interpretation:**
- **True Positives (2538):** Correctly detected attacks
- **False Negatives (29):** Missed attacks (~1.1% of actual attacks) — a key risk in real systems
- **False Positives (24):** Legitimate traffic flagged as attack (~1.2%) — annoying but safer than missing attacks
- **Model Recall:** 0.989 — catches 98.9% of actual intrusions

## Feature Importance

The top 15 features driving the model's decisions (and their security significance):

| Rank | Feature | Importance | Security Meaning |
|------|---------|-----------|------------------|
| 1 | `src_bytes` | 0.131 | Abnormal byte volumes often signal attacks (DoS floods, exfiltration) |
| 2 | `dst_bytes` | 0.100 | Response size anomalies can indicate malicious behavior |
| 3 | `service_http` | 0.061 | HTTP is frequently both legitimate and targeted; service type matters for context |
| 4 | `dst_host_diff_srv_rate` | 0.060 | High rate of different services = **port scanning signature** |
| 5 | `dst_host_rerror_rate` | 0.050 | Rejected connections indicate probing/scanning behavior |
| 6 | `flag_SF` | 0.049 | Normal TCP handshake + close; abnormal flags suggest incomplete/malicious connections |
| 7 | `dst_host_same_srv_rate` | 0.045 | Repeated access to same service = normal; variety = suspicious |
| 8 | `dst_host_srv_count` | 0.045 | Connection frequency to specific services; high = potential scanning |
| 9 | `duration` | 0.036 | Abnormal session lengths can indicate DoS or incomplete attacks |
| 10-15 | Connection rate/count features | 0.025-0.024 | All variations on **temporal behavior**; attacks often show burst/scanning patterns |

**Key Insight:** The model learned classic intrusion detection signatures: byte volume anomalies, service/port scanning patterns (hitting many different services rapidly), connection error rates, and abnormal frequency patterns. These map directly to real-world attack indicators, validating the model's logic.

## Usage

### Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FahdCHD/network-intrusion-detection.git
   cd network-intrusion-detection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Open in your browser:** `http://localhost:8501`

## App Features

- **Interactive input form:** Select protocol type, service, connection flag, and enter numeric features
- **Dual model comparison:** See predictions from both Random Forest and Logistic Regression side-by-side
- **Confidence scores:** Probability estimates help interpret model certainty
- **Disagreement detection:** Alerts when the two models disagree (useful for manual review)

## Files

- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
- `rf_model.pkl` — Trained Random Forest model
- `log_reg_model.pkl` — Trained Logistic Regression model
- `scaler.pkl` — StandardScaler fitted on training data
- `feature_columns.pkl` — List of 116 feature names (after one-hot encoding) in order
- `network_intrusion_detection.ipynb` — Full Jupyter notebook (data loading, preprocessing, training, evaluation)

## Lessons Learned & Next Steps

1. **Multi-class classification:** Current model is binary (normal vs any attack). Extend to distinguish attack types (DoS, Probe, R2L, U2R) for more granular threat response.

2. **Modern dataset:** NSL-KDD is from 2009. Test on CICIDS2017 or UNSW-NB15 for contemporary attack patterns and higher-speed traffic.

3. **Anomaly detection:** Try one-class SVM or autoencoders for unsupervised detection — useful when labeled attack data is scarce or attack types are unknown.

4. **Feature engineering:** Extract time-series features (connection rate trends) or n-gram patterns in payload data if available.

5. **Model interpretability:** Use SHAP values for per-prediction explanations — useful in production when security teams need to trust and understand model decisions.

6. **Real-time deployment:** Package as a Flask/FastAPI microservice to integrate into actual network monitoring pipelines.

7. **Class imbalance handling:** Test SMOTE or class weighting to see if recall improves for actual attacks if the dataset becomes more imbalanced.

## Tools & Technologies

- **Python 3.14**
- **scikit-learn** — model training and evaluation
- **pandas, numpy** — data manipulation
- **Streamlit** — web app deployment
- **joblib** — model serialization

## Author Notes

This project combines both machine learning and cybersecurity knowledge, demonstrating:
- End-to-end ML pipeline from raw data to production app
- Security-aware model interpretation (false negatives vs false positives matter differently in security)
- Feature importance aligned with real-world attack signatures
- Proper separation of training (Colab notebook) and inference (Streamlit app with saved models)

Perfect for portfolios, interviews, or as a foundation for exploring modern IDS architectures.

---

**Repo:** [github.com/FahdCHD/network-intrusion-detection](https://github.com/FahdCHD/network-intrusion-detection)
