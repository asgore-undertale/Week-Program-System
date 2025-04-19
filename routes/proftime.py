from flask import render_template, request, Blueprint
from flask_login import login_required, current_user

from pyscripts.table_builder import build_time_table_html_content
from models import *

proftime_bp = Blueprint("proftime", __name__)

@proftime_bp.route("/get_professor_time_table")
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

@proftime_bp.route("/professor_time")
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

@proftime_bp.route("/professor_time", methods=["POST"])
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