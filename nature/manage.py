import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from nature.auth import login_required
from nature.db import get_db

bp = Blueprint('manage', __name__, url_prefix='/admin')

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
    db = get_db()
    return render_template('manage/index.html')

