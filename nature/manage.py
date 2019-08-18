import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from nature.auth import login_required
from nature.db import get_db

bp = Blueprint('manage', __name__, url_prefix='/my')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/index')
@bp.route('/')
@login_required
def index():
    return render_template('manage/index.html')

@bp.route('/info')
def person():
    db = get_db()
    return render_template('manage/person.html')

@bp.route('/fee')
def pay():
    db = get_db()
    return render_template('manage/fee.html')

@bp.route('/submit')
def submit():
    db = get_db()
    return render_template('manage/submit.html')

@bp.route('/registration')
def update_registration():
    db = get_db()
    return render_template('manage/registration.html')
