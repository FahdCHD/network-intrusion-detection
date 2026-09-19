import streamlit as st
import pandas as pd
import joblib

# ---- Load model artifacts ----
rf = joblib.load('rf_model.pkl')
log_reg = joblib.load('log_reg_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_columns = joblib.load('feature_columns.pkl')

st.set_page_config(page_title="Network Intrusion Detector", page_icon="🛡️")
st.title("🛡️ Network Intrusion Detector")
st.write("Enter connection details below to check whether it looks like **normal traffic** or an **attack** — compared across two models.")

st.subheader("Connection details")

col1, col2 = st.columns(2)
with col1:
    duration = st.number_input("Duration (seconds)", min_value=0, value=0)
    src_bytes = st.number_input("Source bytes", min_value=0, value=0)
    dst_bytes = st.number_input("Destination bytes", min_value=0, value=0)
    count = st.number_input("Count (connections to same host, last 2s)", min_value=0, value=1)
with col2:
    protocol_type = st.selectbox("Protocol type", ["tcp", "udp", "icmp"])
    service = st.selectbox("Service", ["http", "ftp", "smtp", "telnet", "private", "domain_u", "other"])
    flag = st.selectbox("Connection flag", ["SF", "S0", "REJ", "RSTR", "RSTO", "other"])
    logged_in = st.selectbox("Logged in successfully?", ["No", "Yes"])

predict_clicked = st.button("Predict", type="primary")

if predict_clicked:
    # Start with all zeros for every feature the model was trained on
    input_dict = {col: 0 for col in feature_columns}

    # Fill in the numeric fields we collected
    input_dict['duration'] = duration
    input_dict['src_bytes'] = src_bytes
    input_dict['dst_bytes'] = dst_bytes
    input_dict['count'] = count
    input_dict['logged_in'] = 1 if logged_in == "Yes" else 0

    # Fill in the one-hot categorical fields — only set the matching column to 1
    protocol_col = f'protocol_type_{protocol_type}'
    service_col = f'service_{service}'
    flag_col = f'flag_{flag}'

    if protocol_col in input_dict:
        input_dict[protocol_col] = 1
    if service_col in input_dict:
        input_dict[service_col] = 1
    else:
        st.warning(f"Service '{service}' wasn't one of the one-hot columns from training — treating as unknown/other.")
    if flag_col in input_dict:
        input_dict[flag_col] = 1
    else:
        st.warning(f"Flag '{flag}' wasn't one of the one-hot columns from training — treating as unknown/other.")

    # Build the row in the exact column order the model expects
    input_df = pd.DataFrame([input_dict])[feature_columns]
    input_scaled = scaler.transform(input_df)

    # Predict with both models
    rf_pred = rf.predict(input_scaled)[0]
    rf_proba = rf.predict_proba(input_scaled)[0][1]

    lr_pred = log_reg.predict(input_scaled)[0]
    lr_proba = log_reg.predict_proba(input_scaled)[0][1]

    st.subheader("Results")
    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.markdown("**Random Forest**")
        if rf_pred == 1:
            st.error(f"⚠️ Anomaly — {rf_proba:.1%} confidence")
        else:
            st.success(f"✅ Normal — {1 - rf_proba:.1%} confidence")

    with res_col2:
        st.markdown("**Logistic Regression**")
        if lr_pred == 1:
            st.error(f"⚠️ Anomaly — {lr_proba:.1%} confidence")
        else:
            st.success(f"✅ Normal — {1 - lr_proba:.1%} confidence")

    if rf_pred != lr_pred:
        st.info("ℹ️ The two models disagree on this one — a good case to look at manually.")
