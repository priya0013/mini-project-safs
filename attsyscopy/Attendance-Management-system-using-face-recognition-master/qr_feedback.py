import qrcode
from PIL import Image, ImageTk
import tkinter as tk
import random
import string
import os

def qr_feedback_page():
    qr_window = tk.Toplevel()  # <-- use Toplevel instead of Tk
    qr_window.title("QR Code Feedback")
    qr_window.geometry("500x600")
    qr_window.configure(bg="snow")
    qr_window.iconbitmap("AMS.ico")

    tk.Label(qr_window, text="Scan this QR Code to Submit Feedback",
             font=("times", 16, "bold"), bg="snow").pack(pady=20)

    feedback_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    feedback_link = f"http://10.69.174.171:5000/feedback?code={feedback_code}"

    qr_img = qrcode.make(feedback_link)
    qr_path = f"QRCode_{feedback_code}.png"
    qr_img.save(qr_path)

    img = Image.open(qr_path)
    img = img.resize((300, 300))
    photo = ImageTk.PhotoImage(img)
    qr_label = tk.Label(qr_window, image=photo)
    qr_label.image = photo
    qr_label.pack(pady=20)


    def delete_qr():
        if os.path.exists(qr_path):
            os.remove(qr_path)

    tk.Button(qr_window, text="Close", command=lambda: [delete_qr(), qr_window.destroy()],
              bg="red", fg="white", font=("times", 15, "bold")).pack(pady=20)

    qr_window.mainloop()
