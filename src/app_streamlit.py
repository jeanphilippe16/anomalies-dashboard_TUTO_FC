from pathlib import Path
import json
import pandas as pd
import streamlit as st
import sys
from pathlib import Path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
from detect_anomalies import detect

st.set_page_config(page_title="Détection d'anomalies", layout="wide")

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = BASE_DIR / "config" / "thresholds.json"
ALERTS_PATH = DATA_DIR / "alerts_output.csv"

st.title("Tableau d'alertes — anomalies administratives et financières")
st.caption("Démo interactive pour MOA / MOE / Finance / Scolarité")

if st.button("Rafraîchir les alertes à partir des CSV source"):
    refreshed = detect(DATA_DIR, CONFIG_PATH)
    refreshed.to_csv(ALERTS_PATH, index=False, encoding="utf-8-sig")
    st.success(f"{len(refreshed)} alertes recalculées.")

students = pd.read_csv(DATA_DIR / "students.csv")
payments = pd.read_csv(DATA_DIR / "payments.csv")
grades = pd.read_csv(DATA_DIR / "grades.csv")
finance = pd.read_csv(DATA_DIR / "finance_transactions.csv")
alerts = pd.read_csv(ALERTS_PATH)

with open(CONFIG_PATH, encoding="utf-8") as f:
    thresholds = json.load(f)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Étudiants", len(students))
col2.metric("Paiements", len(payments))
col3.metric("Transactions", len(finance))
col4.metric("Alertes", len(alerts))

st.divider()
left, right = st.columns([1, 3])

severity_options = ["Tous"] + sorted(alerts["severity"].dropna().unique().tolist(), reverse=True)
type_options = ["Tous"] + sorted(alerts["alert_type"].dropna().unique().tolist())

selected_severity = left.selectbox("Criticité", severity_options)
selected_type = left.selectbox("Type d'anomalie", type_options)
search = left.text_input("Recherche libre", "")

filtered = alerts.copy()
if selected_severity != "Tous":
    filtered = filtered[filtered["severity"] == selected_severity]
if selected_type != "Tous":
    filtered = filtered[filtered["alert_type"] == selected_type]
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
    filtered = filtered[mask.any(axis=1)]

right.subheader("Alertes filtrées")
right.dataframe(filtered, use_container_width=True, hide_index=True)

chart_col1, chart_col2 = st.columns(2)
chart_col1.subheader("Répartition par criticité")
chart_col1.bar_chart(alerts["severity"].value_counts())

chart_col2.subheader("Répartition par type")
chart_col2.bar_chart(alerts["alert_type"].value_counts())

with st.expander("Seuils de détection"):
    st.json(thresholds)

with st.expander("Aperçu des données source"):
    tab1, tab2, tab3, tab4 = st.tabs(["Étudiants", "Paiements", "Notes", "Transactions"])
    tab1.dataframe(students.head(20), use_container_width=True, hide_index=True)
    tab2.dataframe(payments.head(20), use_container_width=True, hide_index=True)
    tab3.dataframe(grades.head(20), use_container_width=True, hide_index=True)
    tab4.dataframe(finance.head(20), use_container_width=True, hide_index=True)
