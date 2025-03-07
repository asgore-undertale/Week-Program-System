from flask import Flask, render_template#, redirect #, url_for, jsonify
from week_builder_script import build_week, combine_sequenced_lectures, tableize_combined_week_by_year
import json
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/build_week_program", methods=["POST"])
def build_week_program():
    week_program = build_week()

    with open("Databases/week_program.json", "w") as f:
        json.dump(week_program, f, indent=4)

    week_program_combined = combine_sequenced_lectures(week_program)
    tableized_week_program = tableize_combined_week_by_year(week_program_combined)

    with open("Databases/week_program_tableized.json", "w") as f:
        json.dump(tableized_week_program, f, indent=4)

    return {
        "status": 200,
        "message": "Week program built successfully."
    }

@app.route("/get_tableized_week_program", methods=["GET"])
def get_week_program():
    with open("Databases/week_program_tableized.json", "r") as f:
        tableized_week_program = json.load(f)
    
    # return render_template("index.html", week_program=week_program)
    # return redirect("/")
    # return week_program
    return app.response_class( # to remove key sorting
        response=json.dumps(tableized_week_program, ensure_ascii=False, indent=4, sort_keys=False),
        status=200,
        mimetype="application/json"
    )

@app.route("/get_week_program", methods=["GET"])
def get_week_program():
    with open("Databases/week_program.json", "r") as f:
        week_program = json.load(f)
    
    return app.response_class(
        response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
        status=200,
        mimetype="application/json"
    )

if __name__ == '__main__':
    app.run(debug=True)