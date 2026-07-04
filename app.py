from flask import Flask, render_template, request, send_file, redirect
import pandas as pd
import os
import sqlite3
import smtplib
from email.message import EmailMessage


app = Flask(__name__)

REPORT_FOLDER = "reports"

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)


def create_database():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(

        stu_id TEXT PRIMARY KEY,
        name TEXT,
        attend REAL,
        marks REAL,
        performance REAL,
        risk TEXT,
        reason TEXT,
        suggestion TEXT

    )
    """)

    conn.commit()
    conn.close()


create_database()
def send_emails_to_students(data):

    sender_email = "gayathriponugoti31@gmail.com"
    app_password = "bedh jroj fqnx iory"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

        smtp.login(sender_email, app_password)

        for _, row in data.iterrows():

            if pd.isna(row["EMAIL"]) or str(row["EMAIL"]).strip() == "":
                continue

            msg = EmailMessage()

            msg["Subject"] = "Student Performance Alert"
            msg["From"] = sender_email
            msg["To"] = row["EMAIL"]

            msg.set_content(f"""
Dear {row['NAME']},

This is an alert from the Student Performance Analysis System.

Reason:
{row['REASON']}

Please improve your attendance and academic performance.

Regards,
Student Performance Analysis System
""")

            smtp.send_message(msg)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/student")
def student():
    return render_template("student_login.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["file"]

    data = pd.read_excel(file)

    if "BEHAVE" in data.columns:
        data = data.drop(columns=["BEHAVE"])

    performance = []
    risk = []
    reason = []
    suggestion = []

    for index, row in data.iterrows():

        attendance = row["ATTEND"]
        marks = row["MARKS"]

        score = round((attendance + marks) / 2, 2)

        performance.append(score)

        if attendance < 75 and marks < 60:

            risk.append("High Risk")
            reason.append("Low Attendance and Low Marks")
            suggestion.append("Improve attendance and spend more time on academics.")

        elif attendance < 75:

            risk.append("Attendance Risk")
            reason.append("Attendance below 75%")
            suggestion.append("Attend classes regularly.")

        elif marks < 60:

            risk.append("Academic Risk")
            reason.append("Marks below 60")
            suggestion.append("Practice daily and revise important topics.")

        else:

            risk.append("Safe")
            reason.append("Good Performance")
            suggestion.append("Keep up the good work.")

    data["PERFORMANCE SCORE"] = performance
    data["RISK"] = risk
    data["REASON"] = reason
    data["SUGGESTION"] = suggestion

    # Save into database
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")

    for _, row in data.iterrows():

        cursor.execute("""
        INSERT INTO students
        (stu_id, name, attend, marks, performance, risk, reason, suggestion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            str(row["STU-ID"]),
            row["NAME"],
            float(row["ATTEND"]),
            float(row["MARKS"]),
            float(row["PERFORMANCE SCORE"]),
            row["RISK"],
            row["REASON"],
            row["SUGGESTION"]

        ))

    conn.commit()
    conn.close()

    safe_students = data[data["RISK"] == "Safe"]
    risk_students = data[data["RISK"] != "Safe"]

    safe_path = os.path.join(REPORT_FOLDER, "safe_students.xlsx")
    risk_path = os.path.join(REPORT_FOLDER, "risk_students.xlsx")

    safe_students.to_excel(safe_path, index=False)
    risk_students.to_excel(risk_path, index=False)

    total = len(data)
    safe = len(safe_students)
    risk_count = len(risk_students)

    average_score = round(data["PERFORMANCE SCORE"].mean(), 2)

    safe_percent = round((safe / total) * 100, 1) if total > 0 else 0
    risk_percent = round((risk_count / total) * 100, 1) if total > 0 else 0

    return render_template(
        "result.html",
        total=total,
        safe=safe,
        risk=risk_count,
        average=average_score,
        safe_percent=safe_percent,
        risk_percent=risk_percent,
        safe_table=safe_students.to_html(
            classes="table table-striped",
            index=False
        ),
        risk_table=risk_students.to_html(
            classes="table table-striped",
            index=False
        )
    )


@app.route("/download_safe")
def download_safe():

    return send_file(
        os.path.join(REPORT_FOLDER, "safe_students.xlsx"),
        as_attachment=True
    )
@app.route("/student_report", methods=["POST"])
def student_report():

    stu_id = request.form["stu_id"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE stu_id=?",
        (stu_id,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:
     return render_template("student_not_found.html")
    return render_template(
        "student_report.html",
        student=student
    )
@app.route("/send_emails")
@app.route("/send_emails")
def send_emails():

    risk_file = os.path.join(REPORT_FOLDER, "risk_students.xlsx")

    data = pd.read_excel(risk_file)

    # Check whether EMAIL column exists
    if "EMAIL" not in data.columns:
        return {
            "status": "error",
            "message": "EMAIL column not found in uploaded Excel."
        }

    try:

        # Send all emails using one Gmail login
        send_emails_to_students(data)

        return {
            "status": "success",
            "message": "Emails sent successfully!"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

@app.route("/download_risk")
def download_risk():

    return send_file(
        os.path.join(REPORT_FOLDER, "risk_students.xlsx"),
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
