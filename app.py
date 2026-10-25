
import sqlite3
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api')
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


@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route('/students/section/<section_name>')
def get_students_by_section(section_name):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE section = ?',
        (section_name.upper(),)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route('/course')
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "code": "BSIT",
        "year": 3,
        "section": "B"
    })


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


# CREATE: Add a new student
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "All student fields are required",
            "required_fields": required_fields
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section']
            )
        )

        conn.commit()
        new_id = cursor.lastrowid

    finally:
        conn.close()

    return jsonify({
        "message": "Student added",
        "id": new_id
    }), 201


# READ: Get one student
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# UPDATE: Update an existing student
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "All student fields are required",
            "required_fields": required_fields
        }), 400

    conn = get_db_connection()

    try:
        existing_student = conn.execute(
            'SELECT id FROM students WHERE id = ?', (id,)
        ).fetchone()

        if existing_student is None:
            return jsonify({"error": "Student not found"}), 404

        conn.execute(
            """
            UPDATE students
            SET student_id = ?, name = ?, program = ?,
                year = ?, section = ?
            WHERE id = ?
            """,
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                id
            )
        )

        conn.commit()

    finally:
        conn.close()

    return jsonify({"message": "Student updated"})


# DELETE: Delete a student
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?', (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        conn.commit()

    finally:
        conn.close()

    return jsonify({"message": "Student deleted"})


if __name__ == '__main__':
    app.run(debug=True)
