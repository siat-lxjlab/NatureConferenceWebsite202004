import sys
import functools
import re
import random
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from nature.db import get_db
from nature.mail import send_verify_code

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
            error = 'Two passwords are inconsistent.'
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
        elif db.execute(
            'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'Email {} is already registered.'.format(email)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password, name, email, phone, workplace, title, gender, requirement_baby_care, requirement_simultaneous_transmission) VALUES(?,?,?,?,?,?,?,?,?,?)',
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

@bp.route('/reset', methods=('GET', 'POST'))
def reset():
    error = None
    if request.method == 'GET':
        session.clear()
        email_address = request.args.get('target')
        if not email_address:
            return render_template('auth/reset.html')

         # confirm the email format
        email_pattern = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$'       
        if not re.match(email_pattern, email_address):
            error = 'Email format is not right.'
            return json.dumps({'code':2, 'content':error})
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email_address,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email address.'
            return json.dumps({'code':2, 'content':error})
        else:
            code = ''
            for i in range(6):
                code += str(random.randint(1, 9))        
            send_verify_code(email_address, code)
            error = 'Verification code has been sent'
        session.clear()
        session['code'] = code
        session['email'] = email_address
        return json.dumps({"code":1, 'content':error})
    if request.method == 'POST':
        error = None
        code = session.get('code')
        print(code)
        if code is None:
            error = "Verification code is invalid. Resend it."
            return json.dumps({'code':2, 'content':error})
        email_ = request.form['email']
        pass_ = request.form['password']
        if pass_ == session['code'] and session['email'] == email_:
            return json.dumps({'code':1, 'content':"success"})
        error = 'Verification code is not correct.'
        return json.dumps({'code':2, 'content':error})



@bp.route('/change', methods=('GET', 'POST'))
def change():
    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template("auth/change_pass.html")        
    if request.method == 'POST':
        error = None
        repassword = request.form['repassword']
        password = request.form['password']
        if password == repassword:
            db = get_db()
            db.execute(
                'UPDATE user SET password = ? WHERE email = ?',
                (generate_password_hash(password), email)
            )
            db.commit()
            return redirect(url_for('auth.login'))
        else:
            error = "Two passwords are different"
            flash(error)
            return render_template("auth/change_pass.html")  
        

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
