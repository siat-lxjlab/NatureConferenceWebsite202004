import sys
import functools
import re
import random
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash

from nature.db import get_db


bp = Blueprint('admin', __name__, url_prefix='/root')


@bp.before_app_request
def load_logged_in_admin():
    admin_id = session.get('admin_id')

    if admin_id is None:
        g.admin = None
    else:
        g.admin = get_db().execute(
            'SELECT * FROM admin WHERE id = ?', (admin_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for('admin.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/login', methods=('GET', 'POST'))
@bp.route('/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        admin = db.execute(
            'SELECT * FROM admin WHERE username = ?', (username,)
        ).fetchone()

        if admin is None:
            error = 'Incorrect username.'
        elif not check_password_hash(admin['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['admin_id'] = admin['id']
            return redirect(url_for('admin.index'))
        flash(error)
    return render_template('root/login.html')


@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()

    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()

    invoices = db.execute(
        'SELECT * FROM invoice'
    ).fetchall()

    abstracts = db.execute(
        'SELECT * FROM abstract'
    ).fetchall()

    num_bc, num_st = 0, 0
    for user in users:
        if user["requirement_baby_care"] == 1:
            num_bc += 1
        if user["requirement_simultaneous_transmission"] == 1:
            num_st += 1

    return render_template('root/index.html', num_user=len(users), num_invoice=len(invoices), num_abstract=len(abstracts), num_bc=num_bc, num_st=num_st)


@bp.route('/guest', methods=('GET', 'POST'))
@login_required
def guest():
    db = get_db()
    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()
    return render_template('root/guest.html', users=users)


@bp.route('/abstract', methods=('GET', 'POST'))
@login_required
def abstract():
    db = get_db()
    abstracts_raw = db.execute(
        'SELECT * FROM abstract'
    ).fetchall()

    abstracts = list()
    for abstract in abstracts_raw:
        user = abstract["user_id"]
        name = db.execute(
            'SELECT * FROM user WHERE id = ?', (user,)
        ).fetchone()["name"]
        abstracts.append(dict(
            user_id=name, filename=abstract['filename'], id=abstract['id'], created=abstract['created'], state=abstract['state']))
    return render_template('root/abstract.html', abstracts=abstracts)


@bp.route('/abstract/yes/<int:id>', methods=('GET', 'POST'))
@login_required
def abstract_examine_yes(id):
    db = get_db()
    abstract = db.execute(
        'SELECT * FROM abstract WHERE id = ?', (id,)
    ).fetchone()

    if abstract is None:
        abort(404)  
    else:
        db.execute(
            'UPDATE abstract SET state = ? WHERE id = ?',
            (1, id)
        )
        db.commit()          
    return redirect(url_for('admin.abstract'))


@bp.route('/abstract/no/<int:id>', methods=('GET', 'POST'))
@login_required
def abstract_examine_no(id):
    db = get_db()
    abstract = db.execute(
        'SELECT * FROM abstract WHERE id = ?', (id,)
    ).fetchone()

    if abstract is None:
        abort(404)  
    else:
        db.execute(
            'UPDATE abstract SET state = ? WHERE id = ?',
            (2, id)
        )
        db.commit()          
    return redirect(url_for('admin.abstract'))


@bp.route('/paid/yes/<int:id>', methods=('GET', 'POST'))
@login_required
def pay_examine_yes(id):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (id,)
    ).fetchone()

    if user is None:
        abort(404)  
    else:
        db.execute(
            'UPDATE user SET paid = ? WHERE id = ?',
            ("True", id)
        )
        db.commit()   
        db.execute(
            "INSERT INTO invoice (user_id) VALUES( ? ) ", (id, )
        )       
        db.commit()   
    return redirect(url_for('admin.guest'))


@bp.route('/paid/no/<int:id>', methods=('GET', 'POST'))
@login_required
def pay_examine_no(id):
    print(type(id))
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (id, )
    ).fetchone()

    if user is None:
        abort(404)  
    else:
        db.execute(
            'UPDATE user SET paid = ? WHERE id = ?',
            ("False", id)
        )
        db.commit()        
        db.execute(
            "DELETE FROM invoice WHERE user_id = ? ", (id, )
        )       
        db.commit()     
    return redirect(url_for('admin.guest'))



@bp.route('/fee', methods=('GET', 'POST'))
@login_required
def fee():
    db = get_db()
    invoices = db.execute(
        'SELECT * FROM invoice'
    ).fetchall()
    invoices_data = list()
    for invoice in invoices:
        user = invoice["user_id"]
        name = db.execute(
            'SELECT * FROM user WHERE id = ?', (user,)
        ).fetchone()["name"]
        invoices_data.append(dict(user_id=name, created=invoice["created"], invoice_title=invoice["invoice_title"], serial_num=invoice["serial_num"]))
    return render_template('root/fee.html', invoices=invoices_data)
