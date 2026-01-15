import streamlit as st
import pandas as pd
import plotly.express as px

# --- ตั้งค่า ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# 🔴 ใส่ลิงก์ CSV จาก Google Sheet ตรงนี้
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv" 

# 🔴 ใส่ลิงก์หน้ากรอก Google Form ตรงนี้ (เพื่อให้กดปุ่มไปกรอกได้เลย)
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform?usp=publish-editor"

# --- 1. ข้อมูลประวัติ (Master Data) ที่เราคุยกัน ---
def get_master_data():
    data = [
        # --- HS-PGY ---
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Intermittent (SFCC Wiring)"},
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error (Rack Issue)"},
        {"Date": "2025-09-26", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...1851", "Note": "Back from Shop (Spare)"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active (Hero)"},

        # --- HS-PPB ---
        {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "From PGN -> Vibration!"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "New Part Active"},

        # --- HS-PGN ---
        {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Months)"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPC Active"},
        {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "From PPB -> Died"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "From SEC 1 (Suspect Wiring)"},

        # --- HS-PGX ---
        {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Elec Jerk)"},
        {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "From PPT -> Bad Spare"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "From PPC Active"},
        {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up Transient (Reset OK)"},

        # --- HS-PPC ---
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "New Part Active"},
        {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty -> Sent to Shop"},
        {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPE -> Failed Accel"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "From PPF (Confirmed Good)"},
    ]
    return pd.DataFrame(data)

# --- 2. ฟังก์ชันโหลดข้อมูลใหม่จาก Google Sheet ---
@st.cache_data(ttl=60)
def load_all_data():
    # 2.1 โหลด Master Data
    df_master = get_master_data()
    
    # 2.2 โหลด Google Sheet (ถ้ามีลิงก์)
    if "วางลิงก์" not in SHEET_URL:
        try:
            df_sheet = pd.read_csv(SHEET_URL)
            
            # เปลี่ยนชื่อคอลัมน์จาก Google Form ให้ตรงกับโค้ด
            # (Timestamp -> Date, และชื่ออื่นๆ ถ้าคุณตั้งเป็นภาษาไทย)
            df_sheet = df_sheet.rename(columns={
                'Timestamp': 'Date',
                'ประทับเวลา': 'Date',
                # เช็คชื่อใน Google Form ให้ตรงกับฝั่งขวา
                'Aircraft': 'Aircraft',
                'Position': 'Position',
                'SN_In': 'SN_In',
                'Note': 'Note'
            })
            
            # เลือกมาเฉพาะคอลัมน์ที่ใช้
            df_sheet = df_sheet[['Date', 'Aircraft', 'Position', 'SN_In', 'Note']]
            
            # รวมร่าง (Master + Sheet)
            df_final = pd.concat([df_master, df_sheet], ignore_index=True)
            return df_final
            
        except Exception as e:
            # ถ้าโหลด Sheet ไม่ได้ ให้คืนค่า Master Data ไปก่อน
            return df_master
    else:
        return df_master

# --- ส่วนหน้าเว็บ ---
st.title("✈️ Fleet Maintenance Dashboard")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("รวมประวัติทั้งหมด (Master Data) + ข้อมูลใหม่จาก Google Sheets")
with col2:
    if "วางลิงก์" not in FORM_URL:
        st.link_button("📝 + Add New Log", FORM_URL)
    else:
        st.button("📝 + Add New Log", disabled=True, help="ใส่ลิงก์ Google Form ในโค้ดก่อน")

try:
    df = load_all_data()
    
    # แปลงวันที่
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by="Date")
    
    # --- ส่วนแสดงผลกราฟ ---
    st.subheader("Timeline View")
    
    aircraft_list = sorted(df['Aircraft'].unique())
    selected_ac = st.multiselect("Select Aircraft:", aircraft_list, default=aircraft_list)
    
    filtered_df = df[df['Aircraft'].isin(selected_ac)].copy()
    
    if not filtered_df.empty:
        fig = px.scatter(
            filtered_df,
            x="Date",
            y="Aircraft",
            color="SN_In",
            symbol="Position",
            size_max=20,
            hover_data=["Position", "Note"],
            title="Maintenance Events Timeline",
            height=600
        )
        fig.update_traces(marker=dict(size=15, line=dict(width=2, color='DarkSlateGrey')))
        st.plotly_chart(fig, use_container_width=True)
        
        # แสดงตาราง
        st.subheader("Data Logs")
        st.dataframe(filtered_df.sort_values(by='Date', ascending=False), use_container_width=True)
        
    else:
        st.info("ไม่พบข้อมูลของเครื่องบินที่เลือก")

except Exception as e:
    st.error(f"Error: {e}")

