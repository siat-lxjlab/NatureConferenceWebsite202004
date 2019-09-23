import os
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, session, abort
)
from werkzeug.utils import secure_filename
from nature.db import get_db

UPLOAD_FOLDER = os.path.curdir + os.path.sep + 'Abstract' + os.path.sep
ALLOWED_EXTENSIONS = set(['pdf'])

'''
    1 - Arnd Pralle
    2 - Arto V.Nurmikko
    3 - Charles M.Lieber
    4 - Dae-Hyeong Kim
    5 - Daryl Kipke
    6 - Gaurav Sharma
    7 - George Malliaras
    8 - Grégoire Courtine
    9 - John Rogers
    10 - Kullervo Hynynen
    11 - Kristin Zhao
    12 - Lee E Miller
    13 - Leigh Hochberg
    14 - Miguel Nicolelis
    15 - Serge Picaud
    16 - Tamar Makin    
    17 - Xiaojie Duan 
    18 - Xinyan Tracy Cui
    19 - Zhenan Bao
'''

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'nature.sqlite'),
    )
    # restrict the file size
    # app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # index
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')

    @app.route('/zh')
    def zh():
        return render_template('zh/index.html')

    @app.route('/zh/speakers')
    def zh_speaker():
        return render_template('zh/speakers/leading.html')

    @app.route('/zh/speakers/leading')
    def get_zh_leadingspeakers():
        return render_template('zh/speakers/leading.html')

    @app.route('/zh/speakers/part/<int:part_num>')
    def get_zh_speakers_bypart(part_num):
        if part_num < 1 or part_num > 4:
            abort(404) 
        return render_template('zh/speakers/part%d.html'%part_num)

    @app.route('/zh/speakers/<int:speaker_num>')
    def get_zh_speaker_bynum(speaker_num):
        if speaker_num > 19 or speaker_num < 1:
            abort(404) 
        return render_template('zh/speakers/%d.html'%speaker_num)

    @app.route('/speakers')
    def get_speakers():
        return render_template('speakers/leading.html')

    @app.route('/speakers/leading')
    def get_leadingspeakers():
        return render_template('speakers/leading.html')

    @app.route('/speakers/part/<int:part_num>')
    def get_speakers_bypart(part_num):
        if part_num < 1 or part_num > 4:
            abort(404) 
        return render_template('speakers/part%d.html'%part_num)

    @app.route('/speakers/<int:speaker_num>')
    def get_speaker_bynum(speaker_num):
        if speaker_num > 19 or speaker_num < 1:
            abort(404) 
        return render_template('speakers/%d.html'%speaker_num)

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    @app.route('/upload/delete', methods=['GET'])
    def delete_upload_file():
        user_id = session.get('user_id')
        if user_id is None:
            return redirect(url_for('auth.login'))
        abstract_id = request.args.get('id')
        db = get_db()
        abstract = db.execute(
            'SELECT filename FROM abstract WHERE id = ?', (abstract_id,)
        ).fetchone()
        if abstract is not None:
            filename = abstract['filename']
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                print(e.__str__ )
            db.execute(
                'Delete FROM abstract WHERE id = ?', (abstract_id,)
            )
            db.commit()
            return redirect(url_for('manage.submit'))
        return redirect(url_for('manage.submit'))


    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        user_id = session.get('user_id')
        if user_id is None:
            return render_template('/auth/login.html')
        db = get_db()
        test = db.execute(
            'SELECT id FROM abstract WHERE user_id = ?', (user_id,)
                ).fetchone() 
        if test is not None:
            flash('Can\'t repeat upload')  
            return redirect('/my/submit')
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                db.execute(
                    'INSERT INTO abstract (user_id, filename, state) VALUES(?, ?, ?)' ,
                    (user_id, filename, 0)
                )
                db.commit()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect('/my/submit')
        return render_template('/manage/submit.html')


    from . import db, auth
    db.init_app(app)    
    app.register_blueprint(auth.bp)

    from . import manage        
    app.register_blueprint(manage.bp)
    app.add_url_rule('/manage', endpoint='index')

    return app

