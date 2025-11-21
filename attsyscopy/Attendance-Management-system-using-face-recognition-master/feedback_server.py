from flask import Flask, render_template_string, request

app = Flask(__name__)

# Simple feedback page template
feedback_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Feedback</title>
</head>
<body>
    <h2>Submit Feedback</h2>
    <form method="POST">
        Student Code: <b>{{ code }}</b><br><br>
        Name: <input type="text" name="name" required><br><br>
        Feedback: <textarea name="feedback" rows="5" cols="30" required></textarea><br><br>
        <input type="submit" value="Submit">
    </form>
    {% if submitted %}
    <p style="color:green;">Feedback submitted successfully!</p>
    <p>Student Name: {{ name }}</p>
    <p>Feedback: {{ feedback }}</p>
    {% endif %}
</body>
</html>
"""

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    code = request.args.get('code', 'Unknown')
    submitted = False
    name = ""
    feedback_text = ""
    
    if request.method == 'POST':
        name = request.form['name']
        feedback_text = request.form['feedback']
        submitted = True
        # Here you can save the feedback to a CSV or database
        with open("feedback_records.csv", "a") as f:
            f.write(f"{code},{name},{feedback_text}\n")
    
    return render_template_string(feedback_html, code=code, submitted=submitted, name=name, feedback=feedback_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

