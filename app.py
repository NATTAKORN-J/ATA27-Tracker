import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Aircraft Part Tracker", layout="wide")

# ชื่อไฟล์ฐานข้อมูล
FILE_PATH = 'maintenance_log.csv'

# --- 1. ฟังก์ชันจัดการข้อมูล ---
def load_data():
    if not os.path.exists(FILE_PATH):
        # สร้างข้อมูลตัวอย่างถ้ายังไม่มีไฟล์
        data = [
            {"Date": "2025-01-01", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "Original"},
            {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Installation"},
            {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "Replacement"},
        ]
        df = pd.DataFrame(data)
        df.to_csv(FILE_PATH, index=False)
    return pd.read_csv(FILE_PATH)

def save_data(new_entry):
    df = load_data()
    new_df = pd.DataFrame([new_entry])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(FILE_PATH, index=False)
    return df

df = load_data()

# --- 2. ส่วนหน้าเว็บ (Sidebar) ---
st.sidebar.title("✈️ Fleet Maintenance")
menu = st.sidebar.radio("เลือกเมนู", ["Dashboard (ดูกราฟ)", "Data Entry (กรอกข้อมูล)", "View Data (ดูตาราง)"])

# --- 3. หน้า Dashboard ---
if menu == "Dashboard (ดูกราฟ)":
    st.title("📊 Aircraft Component Timeline")
    st.info("กราฟแสดงประวัติการติดตั้งอะไหล่ (แยกตาม S/N)")
    
    # ตัวเลือกกรองเครื่องบิน
    aircraft_list = sorted(df['Aircraft'].unique())
    selected_ac = st.selectbox("เลือกเครื่องบิน:", aircraft_list)
    
    # กรองข้อมูล
    filtered_df = df[df['Aircraft'] == selected_ac].copy()
    
    # สร้างกราฟ Timeline
    if not filtered_df.empty:
        # แปลงวันที่ให้เป็น Format ที่กราฟเข้าใจ
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
        
        fig = px.scatter(
            filtered_df,
            x="Date",
            y="Position",
            color="SN_In", # สีตาม S/N
            size_max=20,
            hover_data=["Note"],
            title=f"Component History: {selected_ac}"
        )
        fig.update_traces(marker=dict(size=15, line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(height=500, xaxis_title="Timeline")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ยังไม่มีข้อมูลของเครื่องนี้")

# --- 4. หน้า Data Entry ---
elif menu == "Data Entry (กรอกข้อมูล)":
    st.title("📝 บันทึกการเปลี่ยนอะไหล่")
    
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("วันที่")
            ac = st.selectbox("ทะเบียนเครื่อง", ["HS-PGY", "HS-PGN", "HS-PPB", "HS-PPC", "HS-PGX", "HS-PPT", "HS-PPE", "HS-PPF"])
            pos = st.selectbox("ตำแหน่ง", ["ELAC 1", "ELAC 2", "SEC 1", "SEC 2", "SEC 3", "FCDC 1", "FCDC 2"])
        with col2:
            sn = st.text_input("S/N ตัวที่ใส่เข้า (SN IN)", placeholder="เช่น SEC ...1851")
            note = st.text_area("หมายเหตุ / อาการเสีย", placeholder="เช่น เปลี่ยนเพราะ Vibration, Reset ไม่หาย...")
            
        submitted = st.form_submit_button("บันทึกข้อมูล")
        
        if submitted:
            if sn:
                entry = {
                    "Date": str(date),
                    "Aircraft": ac,
                    "Position": pos,
                    "SN_In": sn,
                    "Note": note
                }
                save_data(entry)
                st.success("✅ บันทึกเรียบร้อย! ข้อมูลถูกเพิ่มลงใน Database แล้ว")
            else:
                st.error("⚠️ กรุณากรอก S/N")

# --- 5. หน้า View Data ---
elif menu == "View Data (ดูตาราง)":
    st.title("🗂️ ฐานข้อมูลทั้งหมด")
    st.dataframe(df, use_container_width=True)
    
    # ปุ่มดาวน์โหลด CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("ดาวน์โหลด CSV", csv, "maintenance_log.csv", "text/csv")