import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import os, pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

attendance_path = "Attendance"
feedback_path = "Feedback"

window = Tk()
window.title("Faculty Dashboard")
window.geometry("1300x750")
window.config(bg="#E8F1FF")

Label(window, text="FACULTY DASHBOARD", bg="#003d7a", fg="white",
      font=("Segoe UI", 28, "bold"), pady=15).pack(fill=X)

content_frame = Frame(window, bg="white", bd=5, relief=RIDGE)
content_frame.place(x=30, y=120, width=1240, height=520)

Label(window, text="Enter Subject:", bg="#E8F1FF", fg="#003d7a",
      font=("Segoe UI", 16, "bold")).place(x=30, y=70)

subject_entry = Entry(window, width=25, font=("Segoe UI", 16), bd=3, relief=RIDGE)
subject_entry.place(x=200, y=71)

msg_label = Label(window, text="", bg="#E8F1FF", fg="red",
                  font=("Segoe UI", 12, "bold"))
msg_label.place(x=550, y=76)

def display_df(df):
    for widget in content_frame.winfo_children():
        widget.destroy()

    if df.empty:
        Label(content_frame, text="No Records Found", font=("Segoe UI", 14, "bold"),
              bg="white", fg="red").pack(pady=20)
        return

    table = ttk.Treeview(content_frame, columns=list(df.columns), show="headings")
    table.pack(fill=BOTH, expand=True)

    for col in df.columns:
        table.heading(col, text=col)
        table.column(col, width=120, anchor=CENTER)

    for _, row in df.iterrows():
        table.insert("", END, values=list(row))

def show_attendance_with_feedback():
    msg_label.config(text="")
    subject = subject_entry.get().strip().upper()

    if not subject:
        msg_label.config(text="Enter subject!")
        return

    subject_dir = os.path.join(attendance_path, subject)
    if not os.path.exists(subject_dir):
        msg_label.config(text="No attendance found!")
        return

    files = sorted(os.listdir(subject_dir), reverse=True)
    df_att = pd.read_csv(os.path.join(subject_dir, files[0]))

    feedback_file = os.path.join(feedback_path, f"{subject}_feedback.csv")
    if os.path.exists(feedback_file):
        df_fb = pd.read_csv(feedback_file)

        rating_cols = df_fb.columns[1:-1]

        df_fb["Avg Rating"] = df_fb[rating_cols].mean(axis=1)

        df_att = df_att.rename(columns={"Enrollment": "Roll"})
        df_fb = df_fb.rename(columns={"Enrollment": "Roll"})

        df_final = pd.merge(df_att, df_fb[["Roll", "Avg Rating"]], on="Roll", how="left")

    else:
        df_final = df_att.copy()
        df_final["Avg Rating"] = "No Feedback"

    display_df(df_final)

def show_feedback():
    subject = subject_entry.get().strip().upper()
    file = os.path.join(feedback_path, f"{subject}_feedback.csv")

    if not os.path.exists(file):
        msg_label.config(text="No feedback found!")
        return

    df = pd.read_csv(file)
    display_df(df)

def show_feedback_percentage():
    subject = subject_entry.get().strip().upper()
    file = os.path.join(feedback_path, f"{subject}_feedback.csv")

    if not os.path.exists(file):
        return messagebox.showerror("Error", "No feedback found!")

    df = pd.read_csv(file)

    rating_cols = df.columns[1:-1]
    df["TotalRating"] = df[rating_cols].sum(axis=1)

    avg_rating = df["TotalRating"].mean()          # out of 100
    feedback_percentage = (df.shape[0] / 62) * 100 # Assuming class size = 62

    messagebox.showinfo(
        "Feedback Rating Overview",
        f"📘 Subject: {subject}\n\n"
        f"Total Students Submitted: {df.shape[0]}/62\n"
        f"Average Rating Score: {avg_rating:.2f} / 100\n"
        f"Feedback Submission %: {feedback_percentage:.2f}%"
    )

def show_charts():
    subject = subject_entry.get().strip().upper()
    file = os.path.join(feedback_path, f"{subject}_feedback.csv")

    if not os.path.exists(file):
        return messagebox.showerror("Error","No feedback found!")

    df = pd.read_csv(file)
    questions = df.columns[1:-1]
    avg = df[questions].mean()

    plt.figure()
    avg.plot(kind="bar")
    plt.title(f"{subject} | Average Ratings")
    plt.ylabel("Average (out of 10)")
    plt.show()

def generate_pdf():
    subject = subject_entry.get().strip().upper()
    file = os.path.join(feedback_path, f"{subject}_feedback.csv")

    if not os.path.exists(file):
        return messagebox.showerror("Error", "No Feedback Data")

    df = pd.read_csv(file)
    questions = df.columns[1:-1]
    avg = df[questions].mean()

    submitted_students = df['Enrollment'].tolist()  # List of students who submitted
    total_submitted = len(submitted_students)
    class_strength = 62  # Modify if dynamic needed
    feedback_percentage = (total_submitted / class_strength) * 100

    pdf_path = f"{subject}_Report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(150, 800, f"{subject} FEEDBACK REPORT")

    y = 770
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Total Students Submitted: {total_submitted} / {class_strength}")
    y -= 20
    c.drawString(50, y, f"Feedback Submission Percentage: {feedback_percentage:.2f}%")
    y -= 30

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Average Ratings:")
    y -= 20

    c.setFont("Helvetica", 12)
    for q in questions:
        c.drawString(50, y, f"{q}: {round(avg[q],2)} / 10")
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Students Who Submitted:")
    y -= 20

    c.setFont("Helvetica", 12)
    for student in submitted_students:
        c.drawString(50, y, f"- {student}")
        y -= 18
        if y < 50:  # New page if needed
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800

    c.save()
    messagebox.showinfo("Success", f"Report Saved: {pdf_path}")


btn_style = dict(font=("Segoe UI", 13, "bold"), bd=4, relief=RIDGE, height=2, width=22)

Button(window, text="View Feedback + Attendance", command=show_attendance_with_feedback,
       bg="#007bff", fg="white", **btn_style).place(x=30, y=670)

Button(window, text="View Raw Feedback", command=show_feedback,
       bg="#34A853", fg="white", **btn_style).place(x=360, y=670)

Button(window, text="View Charts", command=show_charts,
       bg="#FF9800", fg="white", **btn_style).place(x=690, y=670)

Button(window, text="Download PDF Report", command=generate_pdf,
       bg="#9C27B0", fg="white", **btn_style).place(x=1020, y=60)

# NEW BUTTON ADDED
Button(window, text="Feedback Rating %", command=show_feedback_percentage,
       bg="#0D9488", fg="white", **btn_style).place(x=1020, y=670)

window.mainloop()
