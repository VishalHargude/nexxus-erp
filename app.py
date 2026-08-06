import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NEXXUS Facility ERP", page_icon="⚡", layout="wide"
)

# Custom Styling for Orange & Black Theme
st.markdown(
    """
    <style>
    .main { background-color: #111111; color: #ffffff; }
    h1, h2, h3 { color: #FF6600; }
    .stButton>button { background-color: #FF6600; color: white; font-weight: bold; border-radius: 5px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("⚡ NEXXUS FACILITY ERP")
st.subheader("Manpower Solutions & Daily Attendance Tracking")

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

# Default fields
payer = st.text_input("Payer", "Vishal Hargude")
payment_type = st.selectbox("Payment Type", ["Phone Pay", "Cash", "Online"])
bonus = st.number_input("Bonus", value=25)
reference = st.text_input("Reference", "Jatav")

if st.button("Save Record"):
    st.success(
        f"Record saved successfully for {emp_name} at {selected_plant}!"
    )
