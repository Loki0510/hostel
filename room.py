import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# ------------------------- AUTH SECTION -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 90vh;
            animation: fadeIn 1s ease-in-out;
        }
        .login-card {
            background-color: #f0f2f6;
            padding: 40px 60px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
            animation: fadeIn 1.5s ease-in-out;
        }
        </style>
        <div class='login-container'>
            <div class='login-card'>
                <h1 style='color: navy; margin-bottom: 30px;'>Sri Bhavishya Room Allotment System</h1>
                <h3 style='color: #333;'>🔐 Admin Login</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ------------------------------------------------------------------

# Dark mode toggle
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state["dark_mode"])
st.session_state["dark_mode"] = dark_mode

if dark_mode:
    st.markdown("""
        <style>
        body {
            background-color: #121212;
            color: white;
        }
        .stButton>button, .stSelectbox div, .stTextInput>div>div>input {
            background-color: #333 !important;
            color: white !important;
        }
        .css-1d391kg, .css-1cpxqw2, .css-ffhzg2 {
            background-color: #222 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Required columns for validation
REQUIRED_COLUMNS = {"bed_id", "room_id", "floor", "status", "student_name", "student_id"}

# Initialize or load room and bed status
def initialize_room_data():
    if os.path.exists("room_data.csv"):
        try:
            df = pd.read_csv("room_data.csv")
            if not REQUIRED_COLUMNS.issubset(df.columns):
                raise ValueError("Missing required columns in CSV.")
            return df
        except Exception as e:
            st.warning("Corrupted or invalid CSV detected. Recreating room data.")

    data = []
    for floor in range(1, 6):
        for room in range(1, 11):
            room_id = f"F{floor}-R{room}"
            for bed in range(1, 6):
                bed_id = f"{room_id}-B{bed}"
                data.append({"bed_id": bed_id, "room_id": room_id, "floor": floor, "status": "available", "student_name": "", "student_id": ""})
    df = pd.DataFrame(data)
    df = df.astype({'student_name': 'string', 'student_id': 'string'})
    df.to_csv("room_data.csv", index=False)
    return df

def save_room_data(df):
    df.to_csv("room_data.csv", index=False)

# Load data
df = initialize_room_data()

# Heading and logout button
st.markdown("<h1 style='text-align: center; color: navy;'>Sri Bhavishya Room Allotment System</h1>", unsafe_allow_html=True)
if st.button("🚪 Logout", key="logout"):
    st.session_state.authenticated = False
    st.session_state.page = "floor"
    st.experimental_rerun()

# Navigation logic
page = st.session_state.get("page", "floor")
selected_floor = st.session_state.get("selected_floor")
selected_room = st.session_state.get("selected_room")
selected_bed = st.session_state.get("selected_bed")

# Page: Floor selection
if page == "floor":
    st.subheader("🏢 Select a Floor")
    cols = st.columns(5)
    for i in range(1, 6):
        floor_beds = df[df['floor'] == i]
        booked = (floor_beds['status'] == 'booked').sum()
        available = (floor_beds['status'] == 'available').sum()
        with cols[(i-1)%5]:
            if st.button(f"Floor {i} (🛌 {booked} / {booked + available})"):
                st.session_state.page = "room"
                st.session_state.selected_floor = i
                st.rerun()

# Page: Room selection
elif page == "room":
    st.subheader(f"Rooms on Floor {selected_floor}")
    cols = st.columns(5)
    for r in range(1, 11):
        room_id = f"F{selected_floor}-R{r}"
        room_beds = df[df['room_id'] == room_id]
        is_full = all(room_beds['status'] == 'booked')
        room_color = '#f5c6cb' if is_full else '#d4edda'
        with cols[(r-1)%5]:
            room_html = f"""
            <button style='width:100%;padding:10px;border-radius:6px;border:none;background-color:{room_color};font-weight:bold;'>
                {room_id}
            </button>
            """
            st.markdown(room_html, unsafe_allow_html=True)
            if st.button(f"➡ {room_id}", key=f"room_{room_id}"):
                st.session_state.page = "bed"
                st.session_state.selected_room = room_id
                st.experimental_rerun()
    if st.button("🔙 Back to Floor Selection"):
        st.session_state.page = "floor"
        st.rerun()

# Page: Bed selection
elif page == "bed":
    room_id = selected_room
    st.subheader(f"Beds in Room {room_id}")
    room_beds = df[df['room_id'] == room_id]
    cols = st.columns(5)
    for i, bed in enumerate(room_beds.itertuples()):
        bed_img = "🛏️<br>🛏️"  # Double bed emoji stacked
        bg_color = '#d4edda' if bed.status == 'available' else '#f8d7da'
        label = f"{bed_img}"
        with cols[i % 5]:
            bed_html = f"""
            <div style='width:100%;padding:10px;border-radius:8px;border:none;background-color:{bg_color};font-size:20px;text-align:center;'>
                {label}
            </div>
            """
            st.markdown(bed_html, unsafe_allow_html=True)
            if st.button(f"➡ {bed.bed_id}", key=f"bed_{bed.bed_id}"):
                st.session_state.page = "book"
                st.session_state.selected_bed = bed.bed_id
                st.experimental_rerun()
    if st.button("🔙 Back to Rooms"):
        st.session_state.page = "room"
        st.rerun()

# Page: Booking
elif page == "book":
    bed_id = selected_bed
    bed_data = df[df['bed_id'] == bed_id].iloc[0]
    st.subheader(f"Booking Bed: {bed_id}")
    if bed_data['status'] == 'available':
        name = st.text_input("Student Name")
        sid = st.text_input("Student ID")
        if st.button("Confirm Booking"):
            df.loc[df['bed_id'] == bed_id, ['status']] = "booked"
            df.loc[df['bed_id'] == bed_id, ['student_name']] = pd.Series([str(name)], dtype='string')
            df.loc[df['bed_id'] == bed_id, ['student_id']] = pd.Series([str(sid)], dtype='string')
            save_room_data(df)
            st.success(f"Bed {bed_id} successfully booked!")
            st.session_state.page = "bed"
            st.rerun()
    else:
        st.info(f"Already booked by {bed_data['student_name']} (ID: {bed_data['student_id']})")
        name = st.text_input("Modify Name", value=bed_data['student_name'])
        sid = st.text_input("Modify Student ID", value=bed_data['student_id'])
        if st.button("Update Details"):
            df.loc[df['bed_id'] == bed_id, ['student_name']] = pd.Series([str(name)], dtype='string')
            df.loc[df['bed_id'] == bed_id, ['student_id']] = pd.Series([str(sid)], dtype='string')
            save_room_data(df)
            st.success("Details updated successfully")
            st.experimental_rerun()
        if st.button("❌ Clear Booking"):
            df.loc[df['bed_id'] == bed_id, ['status', 'student_name', 'student_id']] = ["available", "", ""]
            save_room_data(df)
            st.success("Booking cleared.")
            st.session_state.page = "bed"
            st.rerun()
        available_beds = df[(df['status'] == 'available') & (df['bed_id'] != bed_id)]['bed_id'].tolist()
        move_to = st.selectbox("Move booking to another bed", options=available_beds if available_beds else ["No beds available"])
        if move_to != "No beds available" and st.button("➡ Move Booking"):
            df.loc[df['bed_id'] == move_to, ['status', 'student_name', 'student_id']] = ["booked", bed_data['student_name'], bed_data['student_id']]
            df.loc[df['bed_id'] == bed_id, ['status', 'student_name', 'student_id']] = ["available", "", ""]
            save_room_data(df)
            st.success(f"Moved booking to {move_to}")
            st.session_state.page = "bed"
            st.rerun()
    if st.button("🔙 Back to Beds"):
        st.session_state.page = "bed"
        st.rerun()
    if st.button("🔜 Go to Floor Selection"):
        st.session_state.page = "floor"
        st.rerun()
