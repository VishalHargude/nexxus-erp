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
        "2. Photo to Exact Entries (Multi-Row)",
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
      in_time = st.text_input("In Time", "06:53")
    with col5:
      out_time = st.text_input("Out Time", "19:05")
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
            685
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
  st.subheader(
      "📸 Upload Register Photo & Generate Exact Number of Rows (e.g. 13, 100"
      " etc.)"
  )
  uploaded_photo = st.file_uploader(
      "Upload Register Page Photo", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Reference", width=450)

    st.markdown("---")
    st.markdown("### ⚙️ Configure Rows based on Photo:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
      # Default set to 13 as per your mention
      total_entries = st.number_input(
          "Kiti naave/entries ahet photo madhye? (Exact Count)",
          min_value=1,
          max_value=500,
          value=13,
      )
    with col_p2:
      default_plant = st.selectbox(
          "Default Plant for this batch",
          ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
      )

    st.info(
        f"💡 Photo madhye {total_entries} entries ahet. Khaliil table madhe"
        " tichi naave, in-time, out-time direct bhara kinwa paste kara:"
    )

    # Generate exact rows DataFrame
    if "batch_df" not in st.session_state or len(st.session_state.batch_df) != total_entries:
      start_sr = (
          685
          if st.session_state.records.empty
          else int(st.session_state.records["Sr.No"].max()) + 1
      )
      st.session_state.batch_df = pd.DataFrame({
          "Sr.No": [start_sr + i for i in range(total_entries)],
          "Plant": [default_plant] * total_entries,
          "Date": ["18-Jul-26"] * total_entries,
          "Shift": ["First"] * total_entries,
          "Employee Name": [""
                            for _ in range(total_entries)],
          "Contact Number": ["-" for _ in range(total_entries)],
          "In Time": ["06:53" for _ in range(total_entries)],
          "Out Time": ["19:05" for _ in range(total_entries)],
          "Payer": ["Vishal Hargude" for _ in range(total_entries)],
          "Payment Type": ["Phone Pay" for _ in range(total_entries)],
          "Extra": ["-" for _ in range(total_entries)],
          "Remark": ["-" for _ in range(total_entries)],
      })

    # Editable grid matching exact count
    edited_batch = st.data_editor(
        st.session_state.batch_df,
        use_container_width=True,
        key="batch_data_editor",
    )

    if st.button("🚀 Push All These Rows to Master Table"):
      st.session_state.records = pd.concat(
          [st.session_state.records, edited_batch], ignore_index=True
      )
      st.success(
          f"Successfully added all {total_entries} rows to your Master Table!"
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
    st.warning("Ajun kontahi record save kela nahiye.")
