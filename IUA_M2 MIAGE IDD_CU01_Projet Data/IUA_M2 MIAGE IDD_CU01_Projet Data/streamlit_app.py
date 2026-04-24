from src.app_streamlit import *
import streamlit as st
import pandas as pd

st.sidebar.title(" Dashboard anomalies")
page = st.sidebar.selectbox(
    "Navigation",
    ["Accueil", "Anomalies", "Statistiques"]
)

# Charger les données
df = pd.read_csv("data/alerts_output.csv")
# Titre
st.title(" Dashboard des anomalies")

# Charger les données
df = pd.read_csv("data/alerts_output.csv")


if page == "Accueil":
    st.title(" Accueil")
    st.write("Bienvenue dans le dashboard des anomalies")

elif page == "Anomalies":
    st.title(" Liste des anomalies")
    st.dataframe(df)

elif page == "Statistiques":
    st.title(" Statistiques")

    st.metric("Total anomalies", len(df))
    st.metric("Critiques", len(df[df["severity"]=="CRITICAL"]))

    st.bar_chart(df["severity"].value_counts())

# Afficher données
st.subheader(" Liste des anomalies")
st.dataframe(df)

# KPI
st.subheader(" Indicateurs")
st.metric("Total anomalies", len(df))

if "severity" in df.columns:
    st.metric("Critiques", len(df[df["severity"] == "CRITICAL"]))

# Graphique
if "severity" in df.columns:
    st.subheader(" Répartition des anomalies")
    st.bar_chart(df["severity"].value_counts())