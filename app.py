import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ตั้งค่า ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# 🔴 1. ใส่ลิงก์ CSV จาก Google Sheet (ที่ Publish to web แล้ว)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv" 

# 🔴 2. ใส่ลิงก์หน้ากรอก Google Form
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform"

# --- ฟังก์ชัน: ข้อมูลประวัติ (Master Data) ---
def get_master_data():
    data = [
        # ข้อมูลเดิม HS-PGY, PPB, PGN, PGX, PPC (ผมใส่ให้ครบแล้ว)
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Original"},
        {"Date": "2025-12-09", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "Unknown", "Note": "Waiting"},
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...756", "Note": "Original"},
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error"},
        {"Date": "2025-09-25", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...976", "Note": "Died"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current"},
        {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "Vibration"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "Current"},
        {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Mo)"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Current"},
        {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "Died"},
        {"Date": "2025-07-06", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...10686", "Note": "Spare"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "Current (Suspect)"},
        {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Jerk)"},
        {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "Bad Spare"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "Current"},
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "Current"},
        {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty"},
        {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Failed Accel"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "Current"},
    ]
    return pd.DataFrame(data)

# --- ฟังก์ชัน: รวมข้อมูลและคำนวณวันจบ (Magic Logic) ---
@st.cache_data(ttl=10) # ลด Cache เหลือ 10 วิ เพื่อให้ข้อมูลมาเร็วขึ้น
def load_and_process_data():
    # 1. โหลด Master Data
    df_master = get_master_data()
    
    # 2. โหลด Google Sheet (ถ้ามี)
    df_sheet = pd.DataFrame()
    if "http" in SHEET_URL:
        try:
            df_sheet = pd.read_csv(SHEET_URL)
            # แก้ชื่อคอลัมน์ให้ตรงกัน (ถ้า Google Form เป็นภาษาไทย ให้แก้ฝั่งซ้าย)
            df_sheet = df_sheet.rename(columns={
                'Timestamp': 'Date', 'ประทับเวลา': 'Date',
                'Aircraft': 'Aircraft', 'Position': 'Position',
                'SN_In': 'SN_In', 'Note': 'Note'
            })
            df_sheet = df_sheet[['Date', 'Aircraft', 'Position', 'SN_In', 'Note']]
        except Exception as e:
            st.error(f"โหลด Google Sheet ไม่ได้: {e}")

    # 3. รวมร่าง
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    
    # 4. แปลงวันที่ และเรียงข้อมูล
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce') # รองรับวันเดือนปีแบบไทย
    df = df.dropna(subset=['Date']) # ลบแถวที่วันที่เสีย
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']) # เรียงตามเวลา

    # 5. คำนวณวันจบ (Finish Date) อัตโนมัติ!
    # สูตร: วันจบของตัวเก่า = วันเริ่มของตัวใหม่
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    
    # ถ้าไม่มีตัวใหม่มาแทน (เป็นตัวปัจจุบัน) ให้วันจบ = วันนี้
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df

# --- ส่วนแสดงผล ---
st.title("✈️ Fleet Maintenance Tracker (Gantt View)")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("กราฟ Timeline แบบต่อเนื่อง (อัปเดตอัตโนมัติจาก Google Form)")
with col2:
    if "http" in FORM_URL:
        st.link_button("📝 + Add New Log (Google Form)", FORM_URL)
    else:
        st.button("📝 + Add New Log", disabled=True)

try:
    df = load_and_process_data()
    
    # สร้าง Label แกน Y (เช่น HS-PGY [SEC 3])
    df['Y_Label'] = df['Aircraft'] + " [" + df['Position'] + "]"

    # สร้างกราฟ Gantt (Timeline)
    fig = px.timeline(
        df, 
        x_start="Date", 
        x_end="Finish", 
        y="Y_Label", 
        color="SN_In", # สีตาม S/N
        text="Note",   # โชว์ Note บนแท่งกราฟ
        hover_data=["Aircraft", "Position", "Date"],
        title="Component History & Swap Timeline"
    )

    # จัดความสวยงาม
    fig.update_yaxes(autorange="reversed", title="Position") # เรียงจากบนลงล่าง
    fig.update_traces(textposition='inside', insidetextanchor='middle')
    fig.update_layout(
        height=800, 
        xaxis_title="Timeline",
        showlegend=True,
        legend_title_text='Serial Number'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ตารางข้อมูลดิบ (ไว้เช็คว่าข้อมูลมาไหม)
    with st.expander("ดูข้อมูลดิบ (Data Logs)"):
        st.dataframe(df.sort_values(by='Date', ascending=False))

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
