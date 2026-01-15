import streamlit as st
import pandas as pd
import plotly.express as px

# --- ตั้งค่า ---
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# 🔴 ใส่ลิงก์ CSV ที่ได้จาก Google Sheet ตรงนี้ครับ (อย่าลืมใส่เครื่องหมายคำพูดคร่อม)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv" 

# --- ฟังก์ชันโหลดข้อมูล ---
# ใช้ @st.cache_data เพื่อไม่ให้โหลดใหม่ทุกครั้งที่กดปุ่ม ช่วยให้เว็บเร็วขึ้น
# ตั้ง ttl=60 แปลว่าให้จำข้อมูลไว้ 60 วินาที พอครบแล้วค่อยไปดึงจาก Google Sheet ใหม่
@st.cache_data(ttl=60)
def load_data():
    # อ่านไฟล์ CSV จากลิงก์ Google Sheet โดยตรง
    df = pd.read_csv(SHEET_URL)
    
    # เปลี่ยนชื่อหัวตารางจาก Google Form ให้เป็นชื่อที่เราใช้ในโค้ด (ภาษาอังกฤษ)
    # คุณต้องแก้ชื่อภาษาไทยด้านซ้าย ให้ตรงกับใน Google Form ของคุณเป๊ะๆ
    df = df.rename(columns={
        'Timestamp': 'Date',         # Google Form จะให้ Timestamp มาเสมอ
        'ประทับเวลา': 'Date',        # เผื่อเป็นภาษาไทย
        'Aircraft': 'Aircraft',      # ถ้าในฟอร์มชื่อ Aircraft อยู่แล้วก็ไม่ต้องแก้
        'Position': 'Position',
        'SN_In': 'SN_In',
        'Note': 'Note'
    })
    
    return df

# --- ส่วนหน้าเว็บ ---
st.title("✈️ Fleet Maintenance Dashboard")

# ปุ่มกดไปหน้ากรอกข้อมูล (เปิด Google Form)
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("ข้อมูลอัปเดตอัตโนมัติจาก Google Sheets")
with col2:
    # 🔴 ใส่ลิงก์หน้ากรอก Google Form ตรงนี้
    st.link_button("📝 กรอกข้อมูลใหม่ (Google Form)", "https://docs.google.com/forms/d/e/1FAIpQLSejfUq-SOuq82f0Mz0gtTZn2KYk0jR7w3LKrLaceOCB2MfRNw/viewform?usp=publish-editor")

try:
    df = load_data()
    
    # แปลงวันที่
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- ส่วนแสดงผลกราฟ (เหมือนเดิม) ---
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
        
        # แสดงตารางข้อมูลล่าสุด
        st.subheader("Recent Logs")
        st.dataframe(filtered_df.sort_values(by='Date', ascending=False), use_container_width=True)
        
    else:
        st.info("ไม่พบข้อมูลของเครื่องบินที่เลือก")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
    st.warning("คำแนะนำ: กรุณาเช็คว่าเอาลิงก์ CSV มาวางถูกต้องหรือไม่ และตั้งค่า Publish to Web แล้วหรือยัง")

