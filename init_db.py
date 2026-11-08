
import sqlite3

# Connect to the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Recreate the students table
cursor.execute("DROP TABLE IF EXISTS students")

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

# Student records
students = [
    ('24-00347', 'Kate Ashley Distura', 'BSIT', 3, 'B', 'Local'),
    ('24-0087', 'Kc Jane Marie Ladoing', 'BSIT', 3, 'B', 'Local'),
    ('24-00146', 'Gwyneth Joy Laud', 'BSIT', 3, 'B', 'Local'),
    ('24-00194', 'Raveen Emmanuel Celo', 'BSIT', 3, 'A', 'Local'),
    ('24-00234', 'Princess Grace Patricio', 'BSIT', 3, 'C', 'Local')
]

# Insert student records into the database
cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

# Save changes
conn.commit()

# Close the database connection
conn.close()

print("Database created successfully!")
print("5 local student records inserted successfully.")
