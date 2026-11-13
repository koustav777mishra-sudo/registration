
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# Database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            dob TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Student Registration
@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        dob = request.form.get("dob")

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO students
                (first_name, last_name, email, phone, dob)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone, dob))

            conn.commit()

            return render_template(
                "success.html",
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                dob=dob
            )

        except sqlite3.IntegrityError:
            return "This email is already registered!"

        finally:
            conn.close()

    return render_template("index.html")


# Admin Dashboard
@app.route("/dashboard")
def dashboard():

    search = request.args.get("search", "").strip()

    conn = get_db()

    if search:
        students = conn.execute("""
            SELECT * FROM students
            WHERE first_name LIKE ?
            OR last_name LIKE ?
            OR email LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:
        students = conn.execute("""
            SELECT * FROM students
            ORDER BY id DESC
        """).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        search=search
    )


# Delete Student
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":

    create_database()

    app.run(debug=True)
