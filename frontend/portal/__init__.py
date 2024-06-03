import os
from flask import Flask
from flask_thumbnails import Thumbnail

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config['THUMBNAIL_MEDIA_ROOT'] = '/home/www/media'
    app.config['THUMBNAIL_MEDIA_URL'] = '/media/'
    thumbnail = Thumbnail(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import file_explorer
    app.register_blueprint(file_explorer.bp)

    def zip_lists(a, b):
        return zip(a, b)

    app.jinja_env.filters['zip'] = zip_lists
    return app