import sqlite3

# Connect to the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Delete existing student records
cursor.execute("DELETE FROM students")

# Student records
students = [
    ('24-00347', 'Kate Ashley Distura', 'BSIT', 3, 'B'),
    ('24-0087', 'Kc Jane Marie Ladoing', 'BSIT', 3, 'B'),
    ('24-00146', 'Gwyneth Joy Laud', 'BSIT', 3, 'B'),
    ('24-00194', 'Raveen Emmanuel Celo', 'BSIT', 3, 'A'),
    ('24-00234', 'Princess Grace Patricio', 'BSIT', 3, 'C')
]

# Insert student records into the database
cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

# Save changes
conn.commit()

# Close the database connection
conn.close()

print("Database created successfully.")