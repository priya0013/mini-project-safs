from tkinter import *
from tkinter import messagebox
from pymongo import MongoClient
import subprocess
import re

client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]
users = db["users"]

def open_login():
    window.destroy()
    subprocess.Popen(["python", "login.py"])

def signup():
    email = email_entry.get()
    password = pass_entry.get()
    confirm = confirm_entry.get()
    role = role_var.get()

    # Email format validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Error", "Invalid Email Format")
        return
    
    if email == "" or password == "" or confirm == "" or role == "":
        messagebox.showwarning("Warning", "All fields are required")
        return

    if password != confirm:
        messagebox.showerror("Error", "Passwords do not match")
        return

    if users.find_one({"email": email}):
        messagebox.showerror("Error", "Email already exists")
        return

    # Insert into DB
    users.insert_one({"email": email, "password": password, "role": role})
    messagebox.showinfo("Success", "Account Created Successfully")
    open_login()

# UI
window = Tk()
window.title("Signup Page")
window.geometry("350x360")

Label(window, text="SIGNUP", font=("Arial", 16, "bold")).pack(pady=10)

Label(window, text="Email").pack()
email_entry = Entry(window)
email_entry.pack()

Label(window, text="Password").pack()
pass_entry = Entry(window, show="*")
pass_entry.pack()

Label(window, text="Confirm Password").pack()
confirm_entry = Entry(window, show="*")
confirm_entry.pack()

Label(window, text="Select Role").pack(pady=5)
role_var = StringVar(value="")
Radiobutton(window, text="Student", variable=role_var, value="Student").pack()
Radiobutton(window, text="Faculty", variable=role_var, value="Faculty").pack()

Button(window, text="Create Account", command=signup).pack(pady=10)
Button(window, text="Back to Login", command=open_login).pack()

window.mainloop()
