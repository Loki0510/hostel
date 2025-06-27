# hostel_mgmt_app.py (Part 6: Full Login + Faculty Display Fix + Schema Patch)
import streamlit as st
import sqlite3
import pandas as pd

# Initialize DB connection
conn = sqlite3.connect("hostel.db", check_same_thread=False)
c = conn.cursor()

# Create tables with extended fields
c.execute('''CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS floors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_name TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor_id INTEGER,
    room_number TEXT,
    capacity INTEGER,
    FOREIGN KEY(floor_id) REFERENCES floors(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER,
    bed_number TEXT,
    is_occupied INTEGER DEFAULT 0,
    student_name TEXT,
    roll_no TEXT,
    caste TEXT,
    FOREIGN KEY(room_id) REFERENCES rooms(id)
)''')

# === SCHEMA PATCH: add missing columns if not present ===
try:
    c.execute("ALTER TABLE beds ADD COLUMN roll_no TEXT")
except sqlite3.OperationalError:
    pass

try:
    c.execute("ALTER TABLE beds ADD COLUMN caste TEXT")
except sqlite3.OperationalError:
    pass

conn.commit()

# Insert default credentials
c.execute("SELECT * FROM admin")
if not c.fetchone():
    c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))

c.execute("SELECT * FROM faculty")
if not c.fetchone():
    c.execute("INSERT INTO faculty (username, password) VALUES (?, ?)", ("faculty", "fac123"))

conn.commit()

# Streamlit app config
st.set_page_config(page_title="Hostel Management Login", layout="wide")
st.title("🏨 Hostel Management System")

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    role = st.selectbox("Login as", ["Admin", "Faculty"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role == "Admin":
            c.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.experimental_rerun()
            else:
                st.error("Invalid admin credentials")
        else:
            c.execute("SELECT * FROM faculty WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.role = "faculty"
                st.experimental_rerun()
            else:
                st.error("Invalid faculty credentials")
else:
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.experimental_rerun()

    # === Faculty Dashboard ===
    if st.session_state.role == "faculty":
        st.subheader("👨‍🏫 Faculty Dashboard")

        st.markdown("### 📋 View & Allocate Bed")
        available_beds = c.execute("""
            SELECT beds.id, rooms.room_number, beds.bed_number 
            FROM beds 
            JOIN rooms ON beds.room_id = rooms.id 
            WHERE beds.is_occupied = 0
        """).fetchall()

        if available_beds:
            bed_map = {f"Room {rnum} - Bed {bnum} (ID: {bid})": bid for bid, rnum, bnum in available_beds}
            selected = st.selectbox("Select Available Bed", list(bed_map.keys()))

            student_name = st.text_input("Student Name")
            roll_no = st.text_input("Roll Number")
            caste = st.text_input("Caste")

            if st.button("Allocate Bed"):
                c.execute("""
                    UPDATE beds
                    SET is_occupied = 1,
                        student_name = ?,
                        roll_no = ?,
                        caste = ?
                    WHERE id = ?
                """, (student_name, roll_no, caste, bed_map[selected]))
                conn.commit()
                st.success(f"Allocated {selected} to {student_name}.")
        else:
            st.info("No available beds right now.")

        st.markdown("### 📑 Current Allocations")
        allocations = c.execute("""
            SELECT rooms.room_number, beds.bed_number, beds.student_name, beds.roll_no, beds.caste 
            FROM beds 
            JOIN rooms ON beds.room_id = rooms.id 
            WHERE beds.is_occupied = 1
        """).fetchall()

        if allocations:
            df = pd.DataFrame(allocations, columns=["Room", "Bed", "Name", "Roll No", "Caste"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No students allocated yet.")
