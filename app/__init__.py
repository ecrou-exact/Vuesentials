from flask import Flask
from flask_session import Session
from config import config as Config
import os

sess = Session()

def create_app():
    app = Flask(__name__)
    config_name = os.environ.get("FLASKENV")
    app.config.from_object(Config[config_name])
    Config[config_name].init_app(app)

    sess.init_app(app)

    from .home import home_blueprint
    app.register_blueprint(home_blueprint, url_prefix="/")

    return app
    
