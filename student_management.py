import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import csv
from datetime import datetime

# ---------------------- DATABASE SETUP ----------------------
conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    email TEXT,
    course TEXT,
    gender TEXT,
    dob TEXT,
    attendance INTEGER DEFAULT 0,
    grade TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
''')
conn.commit()

# ---------------------- LOGIN SCREEN ----------------------
def login():
    user = username_entry.get()
    pwd = password_entry.get()
    if user == "admin" and pwd == "admin123":
        login_window.destroy()
        main_app()
    else:
        messagebox.showerror("Login Failed", "Incorrect Username or Password")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

tk.Button(login_window, text="Login", command=login).pack(pady=20)

# ---------------------- MAIN APPLICATION ----------------------
def main_app():
    def add_student():
        try:
            name = entry_name.get()
            roll = entry_roll.get()
            email = entry_email.get()
            course = entry_course.get()
            gender = entry_gender.get()
            dob = entry_dob.get()

            if not name or not roll:
                messagebox.showerror("Input Error", "Name and Roll Number are required!")
                return

            cursor.execute(
                "INSERT INTO students (name, roll_no, email, course, gender, dob) VALUES (?, ?, ?, ?, ?, ?)",
                (name, roll, email, course, gender, dob)
            )
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully")
            clear_fields()
            load_students()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            print("Error:", e)  # <-- This will print to your VS Code terminal


    def clear_fields():
        entry_name.delete(0, tk.END)
        entry_roll.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_course.delete(0, tk.END)
        entry_gender.delete(0, tk.END)
        entry_dob.delete(0, tk.END)

    def load_students():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def update_attendance():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "No student selected")
            return
        student_id = tree.item(selected[0])['values'][0]
        today = datetime.today().strftime('%Y-%m-%d')
        cursor.execute("UPDATE students SET attendance = attendance + 1 WHERE id=?", (student_id,))
        cursor.execute("INSERT INTO attendance_log (student_id, date) VALUES (?, ?)", (student_id, today))
        conn.commit()
        load_students()

    def update_grade():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "No student selected")
            return
        grade = grade_entry.get()
        if not grade:
            messagebox.showwarning("Input", "Enter grade to update")
            return
        student_id = tree.item(selected[0])['values'][0]
        cursor.execute("UPDATE students SET grade=? WHERE id=?", (grade, student_id))
        conn.commit()
        load_students()

    def delete_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select", "No student selected")
            return
        student_id = tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this student?")
        if confirm:
            cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            cursor.execute("DELETE FROM attendance_log WHERE student_id=?", (student_id,))
            conn.commit()
            load_students()

    def search_student():
        roll = search_entry.get()
        if not roll:
            messagebox.showwarning("Input", "Enter Roll Number to search")
            return
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM students WHERE roll_no=?", (roll,))
        result = cursor.fetchall()
        if result:
            for row in result:
                tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("Not Found", "No student found with this roll number")

    def export_csv():
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file:
            cursor.execute("SELECT * FROM students")
            data = cursor.fetchall()
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Roll No", "Email", "Course", "Gender", "DOB", "Attendance", "Grade"])
                writer.writerows(data)
            messagebox.showinfo("Success", "Data exported successfully!")

    root = tk.Tk()
    root.title("Student Management System")
    root.geometry("1000x700")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Name").grid(row=0, column=0)
    tk.Label(frame, text="Roll No").grid(row=0, column=2)
    tk.Label(frame, text="Email").grid(row=1, column=0)
    tk.Label(frame, text="Course").grid(row=1, column=2)
    tk.Label(frame, text="Gender").grid(row=2, column=0)
    tk.Label(frame, text="DOB (YYYY-MM-DD)").grid(row=2, column=2)

    entry_name = tk.Entry(frame)
    entry_roll = tk.Entry(frame)
    entry_email = tk.Entry(frame)
    entry_course = tk.Entry(frame)
    entry_gender = tk.Entry(frame)
    entry_dob = tk.Entry(frame)

    entry_name.grid(row=0, column=1)
    entry_roll.grid(row=0, column=3)
    entry_email.grid(row=1, column=1)
    entry_course.grid(row=1, column=3)
    entry_gender.grid(row=2, column=1)
    entry_dob.grid(row=2, column=3)

    tk.Button(frame, text="Add Student", command=add_student).grid(row=3, column=0, columnspan=4, pady=10)

    tk.Label(root, text="Search by Roll No:").pack()
    search_entry = tk.Entry(root)
    search_entry.pack()
    tk.Button(root, text="Search", command=search_student).pack()
    tk.Button(root, text="Show All Students", command=load_students).pack()

    # TreeView
    cols = ("ID", "Name", "Roll No", "Email", "Course", "Gender", "DOB", "Attendance", "Grade")
    tree = ttk.Treeview(root, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10)

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(pady=10)

    tk.Button(bottom_frame, text="+1 Attendance", command=update_attendance).grid(row=0, column=0, padx=10)
    tk.Label(bottom_frame, text="Grade:").grid(row=0, column=1)
    grade_entry = tk.Entry(bottom_frame)
    grade_entry.grid(row=0, column=2)
    tk.Button(bottom_frame, text="Update Grade", command=update_grade).grid(row=0, column=3, padx=10)
    tk.Button(bottom_frame, text="Delete Student", command=delete_student).grid(row=0, column=4, padx=10)
    tk.Button(bottom_frame, text="Export to CSV", command=export_csv).grid(row=0, column=5, padx=10)

    load_students()
    root.mainloop()

login_window.mainloop()
