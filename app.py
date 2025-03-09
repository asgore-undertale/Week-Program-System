from flask import Flask, flash, render_template, Response, request, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
# from flask_wtf.csrf import CSRFProtect

from pyscripts.week_generator import *
from pyscripts.table_builder import *
from config import Config
from models import *

import json
import os
from io import BytesIO


app = Flask(__name__)
app.config.from_object(Config)

# csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db.init_app(app)

with app.app_context():
    db.create_all()
    seed_data(app, bcrypt)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    professors_time = TimeProfessor.query.filter_by(professor_id=professor_id).all()

    html_string = build_time_table_html_content(professors_time)

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

    TimeProfessor.query.filter_by(professor_id=professor_id).delete()
    db.session.add_all(map(lambda x: TimeProfessor(professor_id=professor_id, hour=x[1], day=x[2]), json_data))
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

    # role = Role.query.filter_by(id=current_user.role_id).first().name

    return render_template(
        "week_program.html", 
        students_number=students_number, 
        professors_numbers=professors_numbers, 
        professors=professors,
        # role=role
        # role_id=current_user.role_id
        current_user=current_user
    )

@app.route("/generate_week_program", methods=["POST"])
@login_required
def generate_week_program():
    week_program = build_week()

    # if Role.query.filter_by(id=current_user.role_id).first().name != "Admin":
    if current_user.role_id != 1:
        return {
            "message": "Unauthorized."
        }, 401

    with open("databases/week_program.json", "w") as f:
        json.dump(week_program, f, indent=4)

    return {
        "message": "Week program built successfully."
    }, 200

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
    do_download = request.args.get('download', type=bool)
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

                if professors_numbers is not None and students_number is None and lecture["professorNumber"] in professors_numbers:
                    continue

                if students_number is not None and not len(professors_numbers) and students_number in lecture["studentNumbers"]:
                    continue

                if professors_numbers is not None and students_number is not None and lecture["professorNumber"] in professors_numbers and students_number in lecture["studentNumbers"]:
                    continue

                week_program[day][hour].pop(l)

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