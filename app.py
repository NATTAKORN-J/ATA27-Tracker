import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components # เรียกใช้ component เพื่อฝังเว็บ
from datetime import datetime

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ==========================================
# 🔴 ลิงก์ของคุณ
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform?embedded=true"
# 💡 เคล็ดลับ: เติม ?embedded=true ต่อท้ายลิงก์ฟอร์ม เพื่อตัดขอบออกให้สวยงาม
# ==========================================

# ==========================================
# ✈️ ตั้งค่าฝูงบิน
# ==========================================
FLEET_CONFIG = {
    "Airbus A319/A320": [
        "HS-PGY", "HS-PPB", "HS-PGN", "HS-PGX", "HS-PPC", 
        "HS-PPT", "HS-PPE", "HS-PPF", "HS-PGZ", "HS-PGL"
    ],
    "ATR 72-600": [
        "HS-PZA", "HS-PZB", "HS-PZC", "HS-PZD", "HS-PZE", 
        "HS-PZF", "HS-PZG", "HS-PZH"
    ]
}

# --- 1. Master Data ---
def get_master_data():
    data = [
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Original"},
        {"Date": "2025-12-09", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "Unknown", "Note": "Waiting"},
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...756", "Note": "Original"},
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error"},
        {"Date": "2025-09-25", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...976", "Note": "Died"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "From PGN -> Vibration!"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "Current Active"},
        {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Mo)"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Current Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "From PPB -> Died"},
        {"Date": "2025-07-06", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...10686", "Note": "Spare Unit"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "Current (Suspect Wiring)"},
        {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Jerk)"},
        {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "Bad Spare"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "Current Active"},
        {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up (Reset OK)"},
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "Current Active"},
        {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty -> Shop"},
        {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Failed Accel"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "Current Active"},
    ]
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# --- 2. Load & Process ---
@st.cache_data(ttl=10)
def load_and_process_data():
    status_msg = []
    
    # Master Data
    df_master = get_master_data()
    status_msg.append(f"✅ Master Data loaded: {len(df_master)} rows")
    
    # Google Sheet
    df_sheet = pd.DataFrame()
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        if len(df_sheet.columns) >= 6:
            df_sheet = df_sheet.iloc[:, 1:6]
            df_sheet.columns = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
            
            # Cleaning
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
            
            valid_rows = df_sheet.dropna(subset=['Date'])
            df_sheet = valid_rows
            status_msg.append(f"✅ Google Sheet connected: {len(df_sheet)} rows")
        else:
            status_msg.append("⚠️ Google Sheet columns mismatch.")
    except Exception as e:
        status_msg.append(f"❌ Google Sheet Error: {str(e)}")

    # Concat
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']).reset_index(drop=True)
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df, status_msg

# --- 3. Display ---
st.title("✈️ Fleet Maintenance Tracker")

df, status_log = load_and_process_data()

# ==========================================
# 🧭 Sidebar: Fleet & Filters
# ==========================================
st.sidebar.header("🛫 Fleet Selection")
selected_fleet_type = st.sidebar.radio("Choose Fleet:", ["Airbus A319/A320", "ATR 72-600"])
fleet_aircrafts = FLEET_CONFIG.get(selected_fleet_type, [])

st.sidebar.divider()
st.sidebar.header("🔍 Filters")
available_aircrafts = sorted([ac for ac in df['Aircraft'].unique() if ac in fleet_aircrafts])
selected_aircraft = st.sidebar.multiselect(f"Select {selected_fleet_type}", options=available_aircrafts, default=available_aircrafts)

fleet_df = df[df['Aircraft'].isin(fleet_aircrafts)]
all_sns = sorted(fleet_df[fleet_df['SN_In'].notna()]['SN_In'].unique())
selected_sn = st.sidebar.multiselect("Select S/N", options=all_sns, default=[])

if st.sidebar.button("🔄 Reload Data"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 📥 ส่วนกรอกข้อมูล (EMBEDDED FORM)
# ==========================================
# สร้างกล่องกดแล้วยืดหดได้ (Expander) เพื่อซ่อนฟอร์มไม่ให้เกะกะ
with st.expander("📝 คลิกที่นี่เพื่อกรอกข้อมูลใหม่ (Record New Data)", expanded=False):
    st.markdown("กรอกข้อมูลในแบบฟอร์มด้านล่าง ข้อมูลจะถูกบันทึกเข้าระบบอัตโนมัติ")
    # ฝัง Google Form ลงในเว็บ
    components.iframe(FORM_URL, height=600, scrolling=True)

# ==========================================
# 🧹 Apply Filters & Visualization
# ==========================================
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['Aircraft'].isin(fleet_aircrafts)]
if selected_aircraft:
    filtered_df = filtered_df[filtered_df['Aircraft'].isin(selected_aircraft)]
if selected_sn:
    filtered_df = filtered_df[filtered_df['SN_In'].isin(selected_sn)]

# Layout
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"### 📂 {selected_fleet_type} Dashboard")
with col2:
    st.caption(f"Total Records: {len(filtered_df)}")

try:
    if not filtered_df.empty:
        tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])

        with tab1:
            filtered_df['Y_Label'] = filtered_df['Aircraft'] + " [" + filtered_df['Position'] + "]"
            fig1 = px.timeline(
                filtered_df, x_start="Date", x_end="Finish", y="Y_Label", color="SN_In",
                text="Note", hover_data=["Aircraft", "Position", "Date", "SN_In"],
            )
            fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
            fig1.update_traces(textposition='inside', insidetextanchor='middle')
            fig_height = max(400, len(filtered_df) * 40)
            fig1.update_layout(height=fig_height, xaxis_title="Timeline")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            df_comp = filtered_df[~filtered_df['SN_In'].isin(['Unknown', 'Check', None, 'nan'])].copy()
            if not df_comp.empty:
                df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
                fig2 = px.timeline(
                    df_comp, x_start="Date", x_end="Finish", y="SN_In", color="Aircraft",
                    text="Position", hover_data=["Note", "Aircraft", "Position"],
                )
                fig2.update_yaxes(categoryorder='category ascending', title="Serial Number")
                fig2.update_traces(textposition='inside', insidetextanchor='middle')
                fig_height = max(400, len(df_comp) * 40)
                fig2.update_layout(height=fig_height, xaxis_title="Timeline")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No Component History")

        with st.expander("ดูข้อมูลตาราง (Data Logs)", expanded=True):
            df_show = filtered_df.copy()
            df_show['Date'] = df_show['Date'].dt.strftime('%d/%m/%Y')
            df_show['Finish'] = df_show['Finish'].dt.strftime('%d/%m/%Y')
            cols = ['Date', 'Finish', 'Aircraft', 'Position', 'SN_In', 'Note']
            st.dataframe(df_show[cols].sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.info("No data found for selection.")

except Exception as e:
    st.error(f"Error: {e}")
