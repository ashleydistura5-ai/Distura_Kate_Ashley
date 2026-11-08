
import os
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = "students.db"

CLASSMATE_API_URL = "https://ladoing-kc-jane-marie.onrender.com/students"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# ENSURE SOURCE COLUMN EXISTS
# ==========================================

def ensure_source_column():
    conn = get_db_connection()

    try:
        columns = conn.execute(
            "PRAGMA table_info(students)"
        ).fetchall()

        column_names = [column["name"] for column in columns]

        if columns and "source" not in column_names:

            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

            conn.commit()

            print("Source column added successfully.")

    finally:
        conn.close()


# Run database check when the application starts.
ensure_source_column()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api")
def api():
    return "Welcome to my first API"


# ==========================================
# STUDENT INFORMATION
# ==========================================

@app.route("/student")
def get_student():
    return jsonify({
        "student_id": "24-00347",
        "name": "Kate Ashley Distura",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# GET ALL STUDENTS
# ==========================================

@app.route("/students")
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students"
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GET STUDENT BY ID
# ==========================================

@app.route("/students/<int:id>")
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

    finally:
        conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# ==========================================
# GET STUDENTS BY SECTION
# ==========================================

@app.route("/students/section/<section_name>")
def get_students_by_section(section_name):
    conn = get_db_connection()

    try:
        students = conn.execute(
            "SELECT * FROM students WHERE section = ?",
            (section_name.upper(),)
        ).fetchall()

        return jsonify([dict(student) for student in students])

    finally:
        conn.close()


# ==========================================
# GREETING API
# ==========================================

@app.route("/hello")
def say_hello():
    name = request.args.get("name", "Student")

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# COURSE INFORMATION
# ==========================================

@app.route("/course")
def get_course():
    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "code": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# SKILLS API
# ==========================================

@app.route("/skills")
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


# ==========================================
# STEP 3: PARTNER API ENDPOINT
# ==========================================

@app.route("/partner-records", methods=["GET"])
def get_partner_records():

    try:
        response = requests.get(
            CLASSMATE_API_URL,
            headers={"Accept": "application/json"},
            timeout=15
        )

        response.raise_for_status()

        return jsonify(response.json()), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "The partner API request timed out."
        }), 504

    except requests.exceptions.HTTPError as error:
        return jsonify({
            "error": "Unable to retrieve partner data",
            "details": str(error)
        }), 502

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to connect to the partner API",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "The partner API returned invalid JSON."
        }), 502


# ==========================================
# PREVIOUS CLASSMATE ENDPOINT
# ==========================================

@app.route("/classmate-students", methods=["GET"])
def get_classmate_students():
    return get_partner_records()


# ==========================================
# STEP 5: IMPORT PARTNER STUDENT
# ==========================================

@app.route("/import-student", methods=["POST"])
def import_student():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON data is required."
        }), 400

    required = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    if any(field not in data for field in required):
        return jsonify({
            "error": "All student fields are required."
        }), 400

    if any(
        not str(data[field]).strip()
        for field in ["student_id", "name", "program", "section"]
    ):
        return jsonify({
            "error": "Student fields cannot be empty."
        }), 400

    try:
        year = int(data["year"])

        if year < 1 or year > 10:
            raise ValueError

    except (TypeError, ValueError):
        return jsonify({
            "error": "Year must be a number from 1 to 10."
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                year,
                str(data["section"]).strip().upper(),
                "Classmate API"
            )
        )

        conn.commit()

        return jsonify({
            "message": "Partner record saved successfully.",
            "id": cursor.lastrowid,
            "source": "Classmate API"
        }), 201

    except sqlite3.IntegrityError as error:
        return jsonify({
            "error": str(error)
        }), 400

    finally:
        conn.close()


# ==========================================
# ADD LOCAL STUDENT
# ==========================================

@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON data is required"
        }), 400

    required = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    if any(field not in data for field in required):
        return jsonify({
            "error": "All student fields are required",
            "required_fields": required
        }), 400

    if any(
        not str(data[field]).strip()
        for field in ["student_id", "name", "program", "section"]
    ):
        return jsonify({
            "error": "Student fields cannot be empty"
        }), 400

    try:
        year = int(data["year"])

        if year < 1 or year > 10:
            raise ValueError

    except (TypeError, ValueError):
        return jsonify({
            "error": "Year must be a number from 1 to 10"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                year,
                str(data["section"]).strip().upper(),
                "Local"
            )
        )

        conn.commit()

        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully",
            "id": new_id,
            "source": "Local"
        }), 201

    except sqlite3.IntegrityError as error:
        return jsonify({
            "error": f"Could not add student: {error}"
        }), 400

    finally:
        conn.close()


# ==========================================
# GET STUDENT THROUGH API
# ==========================================

@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):

    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

    finally:
        conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ==========================================
# UPDATE STUDENT
# ==========================================

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON data is required"
        }), 400

    required = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    if any(field not in data for field in required):
        return jsonify({
            "error": "All student fields are required",
            "required_fields": required
        }), 400

    if any(
        not str(data[field]).strip()
        for field in ["student_id", "name", "program", "section"]
    ):
        return jsonify({
            "error": "Student fields cannot be empty"
        }), 400

    try:
        year = int(data["year"])

        if year < 1 or year > 10:
            raise ValueError

    except (TypeError, ValueError):
        return jsonify({
            "error": "Year must be a number from 1 to 10"
        }), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?", (id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        # Preserve the existing source when editing.

        conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                str(data["student_id"]).strip(),
                str(data["name"]).strip(),
                str(data["program"]).strip(),
                year,
                str(data["section"]).strip().upper(),
                id
            )
        )

        conn.commit()

    except sqlite3.IntegrityError as error:
        return jsonify({
            "error": f"Could not update student: {error}"
        }), 400

    finally:
        conn.close()

    return jsonify({
        "message": "Student updated successfully"
    })


# ==========================================
# DELETE STUDENT
# ==========================================

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

    finally:
        conn.close()

    return jsonify({
        "message": "Student deleted successfully"
    })


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
