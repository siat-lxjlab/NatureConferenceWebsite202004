import functools
import re
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, session
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


@bp.route('/info', methods=('GET', 'POST'))
@login_required
def person():
    user_id = session.get('user_id')
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        workplace = request.form['workplace']
        title = request.form['title']
        db = get_db()
        error = None

        # confirm the email format
        email_pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
        if not username:
            error = 'Username is required.'
        elif not name:
            error = 'Name is required.'
        elif not re.match(email_pattern, email):
            error = 'Email format is not right.'
        elif not (len(phone) == 11 or len(phone) == 10):
            error = 'Phone number is not right.'
        elif not workplace:
            error = 'Workplace is required.'
        elif not (title != "0"):
            error = 'Title is required.'
        elif username == g.user["username"]:
            error = None  
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)      
        else:
            error = None

        if error is None:
            db.execute(
                'UPDATE user SET username = ?, name = ?, email = ?, phone = ?, workplace = ?, title = ?' 
                ' WHERE id = ?',
                (username, name, email, phone, workplace, title, user_id)
            )
            db.commit()
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()
            return render_template('manage/person.html')

        flash(error)
    return render_template('manage/person.html')


@bp.route('/fee', methods=('GET', 'POST'))
@login_required
def pay():
    user_id = session.get('user_id')
    if request.method == 'POST':
        serial = request.form['serial']
        title = request.form['title']
        db = get_db()
        error = None

        if not title:
            error = '请填写发票抬头'
        elif not serial:
            error = '请填写纳税人识别号' 
        else:
            error = None

        if error is None:
            error = "提交成功"
            db.execute(
                'UPDATE invoice SET invoice_title = ?, serial_num = ?' 
                ' WHERE user_id = ?',
                (title, serial, user_id)
            )
            db.commit()
        flash(error)
        return render_template('manage/fee.html')
    if request.method == 'GET':
        return render_template('manage/fee.html')


@bp.route('/submit')
@login_required
def submit():
    user_id = session.get('user_id')
    db = get_db()
    user = db.execute(
        'SELECT paid FROM user WHERE id = ?', (user_id,)
    ).fetchone()
    if user["paid"] == "False":
        return redirect(url_for('manage.index'))
    
    abstract = db.execute(
        'SELECT id, filename, created, state FROM abstract WHERE user_id = ?', (user_id,)
    ).fetchone() 
    return render_template('manage/submit.html', abstract = abstract)


# @bp.route('/registration')
# @login_required
# def update_registration():
#     db = get_db()
#     # db.execute()
#     return render_template('manage/registration.html')
