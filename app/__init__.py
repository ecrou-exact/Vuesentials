from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from config import config as Config
import os


db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
sess = Session()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    config_name = os.environ.get("FLASKENV")

    app.config.from_object(Config[config_name])

    Config[config_name].init_app(app)

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.login_view = "account.login"
    login_manager.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db
    sess.init_app(app)
    from .account.account import account_blueprint
    from .home import home_blueprint
    from .components.components import components_blueprint
    from .components.paginations.paginations import paginations_blueprint

    app.register_blueprint(account_blueprint, url_prefix="/account")
    app.register_blueprint(paginations_blueprint, url_prefix="/paginations")
    app.register_blueprint(home_blueprint, url_prefix="/")
    app.register_blueprint(components_blueprint, url_prefix="/components")

    return app
    
