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
            
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
            
            valid_rows = df_sheet.dropna(subset=['Date'])
            if len(df_sheet) > len(valid_rows):
                status_msg.append(f"⚠️ Warning: {len(df_sheet) - len(valid_rows)} rows dropped (Invalid Date).")
            
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
# 🔎 Sidebar Filters (ส่วนกรองข้อมูล)
# ==========================================
st.sidebar.header("🔍 Filter Options (ตัวเลือกกรอง)")

# 1. ปุ่มล้าง Cache
if st.sidebar.button("🔄 Reload Data (โหลดข้อมูลใหม่)"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()

# 2. ตัวกรองเครื่องบิน (Aircraft)
all_aircrafts = sorted(df['Aircraft'].unique())
selected_aircraft = st.sidebar.multiselect(
    "✈️ Select Aircraft (เลือกเครื่องบิน)",
    options=all_aircrafts,
    default=all_aircrafts # ค่าเริ่มต้นคือเลือกทั้งหมด
)

# 3. ตัวกรอง S/N (Serial Number)
all_sns = sorted(df[df['SN_In'].notna()]['SN_In'].unique())
selected_sn = st.sidebar.multiselect(
    "📦 Select S/N (เลือกซีเรียลนัมเบอร์)",
    options=all_sns,
    default=[] # ค่าเริ่มต้นคือไม่เลือก (แปลว่าเอาทั้งหมด)
)

# ==========================================
# 🧹 Apply Filters (ประมวลผลการกรอง)
# ==========================================
filtered_df = df.copy()

# กรองเครื่องบิน
if selected_aircraft:
    filtered_df = filtered_df[filtered_df['Aircraft'].isin(selected_aircraft)]

# กรอง S/N (ถ้ามีการเลือก)
if selected_sn:
    filtered_df = filtered_df[filtered_df['SN_In'].isin(selected_sn)]

# ==========================================
# 📊 Main Content
# ==========================================

# แสดง Status Box
with st.expander("ℹ️ System Status"):
    for msg in status_log:
        if "❌" in msg: st.error(msg)
        elif "⚠️" in msg: st.warning(msg)
        else: st.success(msg)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"แสดงข้อมูล: **{len(filtered_df)}** รายการ (จากทั้งหมด {len(df)})")
with col2:
    st.link_button("📝 + กรอกข้อมูล (Google Form)", FORM_URL)

try:
    if not filtered_df.empty:
        tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])

        with tab1:
            st.subheader("Aircraft Configuration Timeline")
            filtered_df['Y_Label'] = filtered_df['Aircraft'] + " [" + filtered_df['Position'] + "]"
            fig1 = px.timeline(
                filtered_df, x_start="Date", x_end="Finish", y="Y_Label", color="SN_In",
                text="Note", hover_data=["Aircraft", "Position", "Date", "SN_In"],
            )
            fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
            fig1.update_traces(textposition='inside', insidetextanchor='middle')
            fig1.update_layout(height=600 if len(filtered_df) < 10 else 800, xaxis_title="Timeline", showlegend=True)
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            st.subheader("Part Journey (Tracking by Serial Number)")
            df_comp = filtered_df[~filtered_df['SN_In'].isin(['Unknown', 'Check', None, 'nan'])].copy()
            
            if not df_comp.empty:
                df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
                fig2 = px.timeline(
                    df_comp, x_start="Date", x_end="Finish", y="SN_In", color="Aircraft",
                    text="Position", hover_data=["Note", "Aircraft", "Position"],
                )
                fig2.update_yaxes(categoryorder='category ascending', title="Serial Number (S/N)")
                fig2.update_traces(textposition='inside', insidetextanchor='middle')
                fig2.update_layout(height=600 if len(df_comp) < 10 else 800, xaxis_title="Timeline", showlegend=True)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("ไม่พบข้อมูล S/N ในเงื่อนไขที่เลือก")
        
        # ตารางข้อมูล (ตัดเวลาทิ้ง)
        with st.expander("ดูข้อมูลตาราง (Data Logs)", expanded=True):
            df_show = filtered_df.copy()
            df_show['Date'] = df_show['Date'].dt.strftime('%d/%m/%Y')
            df_show['Finish'] = df_show['Finish'].dt.strftime('%d/%m/%Y')
            
            cols = ['Date', 'Finish', 'Aircraft', 'Position', 'SN_In', 'Note']
            st.dataframe(df_show[cols].sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.warning("⚠️ ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาปรับตัวกรองด้านซ้ายมือ")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
