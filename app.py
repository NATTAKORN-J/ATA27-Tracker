import streamlit as st
import pandas as pd

st.title("🕵️‍♂️ Debug Mode: เช็คข้อมูลจาก Google Sheet")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTz1rldEVq2bUlZT6RHwQzmUDCOLEaHFfyyposVcZosoLMnowgJZWRMOb8_eIXZFzVu3YlZvzdiaJ0Z/pub?gid=529676428&single=true&output=csv"

if st.button("โหลดข้อมูลเดี๋ยวนี้"):
    st.cache_data.clear() # ล้าง Cache บังคับโหลดใหม่

try:
    df = pd.read_csv(SHEET_URL)
    st.success("✅ เชื่อมต่อ Google Sheet สำเร็จ!")
    
    st.write("### 1. ชื่อคอลัมน์ที่พบ (Column Names):")
    st.write(list(df.columns)) # โชว์ชื่อหัวตารางทั้งหมด
    
    st.write("### 2. ข้อมูลดิบ 5 แถวล่าสุด:")
    st.dataframe(df.tail()) # โชว์ข้อมูลท้ายตาราง

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
