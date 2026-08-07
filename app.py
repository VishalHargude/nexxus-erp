from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NEXXUS FACILITY - Industrial Manpower Management",
    page_icon="⚡",
    layout="wide",
)

# Professional Dark Theme Styling Matching Screenshots
st.markdown(
    """
    <style>
    .main { background-color: #0b0f19; color: #e6e6e6; font-family: sans-serif; }
    h1, h2, h3 { color: #ff7518; font-weight: 600; }
    
    /* Header Container Card */
    .header-card {
        background-color: #121826;
        border: 1px solid #1e2638;
        border-left: 5px solid #ff7518;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Login Box */
    .login-box {
        background-color: #121826;
        border: 1px solid #1e2638;
        padding: 40px;
        border-radius: 12px;
        max-width: 450px;
        margin: auto;
    }
    
    .stButton>button { background-color: #ff7518; color: white; font-weight: bold; border-radius: 6px; border: none; padding: 0.6rem 1rem; width: 100%; }
    .stButton>button:hover { background-color: #e06612; }
    
    /* Input & Table Dark Styling overrides */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #1a2234; color: white; border: 1px solid #2d3748; }
    </style>
""",
    unsafe_allow_html=True,
)

# Top Banner Header Function
def render_header():
  st.markdown(
      """
        <div class="header-card">
            <h2 style="margin: 0; color: #ffffff; letter-spacing: 1px;">NEXXUS FACILITY</h2>
            <p style="margin: 5px 0 0 0; color: #9ca3af; font-size: 13px; letter-spacing: 2px;">INDUSTRIAL MANPOWER MANAGEMENT</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

# 1. LOGIN SYSTEM
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False

if not st.session_state.logged_in:
  render_header()
  st.markdown("<br>", unsafe_allow_html=True)
  
  col1, col2, col3 = st.columns([1, 1.2, 1])
  with col2:
    st.markdown(
        """
        <div class="login-box">
            <h3 style="text-align: center; color: #ff7518; margin-bottom: 25px;">🔒 ADMIN LOGIN</h3>
        """,
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
      username = st.text_input("USERNAME", value="ADMIN")
      password = st.text_input("PASSWORD", type="password", value="******")
      login_btn = st.form_submit_button("LOGIN")
      
      if login_btn:
        if username.upper() == "ADMIN" and (password == "admin123" or password == "******"):
          st.session_state.logged_in = True
          st.success("Login successful!")
          st.rerun()
        else:
          st.error("Invalid Username or Password! (Default: ADMIN / admin123)")
    st.markdown("</div>", unsafe_allow_html=True)
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
    return total_working, extra_working, payment, payment, in_str, out_str
  except Exception:
    return "00:00", "00:00", 0, 0, in_str, out_str


render_header()

columns_list = [
    "Sr",
    "Plant",
    "Date",
    "Shift",
    "Employee Name",
    "Contact",
    "In Time",
    "Out Time",
    "Total Hrs",
    "OT Hrs",
    "Sys Pay",
    "Cash (Net)",
    "Status",
    "Payer",
    "Bonus",
    "Pay Type",
    "Remark",
]

if "records" not in st.session_state:
  st.session_state.records = pd.DataFrame(columns=columns_list)

# Navigation tabs matching the screenshot layout
tab_choice = st.radio(
    "", ["📝 ENTRY", "📊 REPORTS", "🚪 LOGOUT"], horizontal=True, label_visibility="collapsed"
)

if tab_choice == "🚪 LOGOUT":
  st.session_state.logged_in = False
  st.rerun()

if tab_choice == "📝 ENTRY":
  st.subheader("📋 ATTENDANCE & PAYMENT ENTRY")
  
  with st.form("batch_entry_form"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
      batch_date = st.date_input("DATE", value=datetime.today())
    with c2:
      batch_plant = st.selectbox("PLANT", ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"])
    with c3:
      batch_payer = st.text_input("PAYER", value="Vishal Hargude")
    with c4:
      batch_pay_type = st.selectbox("PAYMENT TYPE", ["Phone Pay", "Net Banking", "Cash"])

    st.markdown("---")
    
    # Initialize editable rows state for multiple labour entry
    if "rows_count" not in st.session_state:
      st.session_state.rows_count = 2

    temp_rows = []
    for i in range(st.session_state.rows_count):
      st.markdown(f"**Labour Row #{i+1}**")
      r1, r2, r3, r4, r5, r6, r7, r8, r9 = st.columns([1.5, 1.2, 1, 1, 1, 1, 1, 1, 1])
      with r1:
        emp_name = st.text_input(f"Name {i+1}", placeholder="Employee Name", key=f"name_{i}")
      with r2:
        emp_contact = st.text_input(f"Contact {i+1}", placeholder="Mobile", key=f"contact_{i}")
      with r3:
        emp_shift = st.selectbox(f"Shift {i+1}", ["First", "Second", "Night", "RO"], key=f"shift_{i}")
      with r4:
        in_t = st.text_input(f"In {i+1}", placeholder="0600", key=f"in_{i}")
      with r5:
        out_t = st.text_input(f"Out {i+1}", placeholder="1800", key=f"out_{i}")
      with r6:
        status = st.selectbox(f"Status {i+1}", ["Pending", "Payment Done"], key=f"status_{i}")
      with r7:
        bonus = st.text_input(f"Bonus {i+1}", value="0", key=f"bonus_{i}")
      with r8:
        pay_type_row = st.selectbox(f"Type {i+1}", ["Phone Pay", "Net Banking", "Cash"], key=f"ptype_{i}")
      with r9:
        remark = st.text_input(f"Remark {i+1}", value="-", key=f"rem_{i}")

      if emp_name:
        tot_w, ot_w, s_pay, c_val, f_in, f_out = calculate_attendance_metrics(in_t, out_t)
        try:
          b_val = float(bonus)
        except:
          b_val = 0.0
        final_pay = s_pay + b_val
        
        temp_rows.append({
            "Sr": len(st.session_state.records) + len(temp_rows) + 1,
            "Plant": batch_plant,
            "Date": str(batch_date),
            "Shift": emp_shift,
            "Employee Name": emp_name.title(),
            "Contact": emp_contact if emp_contact else "-",
            "In Time": f_in,
            "Out Time": f_out,
            "Total Hrs": tot_w,
            "OT Hrs": ot_w,
            "Sys Pay": f"₹ {final_pay}",
            "Cash (Net)": f"₹ {final_pay}",
            "Status": status,
            "Payer": batch_payer,
            "Bonus": f"₹ {b_val}",
            "Pay Type": pay_type_row,
            "Remark": remark,
        })
      st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    add_row_btn = st.form_submit_button("+ ADD LABOUR ROW")
    if add_row_btn:
      st.session_state.rows_count += 1
      st.rerun()

    save_all_btn = st.form_submit_button("💾 SAVE ALL DATA TO SHEET")
    if save_all_btn:
      if temp_rows:
        df_new = pd.DataFrame(temp_rows)
        st.session_state.records = pd.concat([st.session_state.records, df_new], ignore_index=True)
        st.success("All data saved successfully to master sheet!")
        st.session_state.rows_count = 2
        st.rerun()
      else:
        st.error("Kripaya kamit-kami ek tari employee name bhara.")

  if not st.session_state.records.empty:
    st.markdown("---")
    st.subheader("📊 Saved Master Data Preview")
    st.dataframe(st.session_state.records, use_container_width=True)
    
    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Complete Report (CSV)",
        data=csv,
        file_name="nexxus_industrial_manpower.csv",
        mime="text/csv",
    )

elif tab_choice == "📊 REPORTS":
  st.subheader("📈 Operations Summary & Analytics Dashboard")
  if not st.session_state.records.empty:
    df_m = st.session_state.records.copy()
    total_entries = len(df_m)
    unique_plants = df_m["Plant"].nunique()
    
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total Manpower Entries", total_entries)
    col_m2.metric("Active Plants Managed", unique_plants)
    
    st.markdown("---")
    st.markdown("### Plant-wise Distribution")
    st.bar_chart(df_m["Plant"].value_counts())
  else:
    st.info("Ajun kontahi data save kelela nahiye. Entry tab madhe data add kara.")
