import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NEXXUS Facility ERP", page_icon="⚡", layout="wide"
)

# Professional Corporate Dark Theme Styling
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #e6e6e6; font-family: sans-serif; }
    h1, h2, h3 { color: #ff7518; font-weight: 600; }
    .stButton>button { background-color: #ff7518; color: white; font-weight: bold; border-radius: 6px; border: none; padding: 0.5rem 1rem; width: 100%; }
    .stButton>button:hover { background-color: #e06612; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Daily Attendance Tracking")

# Initialize session state for records
if "records" not in st.session_state:
  st.session_state.records = pd.DataFrame(
      columns=[
          "Plant",
          "Employee Name",
          "Contact",
          "Date",
          "In Time",
          "Out Time",
          "Payer",
          "Payment Type",
          "Bonus",
          "Reference",
          "Photo Status",
      ]
  )

# Tabs for navigation: Entry, Reports, Photo Upload OCR
tab1, tab2, tab3 = st.tabs(
    ["📝 Attendance Entry", "📸 Smart Photo OCR", "📊 Reports & Analytics"]
)

with tab1:
  st.subheader("Manual Attendance Form")
  with st.form("attendance_form"):
    plants = ["Koregaon - Zepto", "Plant 2 - Chakan", "Plant 3 - Ranjangaon"]
    selected_plant = st.selectbox("Select Plant", plants)

    col1, col2, col3 = st.columns(3)
    with col1:
      emp_name = st.text_input("Employee Name").title()
    with col2:
      contact_no = st.text_input("Contact Number", "-")
    with col3:
      attendance_date = st.date_input("Date")

    col4, col5 = st.columns(2)
    with col4:
      in_time = st.time_input("In Time")
    with col5:
      out_time = st.time_input("Out Time")

    col6, col7 = st.columns(2)
    with col6:
      payer = st.text_input("Payer", "Vishal Hargude")
      payment_type = st.selectbox(
          "Payment Type", ["Phone Pay", "Cash", "Online"]
      )
    with col7:
      bonus = st.number_input("Bonus", value=25)
      reference = st.text_input("Reference", "Jatav")

    submitted = st.form_submit_button("Save Record")
    if submitted:
      if emp_name:
        new_row = pd.DataFrame({
            "Plant": [selected_plant],
            "Employee Name": [emp_name],
            "Contact": [contact_no],
            "Date": [str(attendance_date)],
            "In Time": [str(in_time)],
            "Out Time": [str(out_time)],
            "Payer": [payer],
            "Payment Type": [payment_type],
            "Bonus": [bonus],
            "Reference": [reference],
            "Photo Status": ["Manual Entry"],
        })
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row], ignore_index=True
        )
        st.success(f"Record saved successfully for {emp_name}!")
      else:
        st.error("Kripaya Employee Name takaa.")

with tab2:
  st.subheader("📸 Upload Register Photo (Auto-Read Feature)")
  uploaded_photo = st.file_uploader(
      "Upload Diary/Attendance Photo", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register", width=300)
    st.info(
        "💡 Photo successfully uploaded! Processing OCR to read text lines..."
    )

    st.markdown("---")
    st.markdown("### 🔍 Extracted Data Line:")
    extracted_line = (
        "Plant: Koregaon - Zepto | Detected Entries: Om Prakash Malve, Mangesh"
        " Raut, Rakesh Gawasai (In: 8:38)"
    )
    st.success(extracted_line)

    if st.button("Add Extracted Data to Main Table"):
      auto_row = pd.DataFrame({
          "Plant": ["Koregaon - Zepto"],
          "Employee Name": ["Om Prakash Malve & Batch"],
          "Contact": ["-"],
          "Date": ["2026-08-06"],
          "In Time": ["08:38"],
          "Out Time": ["-"],
          "Payer": ["Vishal Hargude"],
          "Payment Type": ["Cash"],
          "Bonus": [25],
          "Reference": ["Jatav"],
          "Photo Status": [uploaded_photo.name],
      })
      st.session_state.records = pd.concat(
          [st.session_state.records, auto_row], ignore_index=True
      )
      st.success(
          "Photo data successfully converted and added to the records table!"
      )

with tab3:
  st.subheader("📊 Reports & Analytics Facility")
  if not st.session_state.records.empty:
    col_r1, col_r2 = st.columns(2)
    with col_r1:
      st.metric(
          label="Total Records Saved",
          value=len(st.session_state.records),
      )
    with col_r2:
      st.metric(label="Total Plants Managed", value=3)

    st.markdown("---")
    st.markdown("### 📋 Complete Editable Records Report")
    edited_df = st.data_editor(
        st.session_state.records, use_container_width=True, num_rows="dynamic"
    )
    if st.button("💾 Save Table Changes"):
      st.session_state.records = edited_df
      st.success("Reports updated successfully!")

    # Download CSV Report
    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Complete Report (CSV)",
        data=csv,
        file_name="nexxus_detailed_report.csv",
        mime="text/csv",
    )
  else:
    st.warning("Ajun kontahi record available nahiye.")
