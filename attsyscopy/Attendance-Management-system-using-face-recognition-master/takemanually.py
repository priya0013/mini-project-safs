
import tkinter as tk
import os, cv2
import pandas as pd
import datetime, time
import geocoder

# ------------------ Initialize ------------------
ts = time.time()
Date = datetime.datetime.fromtimestamp(ts).strftime("%Y_%m_%d")
timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
Hour, Minute, Second = timeStamp.split(":")
d = {}
index = 0

# ------------------ Capture Photo ------------------
def capture_photo(enrollment):
    if not os.path.exists("Photos"):
        os.makedirs("Photos")
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    photo_path = f"Photos/{enrollment}_{Date}_{Hour}-{Minute}-{Second}.jpg"
    if ret:
        cv2.imwrite(photo_path, frame)
    cam.release()
    cv2.destroyAllWindows()
    return photo_path

# ------------------ Main GUI ------------------
def manually_fill():
    global sb
    sb = tk.Tk()
    sb.iconbitmap("AMS.ico")
    sb.title("Enter subject name...")
    sb.geometry("580x320")
    sb.configure(background="snow")

    # Subject error popup
    def err_screen_for_subject():
        ec = tk.Tk()
        ec.geometry("300x100")
        ec.iconbitmap("AMS.ico")
        ec.title("Warning!!")
        ec.configure(background="snow")
        tk.Label(ec, text="Please enter subject name!!!", fg="red", bg="white",
                 font=("times", 16, " bold ")).pack()
        tk.Button(ec, text="OK", command=ec.destroy,
                  fg="black", bg="lawn green", width=9, height=1,
                  font=("times", 15, " bold ")).place(x=90, y=50)

    def fill_attendance():
        global subb
        subb = SUB_ENTRY.get()
        if subb == "":
            err_screen_for_subject()
            return

        sb.destroy()
        MFW = tk.Tk()
        MFW.iconbitmap("AMS.ico")
        MFW.title(f"Manually attendance of {subb}")
        MFW.geometry("880x470")
        MFW.configure(background="snow")

        def err_screen1():
            errsc2 = tk.Tk()
            errsc2.geometry("330x100")
            errsc2.iconbitmap("AMS.ico")
            errsc2.title("Warning!!")
            errsc2.configure(background="snow")
            tk.Label(errsc2, text="Please enter Student & Enrollment!!!",
                     fg="red", bg="white", font=("times", 16, " bold ")).pack()
            tk.Button(errsc2, text="OK", command=errsc2.destroy,
                      fg="black", bg="lawn green", width=9, height=1,
                      font=("times", 15, " bold ")).place(x=90, y=50)

        def testVal(inStr, acttyp):
            if acttyp == "1":  # insert
                if not inStr.isdigit():
                    return False
            return True

        # Labels and Entries
        ENR = tk.Label(MFW, text="Enter Enrollment", width=15, height=2, fg="white",
                       bg="blue2", font=("times", 15, " bold "))
        ENR.place(x=30, y=100)

        STU_NAME = tk.Label(MFW, text="Enter Student name", width=15, height=2,
                            fg="white", bg="blue2", font=("times", 15, " bold "))
        STU_NAME.place(x=30, y=200)

        global ENR_ENTRY
        ENR_ENTRY = tk.Entry(MFW, width=20, validate="key", bg="yellow", fg="red",
                              font=("times", 23, " bold "))
        ENR_ENTRY["validatecommand"] = (ENR_ENTRY.register(testVal), "%P", "%d")
        ENR_ENTRY.place(x=290, y=105)

        STUDENT_ENTRY = tk.Entry(MFW, width=20, bg="yellow", fg="red", font=("times", 23, " bold "))
        STUDENT_ENTRY.place(x=290, y=205)

        # Clear buttons
        tk.Button(MFW, text="Clear", command=lambda: ENR_ENTRY.delete(0, "end"),
                  fg="black", bg="deep pink", width=10, height=1,
                  font=("times", 15, " bold ")).place(x=690, y=100)

        tk.Button(MFW, text="Clear", command=lambda: STUDENT_ENTRY.delete(0, "end"),
                  fg="black", bg="deep pink", width=10, height=1,
                  font=("times", 15, " bold ")).place(x=690, y=200)

        # Enter data
        def enter_data_DB():
            global index, d
            ENROLLMENT = ENR_ENTRY.get()
            STUDENT = STUDENT_ENTRY.get()
            if ENROLLMENT == "" or STUDENT == "":
                err_screen1()
                return

            # Capture photo
            photo_path = capture_photo(ENROLLMENT)

            # Get GPS location
            try:
                g = geocoder.ip('me')
                latitude, longitude = g.latlng if g.latlng else ("Unknown", "Unknown")
            except:
                latitude, longitude = "Unknown", "Unknown"

            # Add attendance data
            d[index] = {
                "Enrollment": ENROLLMENT,
                "Name": STUDENT,
                Date: 1,
                "Photo": photo_path,
                "Latitude": latitude,
                "Longitude": longitude
            }
            index += 1
            ENR_ENTRY.delete(0, "end")
            STUDENT_ENTRY.delete(0, "end")
            print(d)

        # Convert to CSV
        def create_csv():
            df = pd.DataFrame(d).T  # transpose so index becomes rows
            df = df[["Enrollment", "Name", Date, "Photo", "Latitude", "Longitude"]]
            if not os.path.exists("Attendance(Manually)"):
                os.makedirs("Attendance(Manually)")
            csv_name = f"Attendance(Manually)/{subb}_{Date}_{Hour}-{Minute}-{Second}.csv"
            df.to_csv(csv_name, index=False)
            Notifi.configure(text="CSV created Successfully", bg="Green", fg="white", width=33,
                              font=("times", 19, "bold"))
            Notifi.place(x=180, y=380)

        DATA_SUB = tk.Button(MFW, text="Enter Data", command=enter_data_DB,
                             fg="black", bg="lime green", width=20, height=2,
                             font=("times", 15, " bold "))
        DATA_SUB.place(x=170, y=300)

        MAKE_CSV = tk.Button(MFW, text="Convert to CSV", command=create_csv,
                             fg="black", bg="red", width=20, height=2,
                             font=("times", 15, " bold "))
        MAKE_CSV.place(x=570, y=300)

        Notifi = tk.Label(MFW, text="", bg="Green", fg="white", width=33, height=2,
                          font=("times", 19, "bold"))

        MFW.mainloop()

    SUB = tk.Label(sb, text="Enter Subject", width=15, height=2,
                   fg="white", bg="blue2", font=("times", 15, " bold "))
    SUB.place(x=30, y=100)

    global SUB_ENTRY
    SUB_ENTRY = tk.Entry(sb, width=20, bg="yellow", fg="red", font=("times", 23, " bold "))
    SUB_ENTRY.place(x=250, y=105)

    tk.Button(sb, text="Fill Attendance", command=fill_attendance,
              fg="white", bg="deep pink", width=20, height=2,
              font=("times", 15, " bold ")).place(x=250, y=160)

    sb.mainloop()

# ------------------ Run ------------------
manually_fill()
