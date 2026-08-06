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
  st.session_state.records = []

# Plant Dropdown
plants = ["Koregaon - Zepto", "Plant 2 - Chakan", "Plant 3 - Ranjangaon"]
selected_plant = st.selectbox("Select Plant", plants)

col1, col2, col3 = st.columns(3)
with col1:
  emp_name = st.text_input("Employee Name")
  if emp_name:
    emp_name = emp_name.title()

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
  payment_type = st.selectbox("Payment Type", ["Phone Pay", "Cash", "Online"])
with col7:
  bonus = st.number_input("Bonus", value=25)
  reference = st.text_input("Reference", "Jatav")

# Photo Upload Option
uploaded_photo = st.file_uploader(
    "Upload Employee / Document Photo", type=["jpg", "png", "jpeg"]
)
if uploaded_photo is not None:
  st.image(uploaded_photo, caption="Uploaded Preview", width=150)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Save Record"):
  if emp_name:
    photo_status = (
        uploaded_photo.name if uploaded_photo is not None else "No Photo"
    )
    new_record = {
        "Plant": selected_plant,
        "Employee Name": emp_name,
        "Contact": contact_no,
        "Date": str(attendance_date),
        "In Time": str(in_time),
        "Out Time": str(out_time),
        "Payer": payer,
        "Payment Type": payment_type,
        "Bonus": bonus,
        "Reference": reference,
        "Photo": photo_status,
    }
    st.session_state.records.append(new_record)
    st.success(f"Record saved successfully for {emp_name} at {selected_plant}!")
  else:
    st.error("Kripaya Employee Name takaa.")

# Display Saved Records Table
st.markdown("---")
st.subheader("📋 Saved Records Table")
if st.session_state.records:
  df = pd.DataFrame(st.session_state.records)
  st.dataframe(df, use_container_width=True)
else:
  st.info("Ajun kontahi record save kela nahiye.")
