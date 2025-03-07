from flask import Flask, render_template, Response, request#, redirect #, url_for, jsonify
from week_builder_script import *
import json
import os
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/week_program")
def week_program():
    students_number = request.args.get('students_number', type=str)
    professors_number = request.args.get('professors_number', type=str)

    return render_template("week_program.html", students_number=students_number, professors_number=professors_number)

@app.route("/generate_week_program", methods=["POST"])
def generate_week_program():
    week_program = build_week()

    # return app.response_class( # to remove key sorting
    #     response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
    #     status=200,
    #     mimetype="application/json"
    # )

    with open("Databases/week_program.json", "w") as f:
        json.dump(week_program, f, indent=4)

    # with open("Databases/week_program_tableized.json", "w") as f:
    #     json.dump(tableized_week_program, f, indent=4)

    return {
        "status": 200,
        "message": "Week program built successfully."
    }

# @app.route("/get_week_program/student_id/<int:student_id>", methods=["GET"])
# def get_json_week_program(student_id):

@app.route("/get_week_program", methods=["GET"])
def get_week_program():
    data_type = request.args.get('type', type=str)
    do_download = request.args.get('download', type=bool)
    professors_number = request.args.get('professors_number', type=str)
    students_number = request.args.get('students_number', type=str)

    if professors_number == "None":
        professors_number = None
    if students_number == "None":
        students_number = None

    if not os.path.exists("Databases/week_program.json"):
        return {
            "status": 400,
            "message": "Week program not generated. Use /generate_week_program to generate it."
        }

    with open("Databases/week_program.json", "r") as f:
        week_program = json.load(f)
        for day in week_program:
            week_program[day] = {
                int(k): v
                for k, v in week_program[day].items()
            }

    print(week_program)
    week_program3 = build_week()
    print(week_program3)
    print(week_program3 == week_program)
    
    for day in week_program:
        for hour in week_program[day]:
            for l in range(len(week_program[day][hour])-1, -1, -1):
                lecture = week_program[day][hour][l]
                if professors_number is None and students_number is None:
                    continue

                if professors_number is not None and students_number is None and professors_number == lecture["professorNumber"]:
                    continue

                if students_number is not None and professors_number is None and students_number in lecture["studentNumbers"]:
                    continue

                if professors_number is not None and students_number is not None and professors_number == lecture["professorNumber"] and students_number in lecture["studentNumbers"]:
                    continue

                week_program[day][hour].pop(l)

    if data_type == "json":
        if do_download == True:
            response = Response(json_data)
            response.headers["Content-Type"] = "application/json"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.json"

            return response
        else:
            # return render_template("index.html", week_program=week_program)
            # return redirect("/")
            # return week_program
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


if __name__ == '__main__':
    app.run(debug=True)