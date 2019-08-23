import os
from flask import (
    Blueprint, Flask, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = os.path.curdir + os.path.sep + 'Abstract' + os.path.sep
ALLOWED_EXTENSIONS = set(['pdf'])

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
    def index():
        return render_template('index.html')

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('/manage/submit.html')
        return render_template('/manage/submit.html')


    from . import db, auth
    db.init_app(app)    
    app.register_blueprint(auth.bp)

    from . import manage
    app.register_blueprint(manage.bp)
    app.add_url_rule('/manage', endpoint='index')

    return app

