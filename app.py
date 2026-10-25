from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/api")
def api():
    return "Welcome to my first API"


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00347",
        "name": "Kate Ashley Distura",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })


# New route for course information
@app.route('/course')
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "code": "BSIT",
        "year": 3,
        "section": "B"
    })


# New route for skills
@app.route('/skills')
def get_skills():
    return jsonify({
        "skills": [
            "Python",
            "Flask",
            "HTML",
            "CSS",
            "JavaScript",
            "Database Management"
        ]
    })


if __name__ == '__main__':
    app.run(debug=True)