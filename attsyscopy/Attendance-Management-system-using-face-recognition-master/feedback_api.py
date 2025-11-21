from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_system"]
feedback_col = db["feedbacks"]

# Submit feedback
@app.route("/api/feedback", methods=["POST"])
def add_feedback():
    data = request.json

    # Required fields validation
    if "subject" not in data or "enrollment" not in data or "ratings" not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    data["timestamp"] = datetime.now()
    feedback_col.insert_one(data)
    return jsonify({"success": True, "message": "Feedback submitted successfully!"})

# Get all feedback for a subject
@app.route("/api/feedback/<subject>", methods=["GET"])
def get_feedback(subject):
    feedbacks = list(feedback_col.find({"subject": subject.upper()}))
    for f in feedbacks:
        f["_id"] = str(f["_id"])  # Convert ObjectId to string
    return jsonify({"success": True, "feedbacks": feedbacks})

# Optional: Get aggregated rating for a subject
@app.route("/api/feedback/<subject>/avg", methods=["GET"])
def avg_feedback(subject):
    feedbacks = list(feedback_col.find({"subject": subject.upper()}))
    if not feedbacks:
        return jsonify({"success": False, "message": "No feedback found"}), 404

    # Calculate average rating per question
    questions = list(feedbacks[0]["ratings"].keys())
    avg_ratings = {}
    for q in questions:
        avg_ratings[q] = sum(f["ratings"][q] for f in feedbacks) / len(feedbacks)

    return jsonify({"success": True, "avg_ratings": avg_ratings, "total_submissions": len(feedbacks)})

if __name__ == "__main__":
    app.run(debug=True)
