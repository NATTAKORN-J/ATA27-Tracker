import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ==========================================
# 🔴 ลิงก์ของคุณ (Google Sheet & Form)
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform?embedded=true"

# ==========================================
# ✈️ ตั้งค่าฝูงบิน (FLEET CONFIG)
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

# --- 2. Load & Process ---
@st.cache_data(ttl=10)
def load_and_process_data():
    status_msg = []
    
    # สร้าง DataFrame เปล่าๆ มารอไว้ก่อน (กัน Error ถ้าโหลด Sheet ไม่ได้)
    df = pd.DataFrame(columns=['Date', 'Aircraft', 'Position', 'SN_In', 'Note', 'WO', 'Request', 'Action'])
    
    # โหลดข้อมูลจาก Google Sheet
    try:
        df_sheet = pd.read_csv(SHEET_URL)
        
        # ตรวจสอบว่ามีข้อมูลอย่างน้อย 6 คอลัมน์ไหม (Timestamp, Date, Aircraft, Position, SN_In, Note)
        if len(df_sheet.columns) >= 6:
            # ดึง 5 คอลัมน์หลัก (ข้าม Timestamp คอลัมน์แรก)
            main_data = df_sheet.iloc[:, 1:6].copy()
            main_data.columns = ['Date', 'Aircraft', 'Position', 'SN_In', 'Note']
            
            # ดึง 3 คอลัมน์เสริม (WO, Request, Action) ถ้ามี
            if len(df_sheet.columns) >= 9:
                extra_data = df_sheet.iloc[:, 6:9].copy()
                extra_data.columns = ['WO', 'Request', 'Action']
                df_sheet = pd.concat([main_data, extra_data], axis=1)
            else:
                # ถ้าใน Sheet ยังไม่มีคอลัมน์พวกนี้ ให้สร้างเป็นค่าว่าง
                df_sheet = main_data
                df_sheet['WO'] = "-"
                df_sheet['Request'] = "-"
                df_sheet['Action'] = "-"
            
            # ทำความสะอาดข้อมูล (Cleaning)
            # แปลงเป็นตัวพิมพ์ใหญ่ และลบช่องว่างหัวท้าย
            df_sheet['Position'] = df_sheet['Position'].astype(str).str.upper().str.strip().str.replace('#', ' ', regex=False)
            df_sheet['Aircraft'] = df_sheet['Aircraft'].astype(str).str.upper().str.strip().str.replace('“', '', regex=False).str.replace('"', '', regex=False)
            
            # แปลงวันที่ (รองรับ Day First)
            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
            
            # ลบแถวที่วันที่เสีย (NaT)
            valid_rows = df_sheet.dropna(subset=['Date'])
            
            status_msg.append(f"✅ Google Sheet connected: {len(valid_rows)} rows found")
            df = valid_rows
            
        else:
            status_msg.append("⚠️ Google Sheet columns mismatch (Need at least 6 columns).")
            
    except Exception as e:
        status_msg.append(f"❌ Google Sheet Error: {str(e)}")

    # ถ้าไม่มีข้อมูลเลย ให้จบการทำงานตรงนี้
    if df.empty:
        return df, status_msg

    # เติมค่าว่างด้วยขีด "-" เพื่อความสวยงาม
    df = df.fillna("-")
    
    # เรียงลำดับข้อมูล: เครื่อง -> ตำแหน่ง -> วันที่
    df = df.sort_values(by=['Aircraft', 'Position', 'Date']).reset_index(drop=True)
    
    # คำนวณวันจบ (Finish Date) เพื่อลากเส้นกราฟ
    # Logic: วันจบของรายการนี้ = วันเริ่มของรายการถัดไป (ในตำแหน่งเดียวกัน)
    df['Finish'] = df.groupby(['Aircraft', 'Position'])['Date'].shift(-1)
    
    # รายการล่าสุด (ที่ยังไม่มีรายการถัดไป) ให้ลากยาวถึง "วันนี้"
    df['Finish'] = df['Finish'].fillna(pd.Timestamp.now())
    
    return df, status_msg

# --- 3. Display ---
st.title("✈️ Fleet Maintenance Tracker")

df, status_log = load_and_process_data()

# ==========================================
# 🧭 SIDEBAR FILTERS (ตัวกรองด้านซ้าย)
# ==========================================
st.sidebar.header("🛫 Fleet Selection")
selected_fleet_type = st.sidebar.radio("Choose Fleet:", ["Airbus A319/A320", "ATR 72-600"])
fleet_aircrafts = FLEET_CONFIG.get(selected_fleet_type, [])

st.sidebar.divider()
st.sidebar.header("🔍 Filters")

if df.empty:
    st.sidebar.warning("ไม่พบข้อมูลในระบบ (กรุณากรอกข้อมูลผ่าน Form)")
    available_aircrafts = []
else:
    # 1. Filter Aircraft (เลือกเครื่องบิน)
    available_aircrafts = sorted([ac for ac in df['Aircraft'].unique() if ac in fleet_aircrafts])
    if not available_aircrafts:
        st.sidebar.warning("ไม่พบข้อมูลเครื่องบินในฝูงนี้")
        selected_aircraft = []
    else:
        selected_aircraft = st.sidebar.multiselect(
            f"Select {selected_fleet_type}", 
            options=available_aircrafts, 
            default=available_aircrafts
        )

    # กรองข้อมูลเบื้องต้นตาม Fleet เพื่อไปสร้างตัวเลือกถัดไป
    fleet_df = df[df['Aircraft'].isin(fleet_aircrafts)]

    # 2. Filter Position (เลือกตำแหน่ง Component)
    all_positions = sorted(fleet_df['Position'].unique())
    selected_position = st.sidebar.multiselect(
        "Select Component/Position", 
        options=all_positions, 
        default=[] # ค่าเริ่มต้นเอาทั้งหมด
    )

    # 3. Filter S/N (เลือกซีเรียลนัมเบอร์)
    # กรอง S/N ตามตำแหน่งที่เลือกไว้
    if selected_position:
        sn_source_df = fleet_df[fleet_df['Position'].isin(selected_position)]
    else:
        sn_source_df = fleet_df

    all_sns = sorted(sn_source_df[sn_source_df['SN_In'] != "-"]['SN_In'].unique()) 
    selected_sn = st.sidebar.multiselect("Select S/N", options=all_sns, default=[])

