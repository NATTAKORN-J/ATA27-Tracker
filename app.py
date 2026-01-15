import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Bangkok Airways Component Tracker", layout="wide")

# ชื่อไฟล์ฐานข้อมูล
FILE_PATH = 'maintenance_log.csv'

# --- 1. ฟังก์ชันจัดการข้อมูล (พร้อม Master Data ครบทุกลำ) ---
def load_data():
    if not os.path.exists(FILE_PATH):
        # สร้างข้อมูลตั้งต้น (Master Data) จากที่เราวิเคราะห์กันมา
        data = [
            # ---------------- HS-PGY ----------------
            {"Date": "2025-01-01", "Aircraft": "HS-PGY", "Position": "SEC 2", "SN_In": "SEC ...068", "Note": "Intermittent (SFCC Wiring)"},
            {"Date": "2025-09-01", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...590", "Note": "Ident Error (Rack Issue)"},
            {"Date": "2025-10-05", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...851", "Note": "Current Active (Hero)"},
            {"Date": "2025-09-26", "Aircraft": "HS-PGY", "Position": "SEC 3", "SN_In": "SEC ...1851", "Note": "Back from Shop"},

            # ---------------- HS-PPB ----------------
            {"Date": "2025-04-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...423", "Note": "From PGN -> Vibration!"},
            {"Date": "2025-10-11", "Aircraft": "HS-PPB", "Position": "SEC 3", "SN_In": "SEC ...240", "Note": "New Part Active"},

            # ---------------- HS-PGN ----------------
            {"Date": "2025-03-20", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...14143", "Note": "Failed (8 Months)"},
            {"Date": "2025-11-27", "Aircraft": "HS-PGN", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPC Active"},
            {"Date": "2025-04-11", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...13925", "Note": "From PPB -> Died"},
            {"Date": "2025-08-19", "Aircraft": "HS-PGN", "Position": "SEC 3", "SN_In": "SEC ...15782", "Note": "From SEC 1 (Suspect Wiring)"},

            # ---------------- HS-PGX ----------------
            {"Date": "2025-03-21", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8763", "Note": "Died (Elec Jerk)"},
            {"Date": "2025-05-07", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...7808", "Note": "From PPT -> Bad Spare"},
            {"Date": "2025-06-10", "Aircraft": "HS-PGX", "Position": "FCDC 2", "SN_In": "FCDC ...8072", "Note": "From PPC Active"},
            {"Date": "2025-12-21", "Aircraft": "HS-PGX", "Position": "ELAC 1", "SN_In": "ELAC ...Check", "Note": "Start Up Transient (Reset OK)"},

            # ---------------- HS-PPC ----------------
            {"Date": "2025-06-11", "Aircraft": "HS-PPC", "Position": "FCDC 2", "SN_In": "FCDC ...8150", "Note": "New Part Active"},
            {"Date": "2025-06-12", "Aircraft": "HS-PPC", "Position": "SEC 2", "SN_In": "SEC ...1851", "Note": "Faulty -> Sent to Shop"},
            {"Date": "2025-10-29", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...10729", "Note": "From PPE -> Failed Accel"},
            {"Date": "2025-11-12", "Aircraft": "HS-PPC", "Position": "ELAC 1", "SN_In": "ELAC ...010495", "Note": "From PPF (Confirmed Good)"},
        ]
        df = pd.DataFrame(data)
        # แปลงวันที่เป็น datetime เพื่อให้เรียงลำดับถูก
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
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
st.sidebar.title("✈️ Component Tracker")
st.sidebar.caption("Bangkok Airways Maintenance")
menu = st.sidebar.radio("Main Menu", ["Dashboard (Timeline)", "Data Entry (Record)", "Database (View All)"])

# --- 3. หน้า Dashboard ---
if menu == "Dashboard (Timeline)":
    st.title("📊 Aircraft Component History")
    
    # ตัวเลือกกรองเครื่องบิน
    aircraft_list = sorted(df['Aircraft'].unique())
    selected_ac = st.multiselect("Select Aircraft:", aircraft_list, default=aircraft_list)
    
    # กรองข้อมูล
    filtered_df = df[df['Aircraft'].isin(selected_ac)].copy()
    
    # สร้างกราฟ Timeline
    if not filtered_df.empty:
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
        filtered_df = filtered_df.sort_values(by="Date")

        fig = px.scatter(
            filtered_df,
            x="Date",
            y="Aircraft",
            color="SN_In", # สีตาม S/N
            symbol="Position",
            size_max=20,
            hover_data=["Position", "Note"],
            title="Maintenance Events Timeline",
            height=600
        )
        fig.update_traces(marker=dict(size=15, line=dict(width=2, color='DarkSlateGrey')))
        fig.update_layout(xaxis_title="Date", yaxis_title="Aircraft Registration")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select an aircraft to view history.")

# --- 4. หน้า Data Entry ---
elif menu == "Data Entry (Record)":
    st.title("📝 New Maintenance Record")
    st.markdown("บันทึกการเปลี่ยนอะไหล่ใหม่")
    
    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date (วันที่)")
            ac = st.selectbox("Aircraft (ทะเบียน)", ["HS-PGY", "HS-PPB", "HS-PGN", "HS-PGX", "HS-PPC", "HS-PPT", "HS-PPE", "HS-PPF"])
            pos = st.selectbox("Position (ตำแหน่ง)", ["ELAC 1", "ELAC 2", "SEC 1", "SEC 2", "SEC 3", "FCDC 1", "FCDC 2"])
        with col2:
            sn = st.text_input("S/N IN (ตัวใหม่ที่ใส่)", placeholder="e.g. SEC ...1851")
            note = st.text_area("Note / Reason (สาเหตุ)", placeholder="e.g. Swapped from HS-PGN, Reset failed...")
            
        submitted = st.form_submit_button("💾 Save Record")
        
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
                st.success(f"Saved! {ac} {pos} - {sn}")
                st.balloons()
            else:
                st.error("Please enter Serial Number (S/N).")

# --- 5. หน้า Database ---
elif menu == "Database (View All)":
    st.title("🗂️ Master Database")
    
    # แสดงตาราง
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    # ปุ่มดาวน์โหลด
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "maintenance_log.csv", "text/csv")
    
    # ปุ่มอัปเดต (กรณีแก้ในตารางแล้วอยากบันทึก)
    if st.button("Save Changes to Database"):
        edited_df.to_csv(FILE_PATH, index=False)
        st.success("Database updated successfully!")

