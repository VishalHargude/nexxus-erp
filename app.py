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

# Initialize session state matching your exact Excel columns structure
if "records" not in st.session_state:
  st.session_state.records = pd.DataFrame(
      columns=[
          "Sr.No",
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
        "1. Manual Entry",
        "2. Photo to Exact Table Rows",
        "3. Master Table & Reports",
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
      in_time = st.text_input("In Time (e.g. 06:53)", "06:53")
    with col5:
      out_time = st.text_input("Out Time (e.g. 19:05)", "19:05")
    with col6:
      payment_type = st.selectbox(
          "Payment Type", ["Phone Pay", "Net Banking", "Cash"]
      )

    col7, col8 = st.columns(2)
    with col7:
      extra = st.text_input("Extra / Bonus", "-")
    with col8:
      remark = st.text_input("Remark", "-")

    submitted = st.form_submit_button("Add to Master Table")
    if submitted:
      if emp_name:
        next_sr = (
            len(st.session_state.records) + 685
            if st.session_state.records.empty
            else int(st.session_state.records["Sr.No"].max()) + 1
        )
        new_row = pd.DataFrame({
            "Sr.No": [next_sr],
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
  st.subheader("📸 Upload Sheet Photo & Match Exact Lines/Serial Numbers")
  uploaded_photo = st.file_uploader(
      "Upload Attendance Register Photo", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Sheet", width=450)

    st.markdown("---")
    st.markdown(
        "### 🔢 Specify exact rows/lines present in this photo page:"
    )

    # Let user input exact number of rows as per their photo/serial numbers
    num_rows_input = st.number_input(
        "Enter exact number of entries (rows) in this photo page:",
        min_value=1,
        max_value=100,
        value=5,
    )

    st.info(
        f"💡 Tula ya photo madhye {num_rows_input} entries disat ahet. Khaliil"
        " table madhe tichi naave ani vela direct bhara:"
    )

    # Generate editable template rows matching exact count
    if "temp_photo_df" not in st.session_state or len(
        st.session_state.temp_photo_df
    ) != num_rows_input:
      start_sr = (
          685
          if st.session_state.records.empty
          else int(st.session_state.records["Sr.No"].max()) + 1
      )
      st.session_state.temp_photo_df = pd.DataFrame({
          "Sr.No": [start_sr + i for i in range(num_rows_input)],
          "Plant": ["Koregaon - Zepto"] * num_rows_input,
          "Date": ["18-Jul-26"] * num_rows_input,
          "Shift": ["First"] * num_rows_input,
          "Employee Name": [""] * num_rows_input,
          "Contact Number": ["-"] * num_rows_input,
          "In Time": ["06:53"] * num_rows_input,
          "Out Time": ["19:05"] * num_rows_input,
          "Payer": ["Vishal Hargude"] * num_rows_input,
          "Payment Type": ["Phone Pay"] * num_rows_input,
          "Extra": ["-"] * num_rows_input,
          "Remark": ["-"] * num_rows_input,
      })

    # Show interactive editor for exact rows mapping
    edited_photo_rows = st.data_editor(
        st.session_state.temp_photo_df,
        use_container_width=True,
        key="photo_row_editor",
    )

    if st.button("🚀 Load These Exact Rows into Master Table"):
      st.session_state.records = pd.concat(
          [st.session_state.records, edited_photo_rows], ignore_index=True
      )
      st.success(
          f"Successfully added {num_rows_input} exact rows to your Master"
          " Table!"
      )

with tab3:
  st.subheader("📊 Master Attendance Report & Editable Sheet")
  if not st.session_state.records.empty:
    st.info(
        "💡 Tip: Tula direct ya table madhe kuthehi click karun kontahi spelling"
        " kinwa vel edit karta yete!"
    )

    edited_df = st.data_editor(
        st.session_state.records, use_container_width=True, num_rows="dynamic"
    )

    if st.button("💾 Save All Changes"):
      st.session_state.records = edited_df
      st.success("Master table updated successfully!")

    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel/CSV Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning(
        "Ajun kontahi record save kela nahiye. Photo OCR kinwa Form vaprun"
        " records add kara."
    )
