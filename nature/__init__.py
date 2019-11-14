import os
import time
import zipfile

from io import BytesIO
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, session, abort, send_from_directory, send_file, current_app
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from nature.db import get_db
from nature.auth import login_required
from nature.root import login_required as admin_login_required
from nature.excel import main


UPLOAD_FOLDER = os.path.curdir + os.path.sep + 'Abstract' + os.path.sep
DOWNLOAD_FOLDER = os.path.curdir + os.path.sep + 'Zip' + os.path.sep
RECOVERY_FOLDER = os.path.curdir + os.path.sep + 'Recovery' + os.path.sep
ALLOWED_EXTENSIONS = set(['docx', 'doc'])

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
    20 - Jacob T. Robinson
    21 - Georg Nagel
    22 - Bijan Pesaran
    23 - Andrew B. Schwartz
'''

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources=r'/*')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
    app.config['RECOVERY_FOLDER'] = RECOVERY_FOLDER
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
        return redirect(url_for('manage.index'))
        return render_template('index.html')

    @app.route('/zh')
    def zh():
        return redirect(url_for('manage.index'))
        return render_template('zh/index.html')

    @app.route('/zh/speakers')
    def zh_speaker():
        return redirect(url_for('manage.index'))
        return render_template('zh/speakers/leading.html')

    @app.route('/zh/speakers/leading')
    def get_zh_leadingspeakers():
        return redirect(url_for('manage.index'))
        return render_template('zh/speakers/leading.html')

    @app.route('/zh/speakers/part/<int:part_num>')
    def get_zh_speakers_bypart(part_num):
        if part_num < 1 or part_num > 4:
            abort(404) 
        return redirect(url_for('manage.index'))
        return render_template('zh/speakers/part%d.html'%part_num)

    @app.route('/zh/speakers/<int:speaker_num>')
    def get_zh_speaker_bynum(speaker_num):
        return redirect(url_for('manage.index'))
        if speaker_num > 23 or speaker_num < 1:
            abort(404) 
        return render_template('zh/speakers/%d.html'%speaker_num)


    @app.route('/speakers')
    def get_speakers():
        return redirect(url_for('manage.index'))
        return render_template('speakers/leading.html')


    @app.route('/speakers/leading')
    def get_leadingspeakers():
        return redirect(url_for('manage.index'))
        return render_template('speakers/leading.html')


    @app.route('/speakers/part/<int:part_num>')
    def get_speakers_bypart(part_num):
        return redirect(url_for('manage.index'))
        if part_num < 1 or part_num > 4:
            abort(404) 
        return render_template('speakers/part%d.html'%part_num)


    @app.route('/speakers/<int:speaker_num>')
    def get_speaker_bynum(speaker_num):
        return redirect(url_for('manage.index'))
        if speaker_num > 23 or speaker_num < 1:
            abort(404) 
        return render_template('speakers/%d.html'%speaker_num)


    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
    @app.route('/upload/delete', methods=['GET'])
    @login_required
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
            db.execute(
                'UPDATE user SET submit = ? WHERE id = ?',
                (False, user_id)
            )
            db.commit()
            return redirect(url_for('manage.submit'))
        return redirect(url_for('manage.submit'))


    @app.route('/download/<int:file_id>', methods=['GET', 'POST'])
    def download_file(file_id):
        user_id = session.get("user_id")
        admin_id = session.get("admin_id")
        if user_id is None and admin_id is None:
            return redirect("/index")
        db = get_db()
        abstract = db.execute(
            'SELECT filename FROM abstract WHERE id = ?', (file_id, )
        ).fetchone()
        
        if abstract is None:
            return abort(404) 
        else:
            return send_from_directory(os.path.realpath(app.config['UPLOAD_FOLDER']), abstract["filename"], as_attachment=True)


    @app.route('/download/batch', methods=['GET', 'POST'])
    def download_batch():
        user_id = session.get("user_id")
        admin_id = session.get("admin_id")
        if user_id is None and admin_id is None:
            return redirect("/index")

        file_list = list()
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        for f in files:
            file_list.append(f)
        print(file_list)

        # abort(404)
        dl_name = '{}.zip'.format('abstract')
        with zipfile.ZipFile(os.path.join(app.config['DOWNLOAD_FOLDER'], dl_name), "w", zipfile.ZIP_DEFLATED) as zf:
            for _file in file_list:
                with open(os.path.join(app.config['UPLOAD_FOLDER'], _file), 'rb') as fp:
                    zf.writestr(os.path.join(app.config['UPLOAD_FOLDER'], _file), fp.read())
        return send_from_directory(os.path.realpath(app.config['DOWNLOAD_FOLDER']), dl_name, as_attachment=True)
    

    @app.route('/download/excel', methods=['GET', 'POST'])
    @admin_login_required
    def download_excel():
        dbpath = current_app.config['DATABASE']
        xlspath = app.config['RECOVERY_FOLDER']
        main(dbpath, xlspath)
        return send_from_directory(os.path.realpath(app.config['RECOVERY_FOLDER']), 'nature.xls', as_attachment=True)
    

    @app.route('/download/db', methods=['GET', 'POST'])
    @admin_login_required
    def download_db():
        dbpath = os.path.curdir + os.path.sep + 'instance' + os.path.sep
        return send_from_directory(os.path.realpath(dbpath), 'nature.sqlite', as_attachment=True)


    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload_file():
        user_id = session.get('user_id')
        if user_id is None:
            return render_template('/auth/login.html')
        db = get_db()
        test = db.execute(
            'SELECT id FROM abstract WHERE user_id = ?', (user_id,)
            ).fetchone() 
        if test is not None:
            flash('Can\'t upload twice')  
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
                timestamp = round(time.time())
                filename = '%d+%d+%s'%(timestamp, user_id, file.filename)
                db.execute(
                    'INSERT INTO abstract (user_id, filename, state) VALUES(?, ?, ?)' ,
                    (user_id, filename, 0)
                )
                db.commit()
                db.execute(
                    'UPDATE user SET submit = ? WHERE id = ?',
                    (True, user_id)
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

    from . import root        
    app.register_blueprint(root.bp)
    app.add_url_rule('/admin', endpoint='index')

    return app

