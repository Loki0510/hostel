# hostel_mgmt_app.py (Full Login + Faculty/Admin Dashboards + Schema Patch + Student Search)
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
                st.rerun()
            else:
                st.error("Invalid admin credentials")
        else:
            c.execute("SELECT * FROM faculty WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.role = "faculty"
                st.rerun()
            else:
                st.error("Invalid faculty credentials")
else:
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()

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

        st.markdown("### 📁 Current Allocations")
        search = st.text_input("Search by Name or Roll Number")
        allocations = c.execute("""
            SELECT rooms.room_number, beds.bed_number, beds.student_name, beds.roll_no, beds.caste 
            FROM beds 
            JOIN rooms ON beds.room_id = rooms.id 
            WHERE beds.is_occupied = 1
        """).fetchall()

        df = pd.DataFrame(allocations, columns=["Room", "Bed", "Name", "Roll No", "Caste"])
        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["Roll No"].str.contains(search, case=False)]

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No matching students found.")

    # === Admin Dashboard ===
    if st.session_state.role == "admin":
        st.subheader("🛠️ Admin Dashboard")

        st.markdown("### ➕ Add New Floor")
        new_floor = st.text_input("Enter Floor Name")
        if st.button("Add Floor"):
            if new_floor:
                c.execute("INSERT INTO floors (floor_name) VALUES (?)", (new_floor,))
                conn.commit()
                st.success(f"Floor '{new_floor}' added.")
            else:
                st.warning("Please enter a valid floor name.")

        st.markdown("### ➕ Add Room")
        floor_options = c.execute("SELECT id, floor_name FROM floors").fetchall()
        if floor_options:
            floor_dict = {f"{fname} (ID: {fid})": fid for fid, fname in floor_options}
            selected_floor = st.selectbox("Select Floor", list(floor_dict.keys()))
            room_number = st.text_input("Room Number")
            capacity = st.number_input("Capacity", min_value=1, max_value=10, step=1)
            if st.button("Add Room"):
                if room_number:
                    c.execute("INSERT INTO rooms (floor_id, room_number, capacity) VALUES (?, ?, ?)",
                              (floor_dict[selected_floor], room_number, capacity))
                    room_id = c.lastrowid
                    for i in range(1, capacity + 1):
                        c.execute("INSERT INTO beds (room_id, bed_number) VALUES (?, ?)",
                                  (room_id, f"Bed-{i}"))
                    conn.commit()
                    st.success(f"Room {room_number} added with {capacity} beds.")
                else:
                    st.warning("Please enter room number.")
        else:
            st.info("Please add a floor first.")

        st.markdown("### 🛎️ All Bed Allocations")
        search = st.text_input("Search Student (Name or Roll No)")
        all_beds = c.execute("""
            SELECT f.floor_name, r.room_number, b.bed_number, b.student_name, b.roll_no, b.caste, b.is_occupied
            FROM beds b
            JOIN rooms r ON b.room_id = r.id
            JOIN floors f ON r.floor_id = f.id
            ORDER BY f.id, r.id, b.id
        """).fetchall()
        df = pd.DataFrame(all_beds, columns=["Floor", "Room", "Bed", "Name", "Roll No", "Caste", "Occupied"])
        df["Occupied"] = df["Occupied"].apply(lambda x: "Yes" if x else "No")

        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["Roll No"].str.contains(search, case=False)]

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No matching students found.")
