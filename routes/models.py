from flask import Blueprint, render_template, redirect, url_for, flash
from models import *
from flask_login import login_required, current_user

from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm

from routes.auth import bcrypt

def get_columns(model):
    return [
        column.name
        for column in model.__table__.columns
    ]

def get_field_args_for_fks(model):
    field_args = {}

    for prop in model.__mapper__.iterate_properties:
        if hasattr(prop, 'direction'):
            rel_name = prop.key
            rel_model = prop.mapper.class_

            # check if rel model has name attribute
            if hasattr(rel_model, 'name'):
                option_string = rel_model.name
                option_attr = 'name'
            else:
                option_string = rel_model.id
                option_attr = 'id'

            field_args[rel_name] = {
                'query_factory': lambda: rel_model.query.order_by(option_string),
                'get_label': option_attr
            }

    return field_args

def populate_obj_by_form(obj, form):
    form.populate_obj(obj)

    if obj.__class__ == User:
        raw_password = form.password.data
        obj.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

def commit_changes():
    try:
        db.session.commit()
        return True
    except Exception as e:
        error_message = str(e)
        print(error_message)
        error_message = error_message[
            error_message.index(')') + 2
            :
            error_message.index('[') - 1
        ]
        flash(error_message, 'error')
        return False

def create_crud_blueprint(name, model, db, url_prefix, template_prefix):
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    form_class = model_form(
        model,
        db_session=db.session,
        base_class=FlaskForm,
        field_args=get_field_args_for_fks(model)
    )

    # List view
    @bp.route('/')
    @login_required
    def index():
        if current_user.role_id != 1:
            return "Unauthorized.", 401
        
        items = model.query.order_by(model.id.desc()).all()
        columns = get_columns(model)
        return render_template(
            f'{template_prefix}/list.html',
            items=items,
            model_name=name.capitalize(),
            columns=columns,
            used_models=used_models
        )

    # # Detail view
    # @login_required
    # @bp.route('/<int:id>')
    # def detail(id):
        # if current_user.role_id != 1:
        #     return "Unauthorized.", 401
    #     item = model.query.get_or_404(id)
    #     return render_template(
    #         f'{template_prefix}/detail.html',
    #         item=item,
    #         item_title=item.name,
    #         model_name=name.capitalize()
    #     )

    # Create view
    @login_required
    @bp.route('/create', methods=('GET', 'POST'))
    def create():
        if current_user.role_id != 1:
            return "Unauthorized.", 401
        
        form = form_class()
        if form.validate_on_submit():
            obj = model()
            populate_obj_by_form(obj, form)

            db.session.add(obj)

            success = commit_changes()
            if not success:
                return redirect(url_for(f'{name}.create'))

            return redirect(url_for(f'{name}.index'))
        
        return render_template(
            f'{template_prefix}/form.html',
            form=form,
            action="Create",
            title=name.capitalize(),
            cancel_url=url_for(f'{name}.index'),
            used_models=used_models
        )

    # Edit view
    @login_required
    @bp.route('/<int:id>/edit', methods=('GET', 'POST'))
    def edit(id):
        if current_user.role_id != 1:
            return "Unauthorized.", 401
        
        obj = model.query.get_or_404(id)
        form = form_class(obj=obj)

        if form.validate_on_submit():
            populate_obj_by_form(obj, form)
            
            success = commit_changes()
            if not success:
                return redirect(url_for(f'{name}.edit', id=id))
            
            return redirect(url_for(f'{name}.index'))
        
        return render_template(
            f'{template_prefix}/form.html',
            form=form,
            action="Edit",
            title=name.capitalize(),
            cancel_url=url_for(f'{name}.index'),
            used_models=used_models
        )

    # Delete view
    @login_required
    @bp.route('/<int:id>/delete')
    def delete(id):
        if current_user.role_id != 1:
            return "Unauthorized.", 401
        
        obj = model.query.get_or_404(id)
        db.session.delete(obj)

        commit_changes()
        return redirect(url_for(f'{name}.index'))

    return bp

used_models = [
    Professor,
    Student,
    Admin,
    Lecture,
    TimeProfessor,
    LectureProfessor,
    LectureStudent,
    Role,
    User,
    Classroom,
    LectureClassroom,
    Year,
    Day,
    Hour
]

models_routes = [
    create_crud_blueprint(
        name=model.__name__.lower(),
        model=model,
        db=db,
        url_prefix=f'/table/{model.__name__.lower()}',
        template_prefix='tables'
    )

    # for model in db.Model._decl_class_registry.values()
    # if issubclass(model, db.Model) or model is db.Model
    for model in used_models
]

model_bp = Blueprint("model", __name__, url_prefix="/tables")

@model_bp.route("/")
def tables():
    if current_user.role_id != 1:
        return "Unauthorized.", 401
    
    return render_template(
        "tables/table_editor_base.html",
        used_models=used_models
    )