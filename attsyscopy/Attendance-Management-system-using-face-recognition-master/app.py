from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)   # allow requests from Tkinter, JS, mobile, etc.

# ------------------ MongoDB Connection ------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]


# ------------------ API: Store Attendance + Location ------------------
@app.route("/api/attendance_location", methods=["POST"])
def attendance_location():
    try:
        data = request.json

        # Extract JSON fields
        enrollment = data.get("enrollment")
        subject = data.get("subject")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        address = data.get("address")  # optional: reverse geocoded text

        # Validate required fields
        if not all([enrollment, subject, latitude, longitude]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        # Store attendance in DB
        db.attendance.insert_one({
            "enrollment": enrollment,
            "subject": subject,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "timestamp": datetime.now()
        })

        return jsonify({
            "success": True,
            "message": "Attendance + location stored successfully"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------ Default Route ------------------
@app.route("/")
def home():
    return "Attendance Location API is running!"


# ------------------ Run Server ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
