from flask import Flask, render_template#, redirect #, url_for, jsonify
from week_builder_script import build_week, combine_sequenced_lectures
import json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/build_week_program", methods=["GET"])
def build_week_program():
    week_program = build_week()

    week_program = combine_sequenced_lectures(week_program)     ###############################
    
    # return render_template("index.html", week_program=week_program)
    # return redirect("/")
    # return week_program
    return app.response_class( # to remove key sorting
        response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
        status=200,
        mimetype="application/json"
    )

# @app.route("/combine_sequenced_lectures", methods=["GET"])
# def combine_sequenced_lectures():
#     week_program = build_week()
    
#     return app.response_class( # to remove key sorting
#         response=json.dumps(week_program, ensure_ascii=False, indent=4, sort_keys=False),
#         status=200,
#         mimetype="application/json"
#     )

if __name__ == '__main__':
    app.run(debug=True)