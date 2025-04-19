from flask import Flask, render_template, Response, request, redirect
from flask_login import LoginManager, login_required, current_user
from config import Config
# from flask_wtf.csrf import CSRFProtect

from models import User

# routes
from routes.models import *
from routes.auth import *
from routes.proftime import *
from routes.week_schedual import *


app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.globals['getattr'] = getattr

# csrf = CSRFProtect(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    # return User.query.get(int(user_id))
    return db.session.get(User, int(user_id))

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(model_bp)
for routes in models_routes:
    app.register_blueprint(routes)
app.register_blueprint(proftime_bp)
app.register_blueprint(weekschedual_bp)

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect("/week_program")
    
    return redirect("/login")


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)