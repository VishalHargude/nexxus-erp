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

# 1. LOGIN SYSTEM
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  st.title("⚡ NEXXUS FACILITY ERP - Login")
  st.subheader("Please login to access manpower records")
  with st.form("login_form"):
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password")
    login_btn = st.form_submit_button("Login")
    if login_btn:
      if username == "admin" and password == "admin123":
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.rerun()
      else:
        st.error("Invalid Username or Password! (Default: admin / admin123)")
  st.stop()


def format_time(time_val):
  t_str = str(time_val).strip().replace(":", "").replace(".", "")
  if len(t_str) == 4 and t_str.isdigit():
    return f"{t_str[:2]}:{t_str[2:]}"
  return str(time_val).strip()


# 2. AUTO-FILL CALCULATIONS BASED ON IN/OUT TIME
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
    return (
        total_working,
        extra_working,
        f"₹ {payment}",
        f"₹ {payment}",
        in_str,
        out_str,
    )
  except Exception:
    return "00:00", "00:00", "₹ 0", "₹ 0", in_str, out_str


st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Attendance Management")

# Logout button in sidebar
with st.sidebar:
  st.write("Logged in as: **Admin**")
  if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

columns_list = [
    "Sr.No",
    "Plant",
    "Date",
    "Night",
    "Employee Name",
    "Contact Number",
    "In Time",
    "Out Time",
    "Total Working Hours",
    "Extra Working Hours",
    "System Genarated Payment",
    "Cash",
    "Payment Status",
    "Payer",
    "Extra",
    "Payment Type",
    "Remark",
]

if "records" not in st.session_state:
  st.session_state.records = pd.DataFrame(columns=columns_list)

tab1, tab2, tab3 = st.tabs([
    "1. Executive Dashboard",
    "2. Fast Manual Entry",
    "3. Master Table & Filters",
])

with tab1:
  st.subheader("📈 Operations Dashboard & Summary")
  if not st.session_state.records.empty:
    df_metrics = st.session_state.records.copy()
    try:
      df_metrics["Numeric_Pay"] = (
          df_metrics["System Genarated Payment"]
          .astype(str)
          .str.replace("₹", "")
          .str.strip()
          .astype(float)
      )
    except Exception:
      df_metrics["Numeric_Pay"] = 0.0

    total_records = len(df_metrics)
    total_payout = df_metrics["Numeric_Pay"].sum()
    unique_plants = df_metrics["Plant"].nunique()
    pending_count = len(
        df_metrics[df_metrics["Payment Status"] == "Pending"]
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Entries", total_records)
    m2.metric("Total Payout (₹)", f"₹ {total_payout:,.2f}")
    m3.metric("Active Plants", unique_plants)
    m4.metric("Pending Payments", pending_count)

    st.markdown("---")
    c_left, c_right = st.columns(2)
    with c_left:
      st.markdown("### Plant-wise Distribution")
      plant_counts = df_metrics["Plant"].value_counts()
      st.bar_chart(plant_counts)
    with c_right:
      st.markdown("### Shift Breakdown")
      shift_counts = df_metrics["Night"].value_counts()
      st.bar_chart(shift_counts)
  else:
    st.info(
        "No records available yet. Add entries using the 'Fast Manual Entry'"
        " tab to view dashboard analytics."
    )

with tab2:
  st.subheader("Add Attendance - Fast Single-Line Entry")
  with st.form("quick_entry_form"):
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 = st.columns(12)

    with c1:
      plant_in = st.selectbox(
          "Plant",
          ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
      )
    with c2:
      date_in = st.date_input("Date")
    with c3:
      shift_in = st.selectbox("Night/Shift", ["First", "Second", "Night", "RO"])
    with c4:
      name_in = st.text_input("Employee Name", placeholder="Name")
    with c5:
      contact_in = st.text_input("Contact No", placeholder="Mobile")
    with c6:
      in_t = st.text_input("In Time", placeholder="0600")
    with c7:
      out_t = st.text_input("Out Time", placeholder="1800")
    with c8:
      pay_status = st.selectbox("Status", ["Pending", "Payment Done"])
    with c9:
      payer_in = st.text_input("Payer", value="Vishal Hargude")
    with c10:
      extra_in = st.text_input("Extra", placeholder="-")
    with c11:
      pay_type = st.selectbox("Type", ["Phone Pay", "Net Banking", "Cash"])
    with c12:
      remark_in = st.text_input("Remark", placeholder="-")

    submitted = st.form_submit_button("✅ Add Record")

    if submitted:
      if name_in:
        next_sr = (
            1
            if st.session_state.records.empty
            else int(st.session_state.records["Sr.No"].max()) + 1
        )
        tot_work, extra_work, sys_pay, cash_val, f_in, f_out = (
            calculate_attendance_metrics(in_t, out_t)
        )

        new_row = pd.DataFrame({
            "Sr.No": [next_sr],
            "Plant": [plant_in],
            "Date": [str(date_in)],
            "Night": [shift_in],
            "Employee Name": [name_in.title()],
            "Contact Number": [contact_in if contact_in else "-"],
            "In Time": [f_in],
            "Out Time": [f_out],
            "Total Working Hours": [tot_work],
            "Extra Working Hours": [extra_work],
            "System Genarated Payment": [sys_pay],
            "Cash": [cash_val],
            "Payment Status": [pay_status],
            "Payer": [payer_in],
            "Extra": [extra_in if extra_in else "-"],
            "Payment Type": [pay_type],
            "Remark": [remark_in if remark_in else "-"],
        })
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row], ignore_index=True
        )
        st.success(f"Record added successfully for {name_in.title()}!")
        st.rerun()
      else:
        st.error("Kripaya Employee Name takaa.")

