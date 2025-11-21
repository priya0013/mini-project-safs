from tkinter import *
from tkinter import messagebox
from pymongo import MongoClient
import subprocess
import sys

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]
users = db["users"]

def open_signup():
    window.destroy()
    subprocess.Popen([sys.executable, "signup.py"])

def login():
    email = email_entry.get()
    password = pass_entry.get()
    role = role_var.get()

    if email == "" or password == "" or role == "":
        messagebox.showwarning("Warning", "All fields are required")
        return

    # Find user
    user = users.find_one({"email": email, "password": password, "role": role})

    if user:
        messagebox.showinfo("Success", f"{role} Login Successful")
        window.destroy()

        # Redirect based on role
        if role == "Student":
            subprocess.Popen([sys.executable, "attendance.py"])
        else:
            subprocess.Popen([sys.executable, "faculty.py"])
    else:
        messagebox.showerror("Error", "Invalid Email, Password or Role")

# UI
window = Tk()
window.title("Login Page")
window.geometry("350x320")

Label(window, text="LOGIN", font=("Arial", 16, "bold")).pack(pady=10)

Label(window, text="Email").pack()
email_entry = Entry(window)
email_entry.pack()

Label(window, text="Password").pack()
pass_entry = Entry(window, show="*")
pass_entry.pack()

Label(window, text="Select Role").pack(pady=5)

role_var = StringVar(value="")
Radiobutton(window, text="Student", variable=role_var, value="Student").pack()
Radiobutton(window, text="Faculty", variable=role_var, value="Faculty").pack()

Button(window, text="Login", width=15, command=login).pack(pady=10)
Button(window, text="Create Account", width=15, command=open_signup).pack(pady=5)

window.mainloop()
