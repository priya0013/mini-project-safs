Smart Attendance and Feedback System
Overview

The Smart Attendance and Feedback System is an AI-powered platform designed to automate student attendance using face recognition and to collect real-time feedback from students. The system improves attendance management, reduces manual work, and enables administrators and teachers to gather feedback efficiently.

This project integrates face recognition, geolocation tracking, and feedback collection with a user-friendly GUI built in Python (Tkinter). MongoDB is used as the backend database to store attendance, feedback, and student details.

Features

Face Recognition Attendance

Uses OpenCV and LBPH algorithm for accurate face recognition.

Captures student photos during attendance.

Automatically records student enrollment, name, timestamp, and location.

Generates CSV attendance sheets for each subject.

Duplicate entries are removed automatically.

Geolocation Tracking

Captures the latitude and longitude of students while taking attendance.

Converts GPS coordinates to a readable location (e.g., "Near Library, KEC Campus, Perundurai, Erode-63").

Locations can be viewed on Google Maps from the attendance records.

Manual Attendance Option

Teachers can manually fill attendance if needed.

Student details and location are automatically captured.

Attendance can be exported to CSV.

Feedback System

Students can submit feedback using two methods:

Manual Feedback Form: Enter ratings and comments in the application.

QR Code Feedback: Scan QR code to submit feedback via a web page.

Feedback is stored in MongoDB with a timestamp and subject.

User Interface

Developed using Tkinter for a clean and interactive GUI.

Supports registration, attendance, feedback, and report viewing.

Provides voice notifications using pyttsx3.

Database

MongoDB stores student details, attendance, feedback, and locations.

Easy to query and generate reports.

Tech Stack

Language: Python 3

GUI: Tkinter

Face Recognition: OpenCV (LBPH algorithm)

Database: MongoDB

APIs: Google Maps Geocoding API for location conversion

Other Libraries: pandas, geocoder, pyttsx3, qrcode, PIL

How to Use

Register Students

Capture student images using the "Register New Student" button.

Train the face recognition model after adding new students.

Take Attendance

Use the "Take Attendance" button.

The system recognizes faces and records attendance automatically.

Attendance is stored in CSV and MongoDB along with geolocation.

View Attendance

Check attendance sheets for each subject.

Locations can be viewed on Google Maps.

Collect Feedback

Manual feedback via application.

QR code feedback via mobile scanning.

Future Enhancements

Add real-time notification to teachers if a student is absent.

Improve location accuracy using Wi-Fi or GPS.

Integrate mobile app interface for student attendance and feedback.
