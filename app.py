from flask import Flask, flash, render_template, Response, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from flask_bcrypt import Bcrypt
# from flask_wtf.csrf import CSRFProtect

from pyscripts.week_generator import *
from pyscripts.table_builder import *
from models import *

import json
import os
from io import BytesIO
import copy


app = Flask(__name__)
app.config.from_object(Config)

# csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # return User.query.get(int(user_id))
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect("/week_program")
    
    return redirect("/login")

### =================================================================

@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect("/week_program")
    
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def process_login():
    if current_user.is_authenticated:
        return {
           "Already logged in." 
        }, 400
    
    usernumber = request.form['usernumber']
    password = request.form['password']

    user = User.query.filter_by(number=usernumber).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        
        # role = Role.query.filter_by(id=user.role_id).first().name

        # if role == "Student":
        if user.role_id == 3:
            return redirect("/week_program?students_number=" + user.number)
        else:
            return redirect("/week_program")

    # message = "Invalid username or password"
    flash('Invalid username or password!', 'error')

    return redirect("/login")

@app.route("/logout")
@login_required
def process_logout():
    logout_user()
    return redirect('/login')

### =================================================================

@app.route("/get_professor_time_table")
@login_required
def get_professor_time_table():
    professors_number = request.args.get('professors_number', type=str)

    if current_user.role_id != 1:
        if not (current_user.role_id == 2 and current_user.number == professors_number):
            return "Unauthorized.", 401

    professor = Professor.query.filter_by(number=professors_number).first()

    if professor is None:
        return "Professor not found.", 400
    
    professor_id = professor.id

    # professors_time = TimeProfessor.query.filter_by(professor_id=professor_id).all()
    professors_time = (
        db.session.query(
            TimeProfessor.id, 
            Day.name.label("day_name"),  # Alias for Day's name column
            Hour.name.label("hour_name") # Alias for Hour's name column
        )
        .join(Day, Day.id == TimeProfessor.day_id)
        .join(Hour, Hour.id == TimeProfessor.hour_id)
        .filter(TimeProfessor.professor_id == professor_id)
        .all()
    )

    professors_time_dict = [
        {
            "hour": item.hour_name,
            "day": item.day_name
        }
        for item in professors_time
    ]
    hours = [
        hour.name
        for hour in db.session.query(Hour).all()
    ]
    days = [
        day.name
        for day in db.session.query(Day).all()
    ]

    html_string = build_time_table_html_content(professors_time_dict, days, hours)

    return html_string

@app.route("/professor_time")
@login_required
def professor_time():
    professors_number = request.args.get('professors_number', type=str)

    if current_user.role_id != 1:
        if not (current_user.role_id == 2 and current_user.number == professors_number):
            return "Unauthorized.", 401

    professors = Professor.query.order_by(Professor.name).all()
    
    professor = next((prof for prof in professors if prof.number == professors_number), None)
    professor_name = professor.name if professor else None
    
    return render_template(
        "professor_time.html",
        professors_number=professors_number,
        professor_name=professor_name,
        professors=professors,
        current_user=current_user
    )

@app.route("/professor_time", methods=["POST"])
@login_required
def save_professor_time():
    json_data = request.get_json()

    if not json_data or not len(json_data):
        return {"message": "Invalid JSON data"}, 400

    try:
        professors_number = json_data[0][0]
    except:
        return {"message": "No prof number."}, 400

    if current_user.role_id != 1:
        if not (current_user.role_id == 2 and current_user.number == professors_number):
            return {"message": "Unauthorized."}, 401

    professor = Professor.query.filter_by(number=professors_number).first()

    if professor is None:
        return {"message": "Professor not found."}, 400

    professor_id = professor.id

    hours_dict = {
        str(hour.name): hour.id # str because of sending stringified json
        for hour in db.session.query(Hour).all()
    }
    days_dict = {
        str(day.name): day.id
        for day in db.session.query(Day).all()
    }

    TimeProfessor.query.filter_by(professor_id=professor_id).delete()
    db.session.add_all(map(lambda x: TimeProfessor(professor_id=professor_id, day_id=days_dict[x[1]], hour_id=hours_dict[x[2]]), json_data))
    db.session.commit()

    return {"message": "Data saved successfully"}, 200

### =================================================================

@app.route("/week_program")
@login_required
def week_program():
    students_number = request.args.get('students_number', type=str)
    professors_numbers = request.args.getlist('professors_numbers')

    if students_number and current_user.role_id != 1 and current_user.number != students_number:
    # if students_number and Role.query.filter_by(id=current_user.role_id).first().name != "Admin" and current_user.number != students_number:
        return "Unauthorized", 401

    professors_numbers = "&".join(map(
        lambda x: "professors_numbers=" + x,
        professors_numbers
    ))

    professors = Professor.query.order_by(Professor.name).all()

    if current_user.role_id == 1:
        detailed_lectures = get_detailed_lectures()
        detailed_lectures.sort(key=lambda x: x["name"])

        for i in range(len(detailed_lectures)):
            detailed_lectures[i] = get_fully_detailed_lecture(detailed_lectures[i])
    else:
        detailed_lectures = None

    if current_user.role_id == 1:
        classrooms = [
            {
                "id": classroom.id,
                "name": classroom.name,
                "capacity": classroom.capacity
            }
            for classroom in Classroom.query.order_by(Classroom.name).all()
        ]
        
    else:
        classrooms = None

    hours = [
        hour.name
        for hour in db.session.query(Hour).all()
    ]
    days = [
        day.name
        for day in db.session.query(Day).all()
    ]

    # role = Role.query.filter_by(id=current_user.role_id).first().name

    return render_template(
        "week_program.html", 
        students_number=students_number, 
        professors_numbers=professors_numbers, 
        professors=professors,
        lectures=detailed_lectures,
        classrooms=classrooms,
        days=days,
        hours=hours,
        # role=role
        # role_id=current_user.role_id
        current_user=current_user
    )

