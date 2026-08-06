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


def format_time(time_val):
  t_str = str(time_val).strip().replace(":", "").replace(".", "")
  if len(t_str) == 4 and t_str.isdigit():
    return f"{t_str[:2]}:{t_str[2:]}"
  return str(time_val).strip()


def calculate_attendance_metrics(in_t, out_t):
  in_str = format_time(in_t)
  out_str = format_time(out_t)
  try:
    t1 = datetime.strptime(in_str, "%H:%M")
    t2 = datetime.strptime(out_str, "%H:%M")

    if t2 < t1:
      diff = (t2 + timedelta(days=1)) - t1
    else:
      diff = t2 - t1

    total_seconds = diff.total_seconds()
    tot_h = int(total_seconds // 3600)
    tot_m = int((total_seconds % 3600) // 60)
    total_working = f"{tot_h:02d}:{tot_m:02d}"

    ot_seconds = max(0, total_seconds - (8 * 3600))
    ot_h = int(ot_seconds // 3600)
    ot_m = int((ot_seconds % 3600) // 60)
    extra_working = f"{ot_h:02d}:{ot_m:02d}"

    payment = 800 if tot_h >= 8 else (tot_h * 100)
    return total_working, extra_working, f"₹ {payment}", in_str, out_str
  except Exception:
    return "00:00", "00:00", "₹ 0", in_str, out_str


st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Daily Attendance Tracking")

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
        "3. Master Table (Instant Auto-Update)",
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
      in_time = st.text_input("In Time (e.g. 0653 or 06:53)", "06:53")
    with col5:
      out_time = st.text_input("Out Time (e.g. 2100 or 21:00)", "19:05")
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
        tot_work, extra_work, sys_pay, f_in, f_out = (
            calculate_attendance_metrics(in_time, out_time)
        )

        new_row = pd.DataFrame({
            "Sr.No": [next_sr],
            "Plant": [selected_plant],
            "Date": [str(attendance_date)],
            "Shift": [shift],
            "Employee Name": [emp_name],
            "Contact Number": [contact_no],
            "In Time": [f_in],
            "Out Time": [f_out],
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
        st.success(f"Record added successfully for {emp_name}!")
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
      num_entries = st.number_input(
          "Kiti entries ahet photo madhye? (Enter exact count e.g. 50, 100)",
          min_value=1,
          max_value=500,
          value=13,
      )
    with col_b2:
      default_plant = st.selectbox(
          "Plant Name",
          ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
          key="batch_plant",
      )

    if st.button("🚀 Generate Exact Rows in Master Table"):
      start_sr = (
          685
          if st.session_state.records.empty
          else int(st.session_state.records["Sr.No"].max()) + 1
      )
      new_batch = pd.DataFrame({
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
      st.session_state.records = pd.concat(
          [st.session_state.records, new_batch], ignore_index=True
      )
      st.success(
          f"Successfully generated {num_entries} rows! Tab 3 madhe jaun naave"
          " type kara."
      )
      st.rerun()

with tab3:
  st.subheader("📊 Master Attendance Report (Instant Live Auto-Update)")
  if not st.session_state.records.empty:
    st.info(
        "💡 Kontechya hi cell madhe time (jasa ki 2100) type kar, bahar click"
        " kar—to instant `21:00` houn Working Hours ani Payment auto-update"
        " hoil!"
    )

    # Instant Editable Table with Auto-Calculation on Change
    edited_df = st.data_editor(
        st.session_state.records,
        use_container_width=True,
        num_rows="dynamic",
        key="master_live_editor",
    )

    # Check for changes and update instantly without any button
    data_changed = False
    for idx, row in edited_df.iterrows():
      tot, ot, pay, f_in, f_out = calculate_attendance_metrics(
          row["In Time"], row["Out Time"]
      )
      if (
          row["In Time"] != f_in
          or row["Out Time"] != f_out
          or row["Total Working Hours"] != tot
          or row["Extra Working Hours"] != ot
          or row["System Generated Payment"] != pay
      ):
        edited_df.at[idx, "In Time"] = f_in
        edited_df.at[idx, "Out Time"] = f_out
        edited_df.at[idx, "Total Working Hours"] = tot
        edited_df.at[idx, "Extra Working Hours"] = ot
        edited_df.at[idx, "System Generated Payment"] = pay
        data_changed = True

    if data_changed:
      st.session_state.records = edited_df
      st.rerun()

    st.markdown("---")
    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel/CSV Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning(
        "Ajun kontahi record nahiye. Tab 2 madhun photo takun rows generate"
        " kara."
    )
