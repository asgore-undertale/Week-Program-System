from flask import Flask, render_template, Response, request#, redirect #, url_for, jsonify
from pyscripts.week_generator import *
from pyscripts.table_builder import *
import json
import os
from io import BytesIO

app = Flask(__name__)

def get_prof_id_by_number(cursor, professors_number):
    professors = cursor.execute("SELECT * FROM ProfessorTb").fetchall()

    for prof in professors:
        if prof[1] == professors_number:
            return prof[0]
    else:
        return None

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    return render_template("login.html")

@app.route("/professor_time")
def professor_time():
    conn = sqlite3.connect("databases/UniversityDb.db")
    cursor = conn.cursor()

    professors = cursor.execute("SELECT * FROM ProfessorTb").fetchall()
    # professors_time = cursor.execute("SELECT * FROM TimeProfessorTb").fetchall()

    professors_number = request.args.get('professors_number', type=str)

    professors.sort(key=lambda x: x[2])

    for prof in professors:
        if prof[1] == professors_number:
            professor_name = prof[2]
            break
    else:
        professor_name = None

    return render_template(
        "professor_time.html",
        professors_number=professors_number,
        professor_name=professor_name,
        professors=professors,
    )

@app.route("/get_professor_time_table")
def get_professor_time_table():
    professors_number = request.args.get('professors_number', type=str)

    conn = sqlite3.connect("databases/UniversityDb.db")
    cursor = conn.cursor()

    professor_id = get_prof_id_by_number(cursor, professors_number)

    if professor_id is None:
        return {"error": "Professor not found."}, 400

    professors_time = cursor.execute("SELECT * FROM TimeProfessorTb WHERE ProfessorId = ?", (professor_id,)).fetchall()

    # return app.response_class( # to remove key sorting
    #     response=json.dumps(professors_time, ensure_ascii=False, indent=4, sort_keys=False),
    #     status=200,
    #     mimetype="application/json"
    # )
    html_string = build_time_table_html_content(professors_time)

    return html_string

@app.route("/professor_time", methods=["POST"])
def save_professor_time():
    json_data = request.get_json()

    if not json_data or not len(json_data):
        return {"error": "Invalid JSON data"}, 400

    try:
        professors_number = json_data[0][0]
    except:
        return {"error": "No prof number."}, 400

    conn = sqlite3.connect("databases/UniversityDb.db")
    cursor = conn.cursor()

    professor_id = get_prof_id_by_number(cursor, professors_number)

    if professor_id is None:
        return {"error": "Professor not found."}, 400

    json_data = list(map(
        lambda x: (professor_id, x[1], x[2]),
        json_data
    ))

    cursor.execute("DELETE FROM TimeProfessorTb WHERE professorId = ?", (professor_id,))
    cursor.executemany("INSERT OR IGNORE INTO TimeProfessorTb (ProfessorId, Hour, Day) VALUES (?, ?, ?)", json_data)
    conn.commit()
    conn.close()

    return {"message": "Data saved successfully"}, 200

@app.route("/week_program")
def week_program():
    students_number = request.args.get('students_number', type=str)
    professors_numbers = request.args.getlist('professors_numbers')

    professors_numbers = "&".join(map(
        lambda x: "professors_numbers=" + x,
        professors_numbers
    ))

    conn = sqlite3.connect("databases/UniversityDb.db")
    cursor = conn.cursor()

    professors = cursor.execute("SELECT * FROM ProfessorTb").fetchall()

    # role = cursor.execute("SELECT * FROM UserTb WHERE student_id = ?", (student_id,)).fetchone()
    # role = "admin"
    # role = "professor"
    role = "student"

    return render_template(
        "week_program.html", 
        students_number=students_number, 
        professors_numbers=professors_numbers, 
        professors=professors,
        role=role
    )

@app.route("/generate_week_program", methods=["POST"])
def generate_week_program():
    week_program = build_week()

    # return app.response_class( # to remove key sorting
    #     response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
    #     status=200,
    #     mimetype="application/json"
    # )

    with open("databases/week_program.json", "w") as f:
        json.dump(week_program, f, indent=4)

    return {
        "status": 200,
        "message": "Week program built successfully."
    }, 200

# @app.route("/get_week_program/student_id/<int:student_id>", methods=["GET"])
# def get_json_week_program(student_id):

@app.route("/get_week_program", methods=["GET"])
def get_week_program():
    data_type = request.args.get('type', type=str)
    do_download = request.args.get('download', type=bool)
    professors_numbers = request.args.getlist('professors_numbers')
    students_number = request.args.get('students_number', type=str)

    # if professors_numbers == "None":
    #     professors_numbers = None
    if students_number == "None":
        students_number = None

    if not os.path.exists("databases/week_program.json"):
        return {
            "status": 400,
            "message": "Week program not generated."
        }, 400

    with open("databases/week_program.json", "r") as f:
        json_data = f.read()
        week_program = json.loads(json_data)
        # for day in week_program:
        #     week_program[day] = {
        #         int(k): v
        #         for k, v in week_program[day].items()
        #     }
    
    for day in week_program:
        for hour in week_program[day]:
            for l in range(len(week_program[day][hour])-1, -1, -1):
                lecture = week_program[day][hour][l]
                if not len(professors_numbers) and students_number is None:
                    continue

                if professors_numbers is not None and students_number is None and lecture["professorNumber"] in professors_numbers:
                    continue

                if students_number is not None and not len(professors_numbers) and students_number in lecture["studentNumbers"]:
                    continue

                if professors_numbers is not None and students_number is not None and lecture["professorNumber"] in professors_numbers and students_number in lecture["studentNumbers"]:
                    continue

                week_program[day][hour].pop(l)

    if data_type == "json":
        if do_download == True:
            response = Response(json_data)
            response.headers["Content-Type"] = "application/json"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.json"

            return response
        else:
            return app.response_class( # to remove key sorting
                response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
                status=200,
                mimetype="application/json"
            )

    elif data_type == "html":
        tableized_week_program = tableize_combined_week_by_year(
            combine_sequenced_lectures(
                week_program
            )
        )

        html_string = build_week_html_content(tableized_week_program)

        if do_download == True:
            response = Response(html_string)
            response.headers["Content-Type"] = "text/html"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.html"

            return response
        else:
            return html_string

    elif data_type == "excel":
        if do_download == True:
            tableized_week_program = tableize_combined_week_by_year(
                combine_sequenced_lectures(
                    week_program
                )
            )

            wb = build_week_excel_file(tableized_week_program)

            excel_buffer = BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)

            response = Response(excel_buffer)
            response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.xlsx"

            return response

    elif data_type == "pdf":
        pass

    elif data_type == "png":
        pass


if __name__ == '__main__':
    app.run(debug=True)