# ปุ่มโหลดใหม่
if st.sidebar.button("🔄 Reload Data"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 📊 MAIN CONTENT
# ==========================================

# ฝัง Google Form
with st.expander("📝 คลิกที่นี่เพื่อกรอกข้อมูลใหม่ (WO, Request, Action)", expanded=False):
    st.markdown("ข้อมูลจะถูกบันทึกลง Google Sheet และแสดงผลในกราฟทันที (กด Reload หากไม่ขึ้น)")
    components.iframe(FORM_URL, height=600, scrolling=True)

# ตรวจสอบว่ามีข้อมูลไหม
if df.empty:
    st.info("👋 ยินดีต้อนรับ! ระบบยังไม่มีข้อมูล กรุณากรอกข้อมูลแรกผ่าน Google Form ด้านบนครับ")
else:
    # ประมวลผลการกรอง (Filter Logic)
    filtered_df = df.copy()

    # กรอง 1: ฝูงบิน
    filtered_df = filtered_df[filtered_df['Aircraft'].isin(fleet_aircrafts)]

    # กรอง 2: ทะเบียนเครื่อง
    if 'selected_aircraft' in locals() and selected_aircraft:
        filtered_df = filtered_df[filtered_df['Aircraft'].isin(selected_aircraft)]

    # กรอง 3: ตำแหน่ง (Position)
    if 'selected_position' in locals() and selected_position:
        filtered_df = filtered_df[filtered_df['Position'].isin(selected_position)]

    # กรอง 4: S/N
    if 'selected_sn' in locals() and selected_sn:
        filtered_df = filtered_df[filtered_df['SN_In'].isin(selected_sn)]

    # แสดงผล Dashboard
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📂 {selected_fleet_type} Dashboard")
    with col2:
        st.caption(f"Total: {len(filtered_df)} records")

    try:
        if not filtered_df.empty:
            tab1, tab2 = st.tabs(["✈️ Aircraft View", "📦 Component View"])
            
            # ข้อมูลที่จะโชว์ตอนเอาเมาส์ชี้
            hover_cols = ["Aircraft", "Position", "Date", "SN_In", "WO", "Request", "Action"]

            with tab1:
                filtered_df['Y_Label'] = filtered_df['Aircraft'] + " [" + filtered_df['Position'] + "]"
                
                fig1 = px.timeline(
                    filtered_df, x_start="Date", x_end="Finish", y="Y_Label", 
                    color="SN_In", 
                    text="SN_In", 
                    hover_data=hover_cols,
                    title="Aircraft Configuration Timeline"
                )
                fig1.update_yaxes(autorange="reversed", title="Aircraft Position")
                fig1.update_traces(textposition='inside', insidetextanchor='middle')
                
                # ปรับความสูงกราฟอัตโนมัติ
                fig_height = max(400, len(filtered_df) * 40)
                fig1.update_layout(height=fig_height, xaxis_title="Timeline")
                
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                # กรอง S/N ที่เป็นค่าว่างทิ้งไปก่อนพลอตกราฟนี้
                df_comp = filtered_df[~filtered_df['SN_In'].isin(['-', 'nan', 'None', 'Unknown'])].copy()
                
                if not df_comp.empty:
                    df_comp = df_comp.sort_values(by=['SN_In', 'Date'])
                    fig2 = px.timeline(
                        df_comp, x_start="Date", x_end="Finish", y="SN_In", 
                        color="Aircraft",
                        text="Position", 
                        hover_data=hover_cols,
                    )
                    fig2.update_yaxes(categoryorder='category ascending', title="Serial Number")
                    fig2.update_traces(textposition='inside', insidetextanchor='middle')
                    
                    fig_height = max(400, len(df_comp) * 40)
                    fig2.update_layout(height=fig_height, xaxis_title="Timeline")
                    
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("ไม่พบประวัติ S/N")

            # ตารางข้อมูลละเอียด
            with st.expander("ดูข้อมูลตารางแบบละเอียด (Detailed Logs)", expanded=True):
                df_show = filtered_df.copy()
                # แปลงวันที่ให้ดูง่าย
                df_show['Date'] = df_show['Date'].dt.strftime('%d/%m/%Y')
                # ถ้า Finish เป็นวันนี้ (Current) ให้โชว์คำว่า "Current" แทนวันที่
                current_date = pd.Timestamp.now().strftime('%d/%m/%Y')
                df_show['Finish'] = df_show['Finish'].dt.strftime('%d/%m/%Y')
                
                cols = ['Date', 'Aircraft', 'Position', 'SN_In', 'WO', 'Request', 'Action', 'Note']
                st.dataframe(df_show[cols].sort_values(by='Date', ascending=False), use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลตามเงื่อนไข (ลองปรับตัวกรองด้านซ้าย)")

    except Exception as e:
        st.error(f"Error: {e}")
