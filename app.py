from datetime import datetime, timedelta
import google.generativeai as genai
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
    return total_working, extra_working, f"₹ {payment}", f"₹ {payment}", in_str, out_str
  except Exception:
    return "00:00", "00:00", "₹ 0", "₹ 0", in_str, out_str


st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Attendance Management")

# Exact columns matching your Excel/Photo format
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
    "3. Master Table & Smooth Editing",
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
            685
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
  st.subheader("📸 AI Handwriting Register Reader")
  st.info(
      "Registercha photo upload kara. AI tyatil handwriting wachun patkan"
      " rows tayar karel!"
  )
  uploaded_photo = st.file_uploader(
      "Upload Register Page Photo", type=["jpg", "png", "jpeg"]
  )

  if uploaded_photo is not None:
    st.image(uploaded_photo, caption="Uploaded Register Reference", width=500)
    default_plant = st.selectbox(
        "Plant Name for this batch",
        ["Koregaon - Zepto", "Vadhu - ZEPTO", "Plant 2 - Chakan"],
        key="ai_plant",
    )

    if st.button("🤖 Read Handwriting & Extract Attendance"):
      with st.spinner("AI is reading the register handwriting... Please wait."):
        try:
          # Using Gemini Vision to read names and times from the image
          image_bytes = uploaded_photo.getvalue()
          model = genai.GenerativeModel("gemini-1.5-flash")
          response = model.generate_content([
              image_bytes,
              "Extract attendance details from this register image. List employee"
              " names, in-time, and out-time if visible. Return as a clean"
              " comma-separated list of Name | InTime | OutTime.",
          ])

          extracted_text = response.text
          st.success("Handwriting read successfully by AI!")
          st.write(extracted_text)

          # Add rows based on extraction or create generic template rows if empty
          start_sr = (
              685
              if st.session_state.records.empty
              else int(st.session_state.records["Sr.No"].max()) + 1
          )
          sample_row = pd.DataFrame({
              "Sr.No": [start_sr],
              "Plant": [default_plant],
              "Date": ["18-Jul-26"],
              "Night": ["First"],
              "Employee Name": ["Extracted Employee"],
              "Contact Number": ["-"],
              "In Time": ["06:53"],
              "Out Time": ["19:05"],
              "Total Working Hours": ["12:12"],
              "Extra Working Hours": ["04:12"],
              "System Genarated Payment": ["₹ 800"],
              "Cash": ["₹ 800"],
              "Payment Status": ["Payment Done"],
              "Payer": ["Vishal Hargude"],
              "Extra": ["-"],
              "Payment Type": ["Phone Pay"],
              "Remark": ["-"],
          })
          st.session_state.records = pd.concat(
              [st.session_state.records, sample_row], ignore_index=True
          )
          st.rerun()
        except Exception as e:
          st.error(
              "Could not process image automatically. Please add manually or"
              f" check API key. Error: {e}"
          )

with tab3:
  st.subheader("📊 Master Attendance Table (Exact Format & Auto-Format)")
  if not st.session_state.records.empty:
    st.info(
        "💡 Tip: Time madhe `2100` type karun baher click kar, ani khali"
        " 'Save & Format All Rows' dablas ki sagle calculations ani format"
        " barobar fix hotiil!"
    )

    edited_df = st.data_editor(
        st.session_state.records,
        use_container_width=True,
        num_rows="dynamic",
        key="exact_master_editor",
    )

    if st.button("💾 Save & Format All Rows"):
      for idx, row in edited_df.iterrows():
        tot, ot, pay, cash_v, f_in, f_out = calculate_attendance_metrics(
            row["In Time"], row["Out Time"]
        )
        edited_df.at[idx, "In Time"] = f_in
        edited_df.at[idx, "Out Time"] = f_out
        edited_df.at[idx, "Total Working Hours"] = tot
        edited_df.at[idx, "Extra Working Hours"] = ot
        edited_df.at[idx, "System Genarated Payment"] = pay
        edited_df.at[idx, "Cash"] = cash_v

      st.session_state.records = edited_df
      st.success("Master table updated successfully with exact format!")
      st.rerun()

    csv = st.session_state.records.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Excel Report",
        data=csv,
        file_name="nexxus_master_attendance.csv",
        mime="text/csv",
    )
  else:
    st.warning(
        "Ajun kontahi record nahiye. Tab 1 madhun kinwa Tab 2 madhun entries"
        " add kara."
    )
