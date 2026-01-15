import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ==========================================
# 🔴 ลิงก์ของคุณ (ใส่ให้เรียบร้อยแล้วครับ)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform"
# ==========================================

# --- 1. Master Data (ข้อมูลประวัติ) ---
def get_master_data():
    data = [
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Original (Intermittent)"},
        {"Date": "2025-12-09", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "Unknown", "Note": "Waiting Replacement"},
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...756", "Note": "Original (Noise)"},
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error"},
        {"Date": "2025-09-25", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...976", "Note": "Died (Reset Fail)"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "From PGN -> Vibration!"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "Current Active"},
        {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Months)"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Current Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "From PPB -> Died"},
        {"Date": "2025-07-06", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...10686", "Note": "Spare Unit"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "Current (Suspect Wiring)"},
        {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Elec Jerk)"},
        {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "Bad Spare from PPT"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "Current Active"},
        {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up Transient (Reset OK)"},
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "Current Active"},
        {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty -> Sent to Shop"},
        {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPE -> Failed Accel"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "From PPF (Confirmed Good)"},
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
        
        # เปลี่ยนชื่อคอลัมน์ (Google Form -> Code)
        df_sheet = df_sheet.rename(columns={
            'Timestamp': 'Date', 'ประทับเวลา': 'Date',
            'Aircraft': 'Aircraft', 'Position': 'Position',
            'SN_In': 'SN_In', 'Note': 'Note'
        })
        
        # ลบคอลัมน์ซ้ำ
        df_sheet = df_sheet.loc[:, ~df_sheet.columns.duplicated()]
        
        # จัดการคอลัมน์ให้ครบ
        required_cols = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
        for col in required_cols:
            if col not in df_sheet.columns:
                df_sheet[col] = None
        df_sheet = df_sheet[required_cols]
        
    except Exception as e:
        st.warning(f"Google Sheet ยังไม่พร้อม (อาจต้องรอ 5 นาทีหลังกรอกข้อมูล): {e}")

    # รวมร่าง
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    df = df.loc[:, ~df.columns.duplicated()]

    # จัดการวันที่
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # เรียงลำดับ
    df = df.sort_values(by=['Aircraft', 'Position', 'Date'])
    df = df.reset_index(drop=True)

    # คำนวณวันจบ (Finish Date)
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
    
    # สร้าง Tabs เพื่อเลือกดูกราฟ
    tab1, tab2 = st.tabs(["✈️ Aircraft View (ดูรายเครื่อง)", "📦 Component View (ดูราย S/N)"])

    # --- TAB 1: Aircraft View (แบบเดิม) ---
    with tab1:
        st.subheader("Aircraft Configuration Timeline")
        # สร้าง Y Label
        df['Y_Label'] = df['Aircraft'] + " [" + df['Position'] + "]"
        
        fig1 = px.timeline(
            df, 
            x_start="Date", 
            x_end="Finish", 
            y="Y_Label", 
            color="SN_In", # สีแบ่งตาม S/N
            text="Note",
            hover_data=["Aircraft", "Position", "Date", "SN_In"],
        )
        fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
        fig1.update_traces(textposition='inside', insidetextanchor='middle')
        fig1.update_layout(height=800, xaxis_title="Timeline", showlegend=True, legend_title_text='Serial Number')
        st.plotly_chart(fig1, use_container_width=True)

    # --- TAB 2: Component View (ของใหม่ตามคำขอ!) ---
    with tab2:
        st.subheader("Part Journey (Tracking by Serial Number)")
        st.markdown("กราฟนี้แกน Y คือ **Serial Number** จะเห็นชัดเจนว่า S/N นี้ย้ายไปเครื่องไหนบ้าง")
        
        # กรองเอาเฉพาะที่มีเลข S/N (ไม่เอา Unknown)
        df_comp = df[~df['SN_In'].isin(['Unknown', 'Check', None])].copy()
        
        # เรียง S/N ตามชื่อ
        df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
        
        fig2 = px.timeline(
            df_comp,
            x_start="Date",
            x_end="Finish",
            y="SN_In",      # แกน Y เป็น S/N
            color="Aircraft", # สีแบ่งตามเครื่องบิน (จะได้เห็นว่าย้ายไปเครื่องไหน)
            text="Position",  # ข้อความบอกตำแหน่ง
            hover_data=["Note", "Aircraft", "Position"],
        )
        fig2.update_yaxes(categoryorder='category ascending', title="Serial Number (S/N)")
        fig2.update_traces(textposition='inside', insidetextanchor='middle')
        fig2.update_layout(height=800, xaxis_title="Timeline", showlegend=True, legend_title_text='Aircraft')
        st.plotly_chart(fig2, use_container_width=True)
    
    # ตารางข้อมูลรวม
    with st.expander("ดูข้อมูลตาราง (Data Logs)"):
        st.dataframe(df.sort_values(by=['Date'], ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
    st.info("ถ้าเพิ่งกรอกข้อมูล กรุณารอประมาณ 5 นาที แล้วกด R เพื่อโหลดใหม่ครับ")
