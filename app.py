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

# ปุ่มล้าง Cache (เผื่อข้อมูลค้าง)
if st.sidebar.button("🔄 กดปุ่มนี้ถ้าข้อมูลไม่ไม่อัปเดต (Clear Cache)"):
    st.cache_data.clear()
    st.rerun()

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
    status_msg = []
    
    # 2.1 Master Data
    df_master = get_master_data()
    status_msg.append(f"✅ Master Data loaded: {len(df_master)} rows")
    
    # 2.2 Google Sheet
    df_sheet = pd.DataFrame()
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        
        # เลือก Column ด้วย Index (1-5) เพื่อความชัวร์
        if len(df_sheet.columns) >= 6:
            df_sheet = df_sheet.iloc[:, 1:6]
            df_sheet.columns = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
            
            # 🧹 CLEANING
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            
            status_msg.append(f"✅ Google Sheet connected: Found {len(df_sheet)} rows")
        else:
            status_msg.append("⚠️ Google Sheet connected but columns mismatch.")
            
    except Exception as e:
        status_msg.append(f"❌ Google Sheet Error: {str(e)}")

    # 2.3 Concat
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    
    # 🔥 [FIX DATE PARSING] แปลงวันที่แบบยืดหยุ่นสุดๆ
    # พยายามแปลงแบบ Day First (30/06/2025) ก่อน
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # เช็คว่ามีแถวไหนหายไปไหม
    rows_before = len(df)
    df = df.dropna(subset=['Date'])
    rows_after = len(df)
    
    if rows_before > rows_after:
        status_msg.append(f"⚠️ Warning: {rows_before - rows_after} rows dropped due to invalid date format.")
    
    # 2.4 Sort & Finish Date
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']).reset_index(drop=True)
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df, status_msg

# --- 3. Display ---
st.title("✈️ Fleet Maintenance Tracker")

# โหลดข้อมูล
df, status_log = load_and_process_data()

# แสดงสถานะระบบ (Debug Box)
with st.expander("ℹ️ System Status (คลิกเพื่อดูสถานะการเชื่อมต่อ)"):
    for msg in status_log:
        if "❌" in msg: st.error(msg)
        elif "⚠️" in msg: st.warning(msg)
        else: st.success(msg)
    st.caption("ถ้า Google Sheet Connected แต่กราฟไม่ขึ้น ให้ลองกดปุ่ม Clear Cache ใน Sidebar ซ้ายมือ")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("ระบบติดตามอะไหล่ & การสลับอุปกรณ์ (Swap Tracking)")
with col2:
    st.link_button("📝 + กรอกข้อมูล (Google Form)", FORM_URL)

try:
    # สร้าง Tabs
    tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])

    # --- TAB 1 ---
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
        else:
            st.warning("No data available to plot.")

    # --- TAB 2 ---
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
    
    with st.expander("ดูข้อมูลตาราง (Data Logs)"):
        st.dataframe(df.sort_values(by=['Date'], ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
