
    try:
        year = int(data['year'])
    except (TypeError, ValueError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO students (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                year,
                str(data['section']).strip().upper()
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
    except sqlite3.IntegrityError as error:
        return jsonify({"error": f"Could not add student: {error}"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Student added", "id": new_id}), 201


@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()
    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?', (id,)
        ).fetchone()
    finally:
        conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data is required"}), 400

    required_fields = ['student_id', 'name', 'program', 'year', 'section']
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": "All student fields are required",
            "required_fields": required_fields
        }), 400

    try:
        year = int(data['year'])
    except (TypeError, ValueError):
        return jsonify({"error": "Year must be a number"}), 400

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
            SET student_id = ?, name = ?, program = ?, year = ?, section = ?
            WHERE id = ?
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                year,
                str(data['section']).strip().upper(),
                id
            )
        )
        conn.commit()
    except sqlite3.IntegrityError as error:
        return jsonify({"error": f"Could not update student: {error}"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Student updated"})


@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    try:
        cursor = conn.execute('DELETE FROM students WHERE id = ?', (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Student deleted"})


if __name__ == '__main__':
    app.run(debug=True)
