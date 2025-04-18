from flask import Blueprint, render_template, redirect, url_for
from models import *
from flask_login import login_required, current_user

from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from sqlalchemy.orm import class_mapper


def get_columns(model):
    return [
        column.name
        for column in model.__table__.columns
    ]

def get_field_args_for_fks(model):
    field_args = {}

    for prop in class_mapper(model).iterate_properties:
        if hasattr(prop, 'direction'):
            rel_name = prop.key
            rel_model = prop.mapper.class_

            field_args[rel_name] = {
                'query_factory': lambda: rel_model.query.order_by(rel_model.name),
                'get_label': 'name'
            }

    return field_args

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
            form.populate_obj(obj)
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for(f'{name}.index'))
        
        return render_template(
            f'{template_prefix}/form.html',
            form=form,
            action="Create",
            title=name.capitalize(),
            cancel_url=url_for(f'{name}.index')
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
            form.populate_obj(obj)
            db.session.commit()
            return redirect(url_for(f'{name}.index'))
        
        return render_template(
            f'{template_prefix}/form.html',
            form=form,
            action="Edit",
            title=name.capitalize(),
            cancel_url=url_for(f'{name}.index')
        )

    # Delete view
    @login_required
    @bp.route('/<int:id>/delete')
    def delete(id):
        if current_user.role_id != 1:
            return "Unauthorized.", 401
        
        obj = model.query.get_or_404(id)
        db.session.delete(obj)
        db.session.commit()
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
    