with tab3:
  st.subheader("📊 Master Attendance Table & Multiple Filters")
  if not st.session_state.records.empty:
    with st.expander(
        "🔍 Filter Records (Search by Plant, Name, or Date)", expanded=True
    ):
      f_col1, f_col2, f_col3 = st.columns(3)
      with f_col1:
        all_plants = ["All"] + list(st.session_state.records["Plant"].unique())
        selected_filter_plant = st.selectbox("Filter by Plant", all_plants)
      with f_col2:
        search_name = st.text_input(
            "Search by Employee Name", placeholder="Type name..."
        )
      with f_col3:
        all_dates = ["All"] + list(st.session_state.records["Date"].unique())
        selected_filter_date = st.selectbox("Filter by Date", all_dates)

    filtered_df = st.session_state.records.copy()
    if selected_filter_plant != "All":
      filtered_df = filtered_df[filtered_df["Plant"] == selected_filter_plant]
    if search_name:
      filtered_df = filtered_df[
          filtered_df["Employee Name"]
          .str.contains(search_name, case=False, na=False)
      ]
    if selected_filter_date != "All":
      filtered_df = filtered_df[filtered_df["Date"] == selected_filter_date]

    st.info(
        "💡 Tip: Time madhe `2100` type karun baher click kara, ani khali"
        " 'Save & Format All Rows' dabla ki sagle calculations fix hotiil!"
    )

    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
        key="exact_master_editor",
    )

    if st.button("💾 Save & Format All Rows"):
      for idx, row in edited_df.iterrows():
        orig_idx = row.name
        tot, ot, pay, cash_v, f_in, f_out = calculate_attendance_metrics(
            row["In Time"], row["Out Time"]
        )
        st.session_state.records.at[orig_idx, "In Time"] = f_in
        st.session_state.records.at[orig_idx, "Out Time"] = f_out
        st.session_state.records.at[orig_idx, "Total Working Hours"] = tot
        st.session_state.records.at[orig_idx, "Extra Working Hours"] = ot
        st.session_state.records.at[orig_idx, "System Genarated Payment"] = pay
        st.session_state.records.at[orig_idx, "Cash"] = cash_v
        for col in columns_list:
          st.session_state.records.at[orig_idx, col] = row[col]

      st.success("Master table updated and saved successfully!")
      st.rerun()

    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning("Ajun kontahi record nahiye. Fast Manual Entry vapra.")
