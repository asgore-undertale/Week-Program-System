from flask import render_template, request, Blueprint, Response
from flask_login import login_required, current_user

from io import BytesIO
import json
import os
import copy

from pyscripts.week_generator import *
from pyscripts.table_builder import *
from models import *

weekschedual_bp = Blueprint("weekschedual", __name__)

@weekschedual_bp.route("/week_program")
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

@weekschedual_bp.route("/generate_week_program", methods=["POST"])
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

    return Response(
        response=json.dumps( # to remove key sorting
            result,
            ensure_ascii=False,
            indent=4,
            sort_keys=False
        ),
        status=200,
        mimetype='application/json'
    )

@weekschedual_bp.route("/remove_week_program", methods=["POST"])
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

# @weekschedual_bp.route("/get_week_program/student_id/<int:student_id>", methods=["GET"])
# def get_json_week_program(student_id):

@weekschedual_bp.route("/get_week_program")
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

@weekschedual_bp.route("/build_week_program", methods=["POST"])
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


# @weekschedual_bp.route("/download_week_program")
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

@weekschedual_bp.route("/confirm_week_program", methods=["POST"])
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
        week_program = remove_week_program_sensitive_info(week_program)

        if do_download == True:
            response = Response(
                json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False) # to use filters
            )
            response.headers["Content-Type"] = "application/json"
            response.headers["Content-Disposition"] = "attachment; filename=week_program.json"

            return response
        else:
            return Response(
                response=json.dumps( # to remove key sorting
                    week_program,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=False
                ),
                status=200,
                mimetype='application/json'
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
        # tableized_week_program = tableize_combined_week_by_year(
        #     combine_sequenced_lectures(
        #         week_program
        #     )
        # )

        # years = [
        #     year.name
        #     for year in db.session.query(Year).all()
        # ]

        # html_string = build_week_html_content(tableized_week_program, years)

        # # pdf_bytes = HTML(string=html_string).write_pdf()
        # pdf_bytes = auto_fit_pdf(html_string)

        # response = Response(pdf_bytes)
        # response.headers['Content-Type'] = 'application/pdf'
        # response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        # return response
        pass

    elif data_type == "png":
        pass

# def auto_fit_pdf(html_string,
#                  target_page_width_mm=297,   # A4 landscape width
#                  target_page_height_mm=210,  # A4 landscape height
#                  margin_mm=10,
#                  render_page_size_mm=1000):  # BIG rendering canvas
#     """
#     Renders a PDF from HTML, scaling the page to fit everything into a single standard page.
#     """
#     # Create a huge page to render the entire content without wrapping/pagination
#     css_large = CSS(string=f'''
#         @page large {{
#             size: {render_page_size_mm}mm {render_page_size_mm}mm;
#             margin: {margin_mm}mm;
#         }}
#         body {{ page: large; }}
#     ''')
#     doc = HTML(string=html_string)
#     layout = doc.render(stylesheets=[css_large])

#     # Get content dimensions (from the first page box)
#     page = layout.pages[0]
#     # fallback in case no anchors: use page._page_box content size
#     box = page._page_box
#     content_width_px = box.width
#     content_height_px = box.height

#     # Convert page size and margin to pixels (WeasyPrint uses 96 dpi)
#     mm_to_px = 96 / 25.4
#     available_width_px = (target_page_width_mm - 2 * margin_mm) * mm_to_px
#     available_height_px = (target_page_height_mm - 2 * margin_mm) * mm_to_px

#     # Calculate the zoom factor
#     zoom_x = available_width_px / content_width_px
#     zoom_y = available_height_px / content_height_px
#     zoom = min(zoom_x, zoom_y, 1.0)

#     # Apply zoom and output final PDF with real page size
#     css_target = CSS(string=f'''
#         @page real {{
#             size: {target_page_width_mm / zoom}mm {target_page_height_mm / zoom}mm;
#             margin: {margin_mm}mm;
#         }}
#         body {{ page: real; }}
#     ''')
#     pdf = doc.write_pdf(stylesheets=[css_target], zoom=zoom)
#     return pdf

# @weekschedual_bp.route("/week_editor")
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