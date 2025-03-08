from flask import Flask, render_template, Response, request#, redirect #, url_for, jsonify
from week_builder_script import *
import json
import os
from io import BytesIO

app = Flask(__name__)

# @app.route("/")
# def home():
#     return render_template("index.html")

@app.route("/week_program")
def week_program():
    students_number = request.args.get('students_number', type=str)
    professors_numbers = request.args.getlist('professors_numbers')

    professors_numbers = "&".join(map(
        lambda x: "professors_numbers=" + x,
        professors_numbers
    ))

    return render_template("week_program.html", students_number=students_number, professors_numbers=professors_numbers)

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
    professors_numbers = request.args.getlist('professors_numbers')
    students_number = request.args.get('students_number', type=str)

    # if professors_numbers == "None":
    #     professors_numbers = None
    if students_number == "None":
        students_number = None

    if not os.path.exists("Databases/week_program.json"):
        return {
            "status": 400,
            "message": "Week program not generated. Use /generate_week_program to generate it."
        }

    with open("Databases/week_program.json", "r") as f:
        week_program = json.load(f)
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


if __name__ == '__main__':
    app.run(debug=True)