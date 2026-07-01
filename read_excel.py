import pandas as pd

data = pd.read_excel("students.xlsx")

print(data)

print("Average Marks:", data["MARKS"].mean())
print("Average Attendance:", data["ATTEND"].mean())

print("\nStudents with Attendance below 75")

low_attendance = data[data["ATTEND"] < 75]
print(low_attendance)

# Performance Prediction

def performance(attend, marks):

    if attend >= 75 and marks >= 75:
        return "High"

    elif attend >= 60 and marks >= 50:
        return "Average"

    else:
        return "Low"

data["PERFORMANCE"] = data.apply(
    lambda row: performance(row["ATTEND"], row["MARKS"]),
    axis=1
)

print("\nStudent Performance")
print(data)
def risk(attend, marks):

    if attend < 50 or marks < 40:
        return "High Risk"

    elif attend < 75 or marks < 60:
        return "Medium Risk"

    else:
        return "Low Risk"

data["RISK"] = data.apply(
    lambda row: risk(row["ATTEND"], row["MARKS"]),
    axis=1
)

print("\nStudent Risk Analysis")
print(data)

print("\nPROJECT SUMMARY")

print("Total Students:", len(data))

print("High Performers:",
      len(data[data["PERFORMANCE"] == "High"]))

print("Average Performers:",
      len(data[data["PERFORMANCE"] == "Average"]))

print("Low Performers:",
      len(data[data["PERFORMANCE"] == "Low"]))

print("High Risk Students:",
      len(data[data["RISK"] == "High Risk"]))

import matplotlib.pyplot as plt

performance_counts = data["PERFORMANCE"].value_counts()

plt.bar(performance_counts.index, performance_counts.values)

plt.title("Student Performance Analysis")
plt.xlabel("Performance")
plt.ylabel("Number of Students")

plt.show()
