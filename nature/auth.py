import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from nature.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        workplace = request.form['workplace']
        title = request.form['title']
        repassword = request.form['repassword']
        gender = request.form['gender']
        requirements = request.form.getlist('requirement')
        baby_care = False
        translate = False
        if len(requirements) == 0:
            pass
        elif len(requirements) == 1:        
            if requirements[0] == "1":
                baby_care = True
            else:
                translate = True
        else:
            baby_care = True
            translate = True        

        db = get_db()
        error = None

        # confirm the email format
        email_pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'
        if not username:
            error = 'Username is required.'
        elif not (len(password) > 5):
            error = 'At least 6 characters.'
        elif not (password == repassword):
            error = 'Two passwords is inconsistent.'
        elif not name:
            error = 'Name is required.'
        elif not re.match(email_pattern, email):
            error = 'Email format is not right.'
        elif not workplace:
            error = 'Workplace is required.'
        elif not (title != "0"):
            error = 'Title is required.'
        elif not (gender != "0"):
            error = 'Gender is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, name, email, phone, workplace, title, gender, requirement_baby_care, requirement_translate) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (username, generate_password_hash(password), name, email, phone, workplace, title, gender, baby_care, translate)
            )
            db.commit()
            return redirect(url_for('auth.login'))
            
        flash(error)
    
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('manage.index'))
        
        flash(error)
    
    return render_template('auth/login.html') 


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
