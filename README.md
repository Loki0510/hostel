# 🏨 Hostel Management System

A web-based hostel management system built with **Streamlit** and **SQLite**, enabling both **Admin** and **Faculty** users to manage bed allocations, student assignments, and floor/room logistics efficiently.

---

## 🚀 Features


### 👨‍💼 Admin Functionalities
- Add new **floors**
- Add new **rooms** to selected floors
- Automatically create beds based on room capacity
- View all bed allocations (occupied & unoccupied)
- **Search students** by name or roll number
- **Remove student** from a bed
- **Move student** to another available bed
- View room/floor/bed hierarchy

---

### 👩‍🏫 Faculty Functionalities
- View all **available beds**
- Allocate students to vacant beds (with name, roll no, caste)
- View current student allocations
- **Search/filter** students by name or roll number

---

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [SQLite3](https://www.sqlite.org/index.html)
- **Language**: Python 3.9+


## ▶️ How to Run

1. **Install Requirements**
   ```bash
   pip install streamlit pandas
````

2. **Run the App**

   ```bash
   streamlit run hostel_mgmt_app.py
   ```



## 🧑‍💻 Author

**Lokesh Vinnakota** – *Designed for Sri Bhavishya Institutions*

---

## 📝 License
This project is licensed under the MIT License.

