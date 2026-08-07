from datetime import datetime, timedelta
import google.generativeai as genai
from PIL import Image
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

# 1. SIMPLE LOGIN SYSTEM
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

# Configure Gemini AI (Make sure to configure key in Streamlit secrets or use fallback)
try:
  genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
  genai.configure(api_key="AIzaSyYourValidApiKeyHere")


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
  st.write(f"Logged in as: **Admin**")
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
    "1. Manual Entry",
    "2. AI Handwriting Register Reader",
    "3. Master Table & Filters",
])

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
      night_shift = st.selectbox("Night (Shift)", ["First", "Second", "Night"])
    with col3:
      contact_no = st.text_input("Contact Number", "-")
      payer = st.text_input("Payer", "Vishal Hargude")

    col4, col5, col6 = st.columns(3)
    with col4:
      in_time = st.text_input("In Time (e.g. 0653 or 2100)", "06:53")
    with col5:
      out_time = st.text_input("Out Time (e.g. 1905)", "19:05")
    with col6:
      payment_type = st.selectbox(
          "Payment Type", ["Phone Pay", "Net Banking", "Cash"]
      )

    col7, col8, col9 = st.columns(3)
    with col7:
      payment_status = st.selectbox(
          "Payment Status", ["Payment Done", "Pending"]
      )
    with col8:
      extra = st.text_input("Extra / Bonus", "-")
    with col9:
      remark = st.text_input("Remark", "-")

    submitted = st.form_submit_button("Add to Master Table")
    if submitted:
      if emp_name:
        next_sr = (
            1
            if st.session_state.records.empty
            else int(st.session_state.records["Sr.No"].max()) + 1
        )
        tot_work, extra_work, sys_pay, cash_val, f_in, f_out = (
            calculate_attendance_metrics(in_time, out_time)
        )

        new_row = pd.DataFrame({
            "Sr.No": [next_sr],
            "Plant": [selected_plant],
            "Date": [str(attendance_date)],
            "Night": [night_shift],
            "Employee Name": [emp_name],
            "Contact Number": [contact_no],
            "In Time": [f_in],
            "Out Time": [f_out],
            "Total Working Hours": [tot_work],
            "Extra Working Hours": [extra_work],
            "System Genarated Payment": [sys_pay],
            "Cash": [cash_val],
            "Payment Status": [payment_status],
            "Payer": [payer],
            "Extra": [extra],
            "Payment Type": [payment_type],
            "Remark": [remark],
        })
        st.session_state.records = pd.concat(
            [st.session_state.records, new_row], ignore_index=True
        )
        st.success(f"Record added successfully for {emp_name}!")
      else:
        st.error("Kripaya Employee Name takaa.")

with tab2:
  st.subheader("📸 AI Handwriting Register Reader (Photo / Screenshot)")
  st.info(
      "Registercha photo kinva screenshot upload kara. AI tyatil data"
      " automatically wachun master table madhe add karel!"
  )
  uploaded_photo = st.file_uploader(
      "Upload Register Page Photo / Screenshot", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Reference", width=500)
    default_plant = st.selectbox(
        "Plant Name for this batch",
        ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
        key="ai_plant",
    )
    batch_date = st.date_input("Date for this Batch", key="ai_date")
    night_shift_ai = st.selectbox(
        "Shift for this Batch", ["First", "Second", "Night"], key="ai_night"
    )

    if st.button("🤖 Read Handwriting & Auto-Fill Records"):
      with st.spinner("AI is reading the image and updating records..."):
        try:
          image = Image.open(uploaded_photo)
          model = genai.GenerativeModel("gemini-1.5-flash")
          prompt = (
              "Extract all employee attendance rows from this register image."
              " Return ONLY a list where each line represents one employee in"
              " the exact format: EmployeeName | InTime | OutTime. Do not"
              " include any extra markdown or text, just the lines."
          )
          response = model.generate_content([image, prompt])

          extracted_text = response.text.strip()
          lines = extracted_text.split("\n")

          added_count = 0
          for line in lines:
            if "|" in line:
              parts = [p.strip() for p in line.split("|")]
              if len(parts) >= 3:
                e_name, raw_in, raw_out = (
                    parts[0].title(),
                    parts[1],
                    parts[2],
                )

                next_sr = (
                    1
                    if st.session_state.records.empty
                    else int(st.session_state.records["Sr.No"].max()) + 1
                )
                tot_work, extra_work, sys_pay, cash_val, f_in, f_out = (
                    calculate_attendance_metrics(raw_in, raw_out)
                )

                new_row = pd.DataFrame({
                    "Sr.No": [next_sr],
                    "Plant": [default_plant],
                    "Date": [str(batch_date)],
                    "Night": [night_shift_ai],
                    "Employee Name": [e_name],
                    "Contact Number": ["-"],
                    "In Time": [f_in],
                    "Out Time": [f_out],
                    "Total Working Hours": [tot_work],
                    "Extra Working Hours": [extra_work],
                    "System Genarated Payment": [sys_pay],
                    "Cash": [cash_val],
                    "Payment Status": ["Pending"],
                    "Payer": ["Vishal Hargude"],
                    "Extra": ["-"],
                    "Payment Type": ["Phone Pay"],
                    "Remark": ["-"],
                })
                st.session_state.records = pd.concat(
                    [st.session_state.records, new_row], ignore_index=True
                )
                added_count += 1

          if added_count > 0:
            st.success(
                f"Successfully extracted and added {added_count} records"
                " automatically!"
            )
            st.rerun()
          else:
            st.warning(
                "AI could not parse rows automatically. Raw output:"
                f" {extracted_text}"
            )
        except Exception as e:
          st.error(f"AI Processing Error: {e}")

with tab3:
  st.subheader("📊 Master Attendance Table & Multiple Filters")
  if not st.session_state.records.empty:
    # 3. MULTIPLE FILTERS (Date, Name, Plant)
    with st.expander("🔍 Filter Records (Search by Plant, Name, or Date)", expanded=True):
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

    # Apply filters
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
      # Update back to main session state records
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
        # Update other edited fields
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
    st.warning("Ajun kontahi record nahiye. Manual Entry kinva AI Reader vapra.")
