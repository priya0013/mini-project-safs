import tkinter as tk
from tkinter import messagebox
import csv, os
import pandas as pd

# Folder to store feedback
feedback_folder = "Feedback"
if not os.path.exists(feedback_folder):
    os.makedirs(feedback_folder)

# Grade Calculator
def get_grade(avg):
    if avg >= 9: return "A"
    elif avg >= 8: return "B"
    elif avg >= 7: return "C"
    elif avg >= 6: return "D"
    else: return "E"

# Summary Report Generator
def generate_report(subject):
    file_path = os.path.join(feedback_folder, f"{subject}_feedback.csv")
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No feedback found for this subject")
        return

    df = pd.read_csv(file_path)
    questions = df.columns[1:-1]  # exclude enrollment & message
    avg_scores = df[questions].mean()

    report_data = []
    for q in questions:
        avg = round(avg_scores[q], 2)
        grade = get_grade(avg)
        report_data.append([q, avg, grade])

    overall_avg = round(avg_scores.mean(), 2)
    overall_grade = get_grade(overall_avg)

    summary_path = os.path.join(feedback_folder, f"{subject}_summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Average (Out of 10)", "Grade"])
        writer.writerows(report_data)
        writer.writerow([])
        writer.writerow(["Final Overall Score", overall_avg, overall_grade])

    messagebox.showinfo("Success", f"Summary generated!\nFile saved: {summary_path}")

# Feedback Form Window
def feedback_window():
    fb = tk.Toplevel()
    fb.title("Teacher Feedback")
    fb.geometry("900x700")
    fb.config(bg="white")
    fb.resizable(True, True)

    # Scrollable Canvas Frame
    canvas = tk.Canvas(fb, bg="white")
    scrollbar = tk.Scrollbar(fb, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="white")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title
    tk.Label(scroll_frame, text="STUDENT FEEDBACK FORM", font=("Arial", 22, "bold"), bg="white").pack(pady=10)

    # Subject & Roll No
    tk.Label(scroll_frame, text="Subject:", font=("Arial", 14), bg="white").pack(anchor="w", padx=20)
    subject_entry = tk.Entry(scroll_frame, font=("Arial", 14), width=35)
    subject_entry.pack(pady=5)

    tk.Label(scroll_frame, text="Roll Number:", font=("Arial", 14), bg="white").pack(anchor="w", padx=20)
    roll_entry = tk.Entry(scroll_frame, font=("Arial", 14), width=35)
    roll_entry.pack(pady=5)

    # Rating Questions
    questions = [
        "Knowledge base of teacher",
        "Communication skills",
        "Sincerity / Commitment",
        "Interest generated",
        "Course integration & relation",
        "Content delivery",
        "Accessibility & guidance",
        "Ability to evaluate & conduct exams",
        "Feedback given during course",
        "Overall ratings"
    ]

    ratings = [0] * len(questions)
    star_btns = []

    def give_rating(q_idx, rate):
        ratings[q_idx] = rate
        update_stars()

    def update_stars():
        for i in range(len(questions)):
            for j in range(10):
                star_btns[i][j].config(
                    text=str(j+1),
                    fg="blue" if j < ratings[i] else "gray"
                )

    for i, q in enumerate(questions):
        tk.Label(scroll_frame, text=f"{i+1}. {q}", font=("Arial", 13), bg="white").pack(anchor="w", padx=30, pady=5)

        row_frame = tk.Frame(scroll_frame, bg="white")
        row_frame.pack()

        btn_row = []
        for j in range(10):
            btn = tk.Button(row_frame, text=str(j+1), font=("Arial", 10), bd=0,
                            command=lambda ii=i, jj=j+1: give_rating(ii, jj))
            btn.pack(side="left", padx=3)
            btn_row.append(btn)
        star_btns.append(btn_row)

    # Comments
    tk.Label(scroll_frame, text="Comments (optional):", font=("Arial", 14), bg="white").pack(anchor="w", padx=30, pady=10)
    message_text = tk.Text(scroll_frame, font=("Arial", 12), width=80, height=3)
    message_text.pack(pady=5)

    restricted_words = ["idiot", "stupid", "dumb", "hate", "ugly"]

    # Submit Feedback
    def submit_feedback():
        subject = subject_entry.get().strip().upper()
        roll = roll_entry.get().strip()
        message = message_text.get("1.0", "end").strip().lower()

        if not subject or not roll:
            messagebox.showerror("Error", "Please fill all fields")
            return

        if 0 in ratings:
            messagebox.showerror("Error", "Please answer ALL rating questions")
            return

        for w in restricted_words:
            if w in message.split():
                messagebox.showerror("Error", f"Remove inappropriate word: '{w}'")
                return

        file_path = os.path.join(feedback_folder, f"{subject}_feedback.csv")

        if not os.path.exists(file_path):
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Enrollment"] + questions + ["Message"])

        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([roll] + ratings + [message])

        messagebox.showinfo("Success", "Feedback submitted successfully 😊")
        fb.destroy()

    tk.Button(scroll_frame, text="Submit Feedback", font=("Arial",14), bg="green", fg="white", width=25,
              command=submit_feedback).pack(pady=20)

    tk.Button(scroll_frame, text="Generate Summary Report", font=("Arial",14), bg="blue", fg="white", width=30,
              command=lambda: generate_report(subject_entry.get().strip().upper())).pack(pady=5)

