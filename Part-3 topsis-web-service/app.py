import streamlit as st
import pandas as pd
import numpy as np
import re
import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "arshnoorsingh.05@gmail.com"
APP_PASSWORD = "dlhhovirseqiakxn"

def send_email(receiver_email, file_bytes):
    msg = EmailMessage()
    msg["Subject"] = "TOPSIS Result"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content("Attached is your TOPSIS result file.")
    msg.add_attachment(file_bytes,
                       maintype="application",
                       subtype="octet-stream",
                       filename="result.csv")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

def valid_email(e):
    return re.match(r"[^@]+@[^@]+\.[^@]+", e)

st.title("TOPSIS Web Service")

uploaded_file = st.file_uploader("Upload CSV/XLSX file")
weights = st.text_input("Weights (comma separated)")
impacts = st.text_input("Impacts (+ or -, comma separated)")
email = st.text_input("Email")

if st.button("Submit"):

    if uploaded_file is None:
        st.error("Upload a file")
        st.stop()

    if not valid_email(email):
        st.error("Invalid email")
        st.stop()

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if df.shape[1] < 3:
        st.error("File must have at least 3 columns")
        st.stop()

    try:
        data = df.iloc[:, 1:].astype(float)
    except:
        st.error("Criteria columns must be numeric")
        st.stop()

    weights_list = weights.split(",")
    impacts_list = impacts.split(",")

    if len(weights_list) != len(impacts_list) or len(weights_list) != data.shape[1]:
        st.error("Weights and impacts count mismatch")
        st.stop()

    try:
        weights_list = [float(i) for i in weights_list]
    except:
        st.error("Weights must be numeric")
        st.stop()

    for i in impacts_list:
        if i not in ['+','-']:
            st.error("Impacts must be + or -")
            st.stop()

    norm = data / np.sqrt((data**2).sum(axis=0))
    weighted = norm * weights_list

    best = []
    worst = []

    for i in range(len(impacts_list)):
        if impacts_list[i] == '+':
            best.append(weighted.iloc[:, i].max())
            worst.append(weighted.iloc[:, i].min())
        else:
            best.append(weighted.iloc[:, i].min())
            worst.append(weighted.iloc[:, i].max())

    best = np.array(best)
    worst = np.array(worst)

    d_best = np.sqrt(((weighted - best)**2).sum(axis=1))
    d_worst = np.sqrt(((weighted - worst)**2).sum(axis=1))

    score = d_worst / (d_best + d_worst)

    df["Topsis Score"] = score
    df["Rank"] = score.rank(method='max', ascending=False)

    csv = df.to_csv(index=False).encode()

    try:
        send_email(email, csv)
        st.success("Result sent to email")
    except:
        st.error("Email failed")

    st.download_button("Download Result", csv, "result.csv")
