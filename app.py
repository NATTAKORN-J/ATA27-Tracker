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

# ปุ่มล้าง Cache
if st.sidebar.button("🔄 กดปุ่มนี้ถ้าข้อมูลไม่ไม่อัปเดต (Clear Cache)"):
    st.cache_data.clear()
    st.rerun()

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
    # Master Data เป็น YYYY-MM-DD แน่นอน
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# --- 2. Load & Process ---
@st.cache_data(ttl=10)
def load_and_process_data():
    status_msg = []
    
    # 2.1 Master Data
    df_master = get_master_data()
    status_msg.append(f"✅ Master Data loaded: {len(df_master)} rows")
    
    # 2.2 Google Sheet
    df_sheet = pd.DataFrame()
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        
        # เลือก Column Index 1-5 (ข้าม Timestamp)
        if len(df_sheet.columns) >= 6:
            df_sheet = df_sheet.iloc[:, 1:6]
            df_sheet.columns = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
            
            # Cleaning
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            
            # แปลงวันที่ Google Sheet (Day First)
            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
            
            valid_rows = df_sheet.dropna(subset=['Date'])
            dropped_count = len(df_sheet) - len(valid_rows)
            
            if dropped_count > 0:
                status_msg.append(f"⚠️ Warning: {dropped_count} rows dropped (Invalid Date).")
            
            df_sheet = valid_rows
            status_msg.append(f"✅ Google Sheet connected: {len(df_sheet)} rows")
        else:
            status_msg.append("⚠️ Google Sheet columns mismatch.")
            
    except Exception as e:
        status_msg.append(f"❌ Google Sheet Error: {str(e)}")

    # 2.3 Concat
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    
    # 2.4 Sort & Finish Date
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']).reset_index(drop=True)
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    # ใช้วันปัจจุบันเป็นวันจบของตัวล่าสุด
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df, status_msg

# --- 3. Display ---
st.title("✈️ Fleet Maintenance Tracker")

df, status_log = load_and_process_data()

with st.expander("ℹ️ System Status"):
    for msg in status_log:
        if "❌" in msg: st.error(msg)
        elif "⚠️" in msg: st.warning(msg)
        else: st.success(msg)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("ระบบติดตามอะไหล่ & การสลับอุปกรณ์ (Swap Tracking)")
with col2:
    st.link_button("📝 + กรอกข้อมูล (Google Form)", FORM_URL)

try:
    tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])

    with tab1:
        st.subheader("Aircraft Configuration Timeline")
        if not df.empty:
            df['Y_Label'] = df['Aircraft'] + " [" + df['Position'] + "]"
            fig1 = px.timeline(
                df, x_start="Date", x_end="Finish", y="Y_Label", color="SN_In",
                text="Note", hover_data=["Aircraft", "Position", "Date", "SN_In"],
            )
            fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
            fig1.update_traces(textposition='inside', insidetextanchor='middle')
            fig1.update_layout(height=800, xaxis_title="Timeline", showlegend=True)
            st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("Part Journey (Tracking by Serial Number)")
        if not df.empty:
            df_comp = df[~df['SN_In'].isin(['Unknown', 'Check', None, 'nan'])].copy()
            df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
            fig2 = px.timeline(
                df_comp, x_start="Date", x_end="Finish", y="SN_In", color="Aircraft",
                text="Position", hover_data=["Note", "Aircraft", "Position"],
            )
            fig2.update_yaxes(categoryorder='category ascending', title="Serial Number (S/N)")
            fig2.update_traces(textposition='inside', insidetextanchor='middle')
            fig2.update_layout(height=800, xaxis_title="Timeline", showlegend=True)
            st.plotly_chart(fig2, use_container_width=True)
    
    # 🔥 [ส่วนที่แก้ไข] ตารางข้อมูล (ตัดเวลาทิ้ง)
    with st.expander("ดูข้อมูลตาราง (Data Logs)"):
        df_show = df.copy()
        # แปลงเป็น String แบบ วัน/เดือน/ปี
        df_show['Date'] = df_show['Date'].dt.strftime('%d/%m/%Y')
        df_show['Finish'] = df_show['Finish'].dt.strftime('%d/%m/%Y')
        
        # เลือกคอลัมน์ที่จะโชว์
        cols = ['Date', 'Finish', 'Aircraft', 'Position', 'SN_In', 'Note']
        st.dataframe(df_show[cols].sort_values(by='Date', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
