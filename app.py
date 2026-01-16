import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import re # เพิ่มตัวช่วยตัดคำ
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform?embedded=true"

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

# --- ฟังก์ชันตัด S/N ให้เหลือ 4 ตัวท้าย (ตามคำขอ) ---
def clean_sn_last4(val):
    val_str = str(val).strip()
    
    # ถ้าเป็นค่าว่าง หรือขีด ให้คงเดิมไว้
    if val_str in ['-', 'nan', 'None', '', 'Unknown']:
        return val_str
    
    # ถ้ามีคำว่า Shop ให้โชว์ว่า SHOP
    if 'shop' in val_str.lower():
        return "SHOP"

    # ลองดึงเฉพาะตัวเลขออกมา
    digits = re.findall(r'\d+', val_str)
    if digits:
        # เอาตัวเลขทั้งหมดมาต่อกัน แล้วตัดเอา 4 ตัวท้าย
        full_num = "".join(digits)
        return full_num[-4:]
    else:
        # ถ้าไม่มีตัวเลขเลย ให้เอา 4 ตัวอักษรท้าย
        return val_str[-4:]

# --- 2. Master Data ---
def get_master_data():
    data = [
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Original", "WO": "-", "Request": "-", "Action": "Original Install"},
        {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active", "WO": "WO-25-099", "Request": "SEC 3 Fault Message", "Action": "Replaced SEC 3"},
        {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "Current Active", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Current Active", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "Current (Suspect)", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "Current Active", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up (Reset OK)", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "Current Active", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "Current Active", "WO": "-", "Request": "-", "Action": "-"},
        # เพิ่มข้อมูลให้ครบตามที่แจ้งว่าหายไป (ตัวอย่าง)
        {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...756", "Note": "Original", "WO": "-", "Request": "-", "Action": "-"},
        {"Date": "2025-09-25", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...976", "Note": "Died", "WO": "-", "Request": "-", "Action": "-"},
    ]
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# --- 3. Load & Process ---
@st.cache_data(ttl=10)
def load_and_process_data():
    status_msg = []
    
    # 3.1 Master Data
    df_master = get_master_data()
    status_msg.append(f"✅ Master Data loaded: {len(df_master)} rows")
    
    # 3.2 Google Sheet
    df_sheet = pd.DataFrame()
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        std_cols = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note', 'WO', 'Request', 'Action']
        
        if len(df_sheet.columns) >= 6:
            main_data = df_sheet.iloc[:, 1:6].copy()
            main_data.columns = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
            
            if len(df_sheet.columns) >= 9:
                extra_data = df_sheet.iloc[:, 6:9].copy()
                extra_data.columns = ['WO', 'Request', 'Action']
                df_sheet = pd.concat([main_data, extra_data], axis=1)
            else:
                df_sheet = main_data
                df_sheet['WO'] = "-"
                df_sheet['Request'] = "-"
                df_sheet['Action'] = "-"
            
            # Cleaning Data
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            
            # Date Parsing
            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
            valid_rows = df_sheet.dropna(subset=['Date'])
            df_sheet = valid_rows
            status_msg.append(f"✅ Google Sheet connected: {len(df_sheet)} rows")
        else:
            status_msg.append("⚠️ Google Sheet columns mismatch.")
    except Exception as e:
        status_msg.append(f"❌ Google Sheet Error: {str(e)}")

    # 3.3 Concat
    df = pd.concat([df_master, df_sheet], ignore_index=True)
    df = df.fillna("-")
    
    # 🔥 Apply S/N Cleaning (เหลือ 4 ตัวท้าย)
    # ทำก่อน sort จะได้เรียงลำดับถูก
    df['SN_Show'] = df['SN_In'].apply(clean_sn_last4)
    
    # Sort
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']).reset_index(drop=True)
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df, status_msg

# --- 4. Display ---
st.title("✈️ Fleet Maintenance Tracker")

df, status_log = load_and_process_data()

# Sidebar
st.sidebar.header("🛫 Fleet Selection")
selected_fleet_type = st.sidebar.radio("Choose Fleet:", ["Airbus A319/A320", "ATR 72-600"])
fleet_aircrafts = FLEET_CONFIG.get(selected_fleet_type, [])

st.sidebar.divider()
st.sidebar.header("🔍 Filters")
available_aircrafts = sorted([ac for ac in df['Aircraft'].unique() if ac in fleet_aircrafts])

if not available_aircrafts:
    selected_aircraft = []
else:
    selected_aircraft = st.sidebar.multiselect(f"Select {selected_fleet_type}", options=available_aircrafts, default=available_aircrafts)

# Filter for S/N list
fleet_df = df[df['Aircraft'].isin(fleet_aircrafts)]
# เรียง S/N จากตัวที่ clean แล้ว (SN_Show) เพื่อความสวยงาม
all_sns = sorted(fleet_df[fleet_df['SN_Show'] != "-"]['SN_Show'].unique()) 
selected_sn = st.sidebar.multiselect("Select S/N (4-Digits)", options=all_sns, default=[])

if st.sidebar.button("🔄 Reload Data"):
    st.cache_data.clear()
    st.rerun()

# Embedded Form
with st.expander("📝 คลิกที่นี่เพื่อกรอกข้อมูลใหม่ (WO, Request, Action)", expanded=False):
    components.iframe(FORM_URL, height=600, scrolling=True)

# Filter Processing
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['Aircraft'].isin(fleet_aircrafts)]
if selected_aircraft:
    filtered_df = filtered_df[filtered_df['Aircraft'].isin(selected_aircraft)]
if selected_sn:
    filtered_df = filtered_df[filtered_df['SN_Show'].isin(selected_sn)]

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"### 📂 {selected_fleet_type} Dashboard")
with col2:
    st.caption(f"Total: {len(filtered_df)} records")

try:
    if not filtered_df.empty:
        tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])
        hover_cols = ["Aircraft", "Position", "Date", "SN_Show", "WO", "Request", "Action"]

        with tab1:
            # ใช้ SN_Show (4 ตัวท้าย) เป็นสีและ label
            filtered_df['Y_Label'] = filtered_df['Aircraft'] + " [" + filtered_df['Position'] + "]"
            fig1 = px.timeline(
                filtered_df, x_start="Date", x_end="Finish", y="Y_Label", 
                color="SN_Show", # ใช้ S/N 4 ตัวท้ายเป็นตัวแบ่งสี
                text="SN_Show",  # โชว์เลข 4 ตัวท้ายในกราฟ
                hover_data=hover_cols,
                title="Timeline (Color by S/N Last 4 Digits)"
            )
            fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
            fig1.update_traces(textposition='inside', insidetextanchor='middle')
            fig_height = max(400, len(filtered_df) * 40)
            fig1.update_layout(height=fig_height, xaxis_title="Timeline")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            # กรองเอาเฉพาะที่มีเลข S/N (รวมถึง Shop ด้วยถ้าอยากเห็น)
            df_comp = filtered_df[~filtered_df['SN_Show'].isin(['-', 'nan', 'None', 'Unknown'])].copy()
            
            if not df_comp.empty:
                df_comp = df_comp.sort_values(by=['SN_Show', 'Date'])
                fig2 = px.timeline(
                    df_comp, x_start="Date", x_end="Finish", y="SN_Show", # แกน Y เป็น S/N 4 ตัวท้าย
                    color="Aircraft",
                    text="Position", 
                    hover_data=hover_cols,
                )
                fig2.update_yaxes(categoryorder='category ascending', title="S/N (Last 4 Digits)")
                fig2.update_traces(textposition='inside', insidetextanchor='middle')
                fig_height = max(400, len(df_comp) * 40)
                fig2.update_layout(height=fig_height, xaxis_title="Timeline")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("ไม่พบประวัติ S/N")

        with st.expander("ดูข้อมูลตารางแบบละเอียด (Detailed Logs)", expanded=True):
            df_show = filtered_df.copy()
            df_show['Date'] = df_show['Date'].dt.strftime('%d/%m/%Y')
            df_show['Finish'] = df_show['Finish'].dt.strftime('%d/%m/%Y')
            # โชว์ SN_Show (4ตัว) คู่กับ SN_In (ตัวเต็ม) เผื่ออยากเช็ค
            cols = ['Date', 'Aircraft', 'Position', 'SN_Show', 'SN_In', 'WO', 'Request', 'Action']
            st.dataframe(df_show[cols].sort_values(by='Date', ascending=False), use_container_width=True)
    else:
        st.info("ไม่พบข้อมูลตามเงื่อนไข")

except Exception as e:
    st.error(f"Error: {e}")
