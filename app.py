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

# Initialize session state matching your Excel columns structure
if "records" not in st.session_state:
  st.session_state.records = pd.DataFrame(
      columns=[
          "Plant",
          "Date",
          "Shift",
          "Employee Name",
          "Contact Number",
          "In Time",
          "Out Time",
          "Payer",
          "Payment Type",
          "Extra",
          "Remark",
      ]
  )

tab1, tab2, tab3 = st.tabs(
    [
        "📝 Single / Bulk Entry",
        "📸 Register Photo Reference",
        "📊 Master Table & Reports",
    ]
)

with tab1:
  st.subheader("Add Individual Attendance Record")
  with st.form("attendance_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
      plants = ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"]
      selected_plant = st.selectbox("Plant", plants)
      emp_name = st.text_input("Employee Name").title()
    with col2:
      attendance_date = st.date_input("Date")
      contact_no = st.text_input("Contact Number", "-")
    with col3:
      shift = st.selectbox("Shift", ["First", "Second", "Night"])
      payer = st.text_input("Payer", "Vishal Hargude")

    col4, col5, col6 = st.columns(3)
    with col4:
      in_time = st.text_input("In Time (e.g. 08:38)", "08:30")
    with col5:
      out_time = st.text_input("Out Time (e.g. 19:05)", "19:00")
    with col6:
      payment_type = st.selectbox(
          "Payment Type", ["Phone Pay", "Net Banking", "Cash"]
      )

    col7, col8 = st.columns(2)
    with col7:
      extra = st.text_input("Extra / Bonus", "₹ 25")
    with col8:
      remark = st.text_input("Remark", "Bonus to Jatav")

    submitted = st.form_submit_button("Add to Master Table")
    if submitted:
      if emp_name:
        new_row = pd.DataFrame({
            "Plant": [selected_plant],
            "Date": [str(attendance_date)],
            "Shift": [shift],
            "Employee Name": [emp_name],
            "Contact Number": [contact_no],
            "In Time": [in_time],
            "Out Time": [out_time],
            "Payer": [payer],
            "Payment Type": [payment_type],
            "Extra": [extra],
            "Remark": [remark],
        })
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row], ignore_index=True
        )
        st.success(f"Record added successfully for {emp_name}!")
      else:
        st.error("Kripaya Employee Name takaa.")

with tab2:
  st.subheader("📸 Upload Register Photo for Verification")
  uploaded_photo = st.file_uploader(
      "Upload Diary Page Photo", type=["jpg", "png", "jpeg"]
  )
  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Reference", width=350)
    st.info(
        "💡 Photo safely uploaded! You can view this photo here side-by-side"
        " while entering names individually in the table to avoid any mistakes."
    )

with tab3:
  st.subheader("📊 Master Attendance Report & Editable Sheet")
  if not st.session_state.records.empty:
    st.info(
        "💡 Tip: Tula direct ya table madhe kuthehi click karun naave, vela,"
        " kinwa remarks edit karta yetat!"
    )

    # Fully editable data grid resembling Excel
    edited_df = st.data_editor(
        st.session_state.records, use_container_width=True, num_rows="dynamic"
    )

    if st.button("💾 Save All Changes"):
      st.session_state.records = edited_df
      st.success("Master table updated successfully!")

    # CSV Download Button matching your Excel needs
    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel/CSV Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning(
        "Ajun kontahi record save kela nahiye. Form madhun records add kara."
    )
