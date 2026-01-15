import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ==========================================
# 🔴 ส่วนที่คุณต้องแก้ไข (ใส่ลิงก์ของคุณ)
# ==========================================
# 1. ลิงก์ CSV จาก Google Sheet (File -> Share -> Publish to web -> CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv" 

# 2. ลิงก์หน้ากรอก Google Form
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform"
# ==========================================

# --- 1. ข้อมูลประวัติ (Master Data) ---
def get_master_data():
    data = [
        # --- HS-PGY ---
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Original (Intermittent)"},
        {"Date": "2025-12-09", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "Unknown", "Note": "Waiting Replacement"},
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...756", "Note": "Original (Noise)"},
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error"},
        {"Date": "2025-09-25", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...976", "Note": "Died (Reset Fail)"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active"},
        
        # --- HS-PPB ---
        {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "From PGN -> Vibration!"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "Current Active"},

        # --- HS-PGN ---
        {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Months)"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Current Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "From PPB -> Died"},
        {"Date": "2025-07-06", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...10686", "Note": "Spare Unit"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "Current (Suspect Wiring)"},

        # --- HS-PGX ---
        {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Elec Jerk)"},
        {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "Bad Spare from PPT"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "Current Active"},
        {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up Transient (Reset OK)"},

        # --- HS-PPC ---
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "Current Active"},
        {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty -> Sent to Shop"},
        {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPE -> Failed Accel"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "From PPF (Confirmed Good)"},
    ]
    return pd.DataFrame(data)

# --- 2. ฟังก์ชันโหลดและประมวลผล (Magic Logic) ---
@st.cache_data(ttl=10)
def load_and_process_data():
    # 2.1 โหลด Master Data
    df_master = get_master_data()
    
    # 2.2 โหลด Google Sheet (ถ้ามี)
    df_sheet = pd.DataFrame()
    if "http" in SHEET_URL:
        try:
            df_sheet = pd.read_csv(SHEET_URL)
            # เปลี่ยนชื่อคอลัมน์จาก Google Form ให้ตรงกับโค้ด
            df_sheet = df_sheet.rename(columns={
                'Timestamp': 'Date', 'ประทับเวลา': 'Date',
                'Aircraft': 'Aircraft', 'Position': 'Position',
                'SN_In': 'SN_In', 'Note': 'Note'
            })
            # เลือกเฉพาะคอลัมน์ที่จำเป็น (กัน Error)
            valid_cols = [c for c in ['Date', 'Aircraft', 'Position', 'SN_In', 'Note'] if c in df_sheet.columns]
            df_sheet = df_sheet[valid_cols]
        except Exception as e:
            st.error(f"โหลด Google Sheet ไม่ได้ (โชว์เฉพาะข้อมูลเก่า): {e}")

    # 2.3 รวมร่าง (Concat)
    # ignore_index=True สำคัญมาก! ป้องกันเลขบรรทัดซ้ำ
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    
    # 2.4 จัดการวันที่
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # 2.5 เรียงลำดับข้อมูล
    df = df.sort_values(by=['Aircraft', 'Position', 'Date'])
    
    # 🔥 [FIX] รีเซ็ต Index ใหม่ทั้งหมด เพื่อแก้ Error "Reindexing only valid..."
    df = df.reset_index(drop=True)

    # 2.6 คำนวณวันจบ (Finish Date) อัตโนมัติ
    # วันจบของตัวเก่า = วันเริ่มของตัวใหม่
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    
    # ถ้าไม่มีตัวใหม่มาแทน (เป็นตัวปัจจุบัน) ให้วันจบ = วันนี้
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df

# --- 3. ส่วนแสดงผลหน้าเว็บ ---
st.title("✈️ Fleet Maintenance Tracker (Gantt Chart)")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("ติดตามประวัติการเปลี่ยนอะไหล่ (Timeline ต่อเนื่อง)")
with col2:
    if "http" in FORM_URL:
        st.link_button("📝 + กรอกข้อมูลใหม่ (Google Form)", FORM_URL)
    else:
        st.button("📝 + กรอกข้อมูลใหม่", disabled=True, help="ใส่ลิงก์ Google Form ในโค้ดก่อน")

try:
    df = load_and_process_data()
    
    # สร้าง Label แกน Y (เช่น HS-PGY [SEC 3])
    df['Y_Label'] = df['Aircraft'] + " [" + df['Position'] + "]"

    # สร้างกราฟ Timeline (Gantt)
    fig = px.timeline(
        df, 
        x_start="Date", 
        x_end="Finish", 
        y="Y_Label", 
        color="SN_In",   # สีแยกตาม S/N
        text="Note",     # ข้อความบนแท่งกราฟ
        hover_data=["Aircraft", "Position", "Date", "SN_In"],
        title="Component History & Swap Timeline"
    )

    # จัดความสวยงาม
    fig.update_yaxes(autorange="reversed", title="Aircraft Position")
    fig.update_traces(textposition='inside', insidetextanchor='middle')
    fig.update_layout(
        height=800, 
        xaxis_title="Timeline (Date)",
        showlegend=True,
        legend_title_text='Serial Number'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ส่วนดูข้อมูลดิบ
    with st.expander("ดูข้อมูลตาราง (Data Logs)"):
        st.dataframe(df.sort_values(by=['Aircraft', 'Date'], ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
    st.info("คำแนะนำ: ลองเช็คลิงก์ CSV หรือลองกดปุ่ม R (Rerun) เพื่อโหลดใหม่")
