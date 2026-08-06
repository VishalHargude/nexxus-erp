from datetime import datetime, timedelta
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


# Helper function to calculate working hours, OT, and payment automatically
def calculate_attendance_metrics(in_t, out_t):
  try:
    t1 = datetime.strptime(str(in_t).strip(), "%H:%M")
    t2 = datetime.strptime(str(out_t).strip(), "%H:%M")

    # Handle night shift crossing midnight
    if t2 < t1:
      diff = (t2 + timedelta(days=1)) - t1
    else:
      diff = t2 - t1

    total_seconds = diff.total_seconds()
    tot_h = int(total_seconds // 3600)
    tot_m = int((total_seconds % 3600) // 60)
    total_working = f"{tot_h:02d}:{tot_m:02d}"

    # Extra/OT calculation (Standard shift = 8 hours)
    ot_seconds = max(0, total_seconds - (8 * 3600))
    ot_h = int(ot_seconds // 3600)
    ot_m = int((ot_seconds % 3600) // 60)
    extra_working = f"{ot_h:02d}:{ot_m:02d}"

    # System Generated Payment (Base 800 for 8+ hours)
    payment = 800 if tot_h >= 8 else (tot_h * 100)

    return total_working, extra_working, f"₹ {payment}"
  except:
    return "00:00", "00:00", "₹ 0"


st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Daily Attendance Tracking")

# Initialize session state with exact columns matching your Excel sheet
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
          "Total Working Hours",
          "Extra Working Hours",
          "System Generated Payment",
          "Payer",
          "Payment Type",
          "Extra",
          "Remark",
      ]
  )

tab1, tab2, tab3 = st.tabs(
    [
        "1. Manual Entry",
        "2. Bulk Register Batch (50-100 Rows)",
        "3. Master Table & Auto-Calculations",
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
      in_time = st.text_input("In Time (HH:MM)", "06:53")
    with col5:
      out_time = st.text_input("Out Time (HH:MM)", "19:05")
    with col6:
      payment_type = st.selectbox(
          "Payment Type", ["Phone Pay", "Net Banking", "Cash"]
      )

    col7, col8 = st.columns(2)
    with col7:
      extra = st.text_input("Extra / Bonus", "-")
    with col8:
      remark = st.text_input("Remark", "-")

    submitted = st.form_submit_button("Add & Auto-Calculate")
    if submitted:
      if emp_name:
        next_sr = (
            685
            if st.session_state.records.empty
            else int(st.session_state.records["Sr.No"].max()) + 1
        )
        tot_work, extra_work, sys_pay = calculate_attendance_metrics(
            in_time, out_time
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
            "Total Working Hours": [tot_work],
            "Extra Working Hours": [extra_work],
            "System Generated Payment": [sys_pay],
            "Payer": [payer],
            "Payment Type": [payment_type],
            "Extra": [extra],
            "Remark": [remark],
        })
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row], ignore_index=True
        )
        st.success(f"Record added & calculated successfully for {emp_name}!")
      else:
        st.error("Kripaya Employee Name takaa.")

with tab2:
  st.subheader(
      "📸 Upload Register Photo & Generate Bulk Rows (50, 100 or as needed)"
  )
  uploaded_photo = st.file_uploader(
      "Upload Register Page Photo", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Reference", width=500)

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
      # Allows setting 50, 100 or any exact count
      num_entries = st.number_input(
          "Kiti entries ahet photo madhye? (Enter exact count)",
          min_value=1,
          max_value=200,
          value=13,
      )
    with col_b2:
      default_plant = st.selectbox(
          "Plant Name",
          ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
          key="batch_plant",
      )

    st.info(
        f"💡 {num_entries} rows tayar kele ahet. Tumhi naave taku shakshil"
        " ani In/Out time badalalas ki auto-calculation hoil."
    )

    if "bulk_df" not in st.session_state or len(st.session_state.bulk_df) != num_entries:
      start_sr = (
          685
          if st.session_state.records.empty
          else int(st.session_state.records["Sr.No"].max()) + 1
      )
      st.session_state.bulk_df = pd.DataFrame({
          "Sr.No": [start_sr + i for i in range(num_entries)],
          "Plant": [default_plant] * num_entries,
          "Date": ["18-Jul-26"] * num_entries,
          "Shift": ["First"] * num_entries,
          "Employee Name": ["" for _ in range(num_entries)],
          "Contact Number": ["-" for _ in range(num_entries)],
          "In Time": ["06:53" for _ in range(num_entries)],
          "Out Time": ["19:05" for _ in range(num_entries)],
          "Total Working Hours": ["12:12" for _ in range(num_entries)],
          "Extra Working Hours": ["04:12" for _ in range(num_entries)],
          "System Generated Payment": ["₹ 800" for _ in range(num_entries)],
          "Payer": ["Vishal Hargude" for _ in range(num_entries)],
          "Payment Type": ["Phone Pay" for _ in range(num_entries)],
          "Extra": ["-" for _ in range(num_entries)],
          "Remark": ["-" for _ in range(num_entries)],
      })

    edited_bulk = st.data_editor(
        st.session_state.bulk_df,
        use_container_width=True,
        key="bulk_data_editor",
    )

    if st.button("🚀 Push Bulk Rows to Master Table"):
      st.session_state.records = pd.concat(
          [st.session_state.records, edited_bulk], ignore_index=True
      )
      st.success(f"Successfully added all {num_entries} rows to Master Table!")

with tab3:
  st.subheader("📊 Master Attendance Report & Auto-Update Engine")
  if not st.session_state.records.empty:
    st.info(
        "💡 Tip: Tula kontahi In Time ya Out Time badalaycha asel tar direct"
        " ya table madhe click karun badal. Khali 'Recalculate & Save Changes'"
        " dablas ki Working Hours, OT ani Payment automatic update hoil!"
    )

    edited_df = st.data_editor(
        st.session_state.records, use_container_width=True, num_rows="dynamic"
    )

    if st.button("💾 Recalculate & Save All Changes"):
      # Auto-recalculate metrics for all rows based on current In/Out times
      for idx, row in edited_df.iterrows():
        t_work, e_work, s_pay = calculate_attendance_metrics(
            row["In Time"], row["Out Time"]
        )
        edited_df.at[idx, "Total Working Hours"] = t_work
        edited_df.at[idx, "Extra Working Hours"] = e_work
        edited_df.at[idx, "System Generated Payment"] = s_pay

      st.session_state.records = edited_df
      st.success(
          "Master table updated and all working hours/payments recalculated"
          " successfully!"
      )

    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel/CSV Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning("Ajun kontahi record save kela nahiye.")