@app.route("/generate_week_program", methods=["POST"])
@login_required
def generate_week_program():
    # if Role.query.filter_by(id=current_user.role_id).first().name != "Admin":
    if current_user.role_id != 1:
        return {
            "message": "Unauthorized."
        }, 401

    data = request.get_json()

    if data is None:
        result = build_week()

    else:
        if "week_program" not in data:
            return {
                "message": "No week program data provided."
            }, 400
        if "detailed_lectures" not in data:
            return {
                "message": "No detailed lectures data provided."
            }, 400

        if data["week_program"] != None:
            week = {
                day: {
                    int(hour): value
                    for hour, value in hour_values.items()
                }
                for day, hour_values in data["week_program"].items()
            }

        result = build_week(
            week,
            copy.deepcopy(data["detailed_lectures"]),
        )

    if result["week_program"] is None:
        return {
            "message": "Failed to generate week program."
        }, 400
    
    # week_program = run_genetic()

    return app.response_class( # to remove key sorting
        response=json.dumps(result, ensure_ascii=False, indent=4, sort_keys=False),
        status=200,
        mimetype="application/json"
    )

@app.route("/remove_week_program", methods=["POST"])
@login_required
def remove_week_program():
    # if Role.query.filter_by(id=current_user.role_id).first().name != "Admin":
    if current_user.role_id != 1:
        return {
            "message": "Unauthorized."
        }, 401

    if os.path.exists("databases/week_program.json"):
        os.remove("databases/week_program.json")

        return {
            "message": "Week program removed successfully."
        }, 200
    else:
        return {
            "message": "Week program not found."
        }, 400

# @app.route("/get_week_program/student_id/<int:student_id>", methods=["GET"])
# def get_json_week_program(student_id):

@app.route("/get_week_program")
@login_required
def get_week_program():
    data_type = request.args.get('type', type=str)
    professors_numbers = request.args.getlist('professors_numbers')
    students_number = request.args.get('students_number', type=str)

    if students_number == "None":
        students_number = None

    if not os.path.exists("databases/week_program.json"):
        return {
            "message": "Week program not found."
        }, 400

    with open("databases/week_program.json", "r") as f:
        week_program = json.loads(f.read())
    
    for day in week_program:
        for hour in week_program[day]:
            for l in range(len(week_program[day][hour])-1, -1, -1):
                lecture = week_program[day][hour][l]
                if not len(professors_numbers) and students_number is None:
                    continue

                if professors_numbers is not None and students_number is None and lecture["professor"]["number"] in professors_numbers:
                    continue

                if students_number is not None and not len(professors_numbers) and students_number in lecture["studentNumbers"]:
                    continue

                if professors_numbers is not None and students_number is not None and lecture["professor"]["number"] in professors_numbers and students_number in lecture["studentNumbers"]:
                    continue

                week_program[day][hour].pop(l)

    return build_week_program_(week_program, data_type, False)

@app.route("/build_week_program", methods=["POST"])
@login_required
def build_week_program():
    # if current_user.role_id != 1:
    #     return {
    #         "message": "Unauthorized."
    #     }, 401
    
    data_type = request.args.get('type', type=str)
    do_download = request.args.get('download', type=bool)

    week_program = request.get_json()

    return build_week_program_(week_program, data_type, do_download)


# @app.route("/download_week_program")
# @login_required
# def download_week_program():
#     # if current_user.role_id != 1:
#     #     return {
#     #         "message": "Unauthorized."
#     #     }, 401
    
#     data_type = request.args.get('type', type=str)
#     do_download = request.args.get('download', type=bool)
#     professors_numbers = request.args.getlist('professors_numbers')
#     students_number = request.args.get('students_number', type=str)

#     week_program = get_week_program()

#     return build_week_program_(week_program, data_type, do_download)

@app.route("/confirm_week_program", methods=["POST"])
@login_required
def confirm_week_program():
    if current_user.role_id != 1:
        return {
            "message": "Unauthorized."
        }, 401
    
    week_program = request.get_json()

    with open("databases/week_program.json", "w") as f:
        json.dump(week_program, f, indent=4)

    return {
        "message": "Week program confirmed successfully."
    }, 200

def build_week_program_(week_program, data_type, do_download):
    if data_type == "json":
        if do_download == True:
            response = Response(
                json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False) # to use filters
            )
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

        years = [
            year.name
            for year in db.session.query(Year).all()
        ]

        html_string = build_week_html_content(tableized_week_program, years)

        if do_download == True:
            response = Response(html_string)
            response.headers["Content-Type"] = "text/html"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.html"

            return response
        else:
            return html_string

    elif data_type == "xlsx":
        # if do_download == True:
        tableized_week_program = tableize_combined_week_by_year(
            combine_sequenced_lectures(
                week_program
            )
        )

        years = [
            year.name
            for year in db.session.query(Year).all()
        ]

        wb = build_week_excel_file(tableized_week_program, years)

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


# @app.route("/week_editor")
# @login_required
# def week_editor():
#     if current_user.role_id != 1:
#         return "Unauthorized", 401
    
#     # lectures = Lecture.query.order_by(Lecture.name).all()
#     detailed_lectures = get_detailed_lectures()
#     detailed_lectures.sort(key=lambda x: x["name"])

#     for i in range(len(detailed_lectures)):
#         detailed_lectures[i] = get_fully_detailed_lecture(detailed_lectures[i])

#     return render_template(
#         "week_editor.html", 
#         lectures=detailed_lectures,
#         current_user=current_user
#     )

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)