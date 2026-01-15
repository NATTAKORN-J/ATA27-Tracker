import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ==========================================
# 🔴 ลิงก์ของคุณ
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform"
# ==========================================

# --- 1. Master Data (ข้อมูลประวัติ) ---
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
    return pd.DataFrame(data)

# --- 2. Load & Process ---
@st.cache_data(ttl=10)
def load_and_process_data():
    df_master = get_master_data()
    
    # โหลด Google Sheet
    df_sheet = pd.DataFrame()
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        
        # 🔥 [FIXED] ไม่เปลี่ยนชื่อ 'ประทับเวลา' เป็น Date แล้ว (โยนทิ้งไปเลย)
        # เราจะใช้คอลัมน์ที่ชื่อ "Date" (ที่มีอยู่แล้วใน Sheet ของคุณ) โดยตรง
        
        # ลบคอลัมน์ที่ไม่จำเป็น (ประทับเวลา) ออกไป เพื่อไม่ให้สับสน
        cols_to_drop = ['Timestamp', 'ประทับเวลา']
        df_sheet = df_sheet.drop(columns=[c for c in cols_to_drop if c in df_sheet.columns], errors='ignore')
        
        # เปลี่ยนชื่อคอลัมน์อื่นๆ (เผื่อไว้) แต่ Date ไม่ต้องเปลี่ยนเพราะชื่อตรงอยู่แล้ว
        df_sheet = df_sheet.rename(columns={
            # 'Date': 'Date', <-- ไม่ต้องเปลี่ยน เพราะมันชื่อ Date อยู่แล้ว
            'Aircraft': 'Aircraft', 
            'Position': 'Position', 
            'SN_In': 'SN_In', 
            'Note': 'Note'
        })
        
        # จัดการคอลัมน์ให้ครบ
        required_cols = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
        for col in required_cols:
            if col not in df_sheet.columns:
                df_sheet[col] = None
        df_sheet = df_sheet[required_cols]

        # 🧹 CLEANING DATA
        df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip()
        df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip()
        
        # แก้เครื่องหมาย # และฟันหนู
        df_sheet['Position'] = df_sheet['Position'].str.replace('#', ' ', regex=False)
        df_sheet['Aircraft'] = df_sheet['Aircraft'].str.replace('“', '', regex=False).str.replace('"', '', regex=False)
        
    except Exception as e:
        st.warning(f"Google Sheet Warning: {e}")

    # รวมร่าง
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    
    # จัดการวันที่ (รองรับทั้งแบบ 30/6/2025 และ 2025-06-30)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # เรียงลำดับและรีเซ็ต index
    df = df.sort_values(by=['Aircraft', 'Position', 'Date'])
    df = df.reset_index(drop=True)

    # คำนวณวันจบ
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df

# --- 3. Display ---
st.title("✈️ Fleet Maintenance Tracker")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("ระบบติดตามอะไหล่ & การสลับอุปกรณ์ (Swap Tracking)")
with col2:
    st.link_button("📝 + กรอกข้อมูล (Google Form)", FORM_URL)

try:
    df = load_and_process_data()
    
    # สร้าง Tabs
    tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])

    # --- TAB 1 ---
    with tab1:
        st.subheader("Aircraft Configuration Timeline")
        df['Y_Label'] = df['Aircraft'] + " [" + df['Position'] + "]"
        
        fig1 = px.timeline(
            df, 
            x_start="Date", 
            x_end="Finish", 
            y="Y_Label", 
            color="SN_In",
            text="Note",
            hover_data=["Aircraft", "Position", "Date", "SN_In"],
        )
        fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
        fig1.update_traces(textposition='inside', insidetextanchor='middle')
        fig1.update_layout(height=800, xaxis_title="Timeline", showlegend=True)
        st.plotly_chart(fig1, use_container_width=True)

    # --- TAB 2 ---
    with tab2:
        st.subheader("Part Journey (Tracking by Serial Number)")
        df_comp = df[~df['SN_In'].isin(['Unknown', 'Check', None, 'nan'])].copy()
        df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
        
        fig2 = px.timeline(
            df_comp,
            x_start="Date",
            x_end="Finish",
            y="SN_In",
            color="Aircraft",
            text="Position",
            hover_data=["Note", "Aircraft", "Position"],
        )
        fig2.update_yaxes(categoryorder='category ascending', title="Serial Number (S/N)")
        fig2.update_traces(textposition='inside', insidetextanchor='middle')
        fig2.update_layout(height=800, xaxis_title="Timeline", showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)
    
    with st.expander("ดูข้อมูลตาราง (Data Logs)"):
        st.dataframe(df.sort_values(by=['Date'], ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
