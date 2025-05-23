import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
DB = "database.db"
def create_connection():
    return sqlite3.connect(DB)

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            complaint TEXT,
            energy_level INTEGER,
            emotions TEXT,
            ai_plan TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_session(client, date, complaint, energy, emotions, ai_plan, notes):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (client_name, date, complaint, energy_level, emotions, ai_plan, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client, date, complaint, energy, emotions, ai_plan, notes))
    conn.commit()
    conn.close()

def fetch_sessions(client):
    conn = create_connection()
    df = pd.read_sql_query("SELECT date, complaint, energy_level, emotions, ai_plan, notes FROM sessions WHERE client_name = ?", conn, params=(client,))
    conn.close()
    return df

def export_sessions_csv(client):
    df = fetch_sessions(client)
    filename = f"{client.replace(' ', '_')}_sessies.csv"
    df.to_csv(f"/mnt/data/{filename}", index=False)
    return f"/mnt/data/{filename}"

# Simpele AI-analyse (regelgebaseerd voorbeeld)
def generate_ai_plan(complaint, energy, emotions):
    advies = []
    if energy <= 4:
        advies.append("Reiki op wortel- en zonnevlechtchakra voor energiebalans.")
    if "angst" in emotions.lower() or "stress" in emotions.lower():
        advies.append("NLP-interventie voor stressreductie en ademhalingsoefeningen.")
    if "rug" in complaint.lower():
        advies.append("Klanktherapie gericht op lage frequenties voor ontspanning.")
    if not advies:
        advies.append("Intake onvoldoende voor gericht advies. Overweeg aanvullend gesprek.")
    return "\n".join(advies)

# UI Start
create_table()
st.set_page_config(page_title="Holistische praktijk", layout="wide")
st.title("🌿 Holistische praktijk – intake, AI-analyse en sessiebeheer")

tab1, tab2 = st.tabs(["➕ Nieuwe sessie", "📂 Cliëntenhistorie + Export"])

with tab1:
    st.header("Intakeformulier")
    client_name = st.text_input("Naam cliënt")
    date = st.date_input("Datum", datetime.today())
    complaint = st.text_input("Klachtomschrijving")
    energy = st.slider("Energie (0–10)", 0, 10, 5)
    emotions = st.text_area("Emotionele gesteldheid")
    notes = st.text_area("Therapeutische notities")

    if st.button("🧠 Genereer behandelplan"):
        ai_plan = generate_ai_plan(complaint, energy, emotions)
        st.subheader("📄 Behandelvoorstel (AI):")
        st.text(ai_plan)

        if st.button("💾 Opslaan sessie"):
            if client_name:
                insert_session(client_name, date.isoformat(), complaint, energy, emotions, ai_plan, notes)
                st.success("Sessie opgeslagen.")
            else:
                st.error("Voer een naam in voor de cliënt.")

with tab2:
    st.header("Cliëntenhistorie en export")
    client_filter = st.text_input("Zoek op cliëntnaam")
    if client_filter:
        df = fetch_sessions(client_filter)
        if not df.empty:
            st.dataframe(df)
            if st.button("📤 Exporteer sessies naar CSV"):
                path = export_sessions_csv(client_filter)
                st.success("Bestand aangemaakt")
                st.markdown(f"[📁 Download CSV]({path})")
        else:
            st.info("Geen sessies gevonden voor deze cliënt.")
