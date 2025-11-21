import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font
import geocoder  # For location tracking
import webbrowser  # To open Google Maps

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "TrainingImageLabel\\Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "StudentDetails\\studentdetails.csv"
attendance_path = "Attendance"

def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        if sub == "":
            text_to_speech("Please enter the subject name!!!")
            return
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            try:
                recognizer.read(trainimagelabel_path)
            except:
                e = "Model not found, please train model"
                Notifica.configure(
                    text=e, bg="white", fg="blue", width=33,
                    font=("times", 15, "bold"))
                Notifica.place(x=20, y=250)
                text_to_speech(e)
            
            facecasCade = cv2.CascadeClassifier(haarcasecade_path)
            df = pd.read_csv(studentdetail_path)
            cam = cv2.VideoCapture(0)
            font_cv = cv2.FONT_HERSHEY_SIMPLEX
            col_names = ["Enrollment", "Name", "Location", "Latitude", "Longitude"]
            attendance = pd.DataFrame(columns=col_names)
            
            ts = time.time()
            future = ts + 20  # 20 seconds attendance window
            
            while True:
                ret, im = cam.read()
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = facecasCade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    global Id
                    Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

                    if conf < 70:
                        Subject = tx.get()
                        date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                        
                        aa = df.loc[df["Enrollment"].astype(str) == str(Id)]["Name"].values
                        student_name = aa[0] if len(aa) > 0 else "Unknown"

                        
                        # Get location
                        try:
                            g = geocoder.ip('me')
                            if g.ok:
                                city = g.city if g.city else ""
                                state = g.state if g.state else ""
                                country = g.country if g.country else ""
                                location = ", ".join([city, state, country]).strip(", ")
                                lat, lng = g.latlng if g.latlng else (0, 0)
                                if not location:
                                    location = "Unknown Location"
                            else:
                                location = "Unknown Location"
                                lat, lng = 0, 0
                        except:
                            location = "Unknown Location"
                            lat, lng = 0, 0
                        
                        attendance.loc[len(attendance)] = [Id, student_name, location, lat, lng]

                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 4)

                        #uuuu
                        cv2.putText(im, f"{Id} - {student_name}", (x, y-10), font_cv, 1, (255, 255, 0), 2)

                    else:
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 4)
                        cv2.putText(im, "Unknown", (x, y-10), font_cv, 1, (0, 25, 255), 2)
                
                cv2.imshow("Filling Attendance...", im)
                key = cv2.waitKey(30) & 0xFF
                if key == 27 or time.time() > future:
                    break

            cam.release()
            cv2.destroyAllWindows()

            # Remove duplicates before saving
            attendance = attendance.drop_duplicates(subset=['Enrollment'], keep='first')

            # Save CSV
            date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            time_str = datetime.datetime.fromtimestamp(ts).strftime("%H-%M-%S")
            path = os.path.join(attendance_path, Subject)
            if not os.path.exists(path):
                os.makedirs(path)
            fileName = f"{path}/{Subject}_{date_str}_{time_str}.csv"
            attendance.to_csv(fileName, index=False)

            m = f"Attendance Filled Successfully for {Subject}"
            Notifica.configure(text=m, bg="white", fg="blue", width=33, font=("times", 15, "bold"))
            text_to_speech(m)
            Notifica.place(x=20, y=250)

            # Display attendance in Tkinter window with "View on Map"
            root = tk.Tk()
            root.title(f"Attendance of {Subject}")
            root.configure(background="white")

            # Remove duplicates during display also
            attendance = attendance.drop_duplicates(subset=['Enrollment'], keep='first')

            # Header
            for c, col_name in enumerate(attendance.columns):
                tk.Label(root, width=15, height=1, fg="blue",
                         font=("times", 15, "bold"), bg="white",
                         text=col_name, relief=tk.RIDGE).grid(row=0, column=c)
            tk.Label(root, width=15, height=1, fg="blue",
                     font=("times", 15, "bold"), bg="white",
                     text="Map", relief=tk.RIDGE).grid(row=0, column=len(attendance.columns))

            # Display rows
            for r, row in attendance.iterrows():
                for c, value in enumerate(row):
                    tk.Label(root, width=15, height=1, fg="black",
                             font=("times", 15, " bold "), bg="white",
                             text=value, relief=tk.RIDGE).grid(row=r+1, column=c)

                tk.Button(
                    root, text="View on Map", bg="blue", fg="white",
                    command=lambda lat=row['Latitude'], lng=row['Longitude']: webbrowser.open(f"https://www.google.com/maps?q={lat},{lng}")
                ).grid(row=r+1, column=len(attendance.columns), padx=5, pady=2)
            
            root.mainloop()

        except Exception as e:
            text_to_speech("No Face found for attendance")
            print(e)
            cv2.destroyAllWindows()

    # Tkinter subject window
    subject = Tk()
    subject.title("Subject...")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="white")

    tk.Label(subject, bg="white", relief=RIDGE, bd=10, font=("arial", 30)).pack(fill=X)
    tk.Label(subject, text="Enter the Subject Name", bg="white", fg="green", font=("arial", 25)).place(x=160, y=12)

    global Notifica
    Notifica = tk.Label(subject, text="Attendance filled Successfully", bg="blue", fg="white",
                        width=33, height=2, font=("times", 15, "bold"))

    tk.Label(subject, text="Enter Subject", width=10, height=2, bg="white", fg="blue",
             bd=5, relief=RIDGE, font=("times new roman", 15)).place(x=50, y=100)

    global tx
    tx = tk.Entry(subject, width=15, bd=5, bg="white", fg="blue", relief=RIDGE,
                  font=("times", 30, "bold"))
    tx.place(x=190, y=100)

    tk.Button(subject, text="Fill Attendance", command=FillAttendance, bd=7,
              font=("times new roman", 15), bg="white", fg="blue",
              height=2, width=12, relief=RIDGE).place(x=195, y=170)

    def Attf():
        sub = tx.get()
        if sub == "":
            text_to_speech("Please enter the subject name!!!")
        else:
            os.startfile(f"Attendance\\{sub}")

    tk.Button(subject, text="Check Sheets", command=Attf, bd=7, font=("times new roman", 15),
              bg="white", fg="blue", height=2, width=10, relief=RIDGE).place(x=360, y=170)

    subject.mainloop()
