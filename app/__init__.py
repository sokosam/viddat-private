#socketio
from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from instance.secrets import getAppKey, getSQL, getEmailPWD
from flask_mail import Mail
from rq import Queue
from redis import Redis
from flask_socketio import SocketIO
from dotenv import load_dotenv
from os import environ as env, urandom
load_dotenv()


db = SQLAlchemy()
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USERNAME'] = 'viddatconfirm@gmail.com'
app.config['MAIL_PASSWORD'] = env["MAIL"]
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

connection = Redis(host='redis', port =6379)
app.config["CONNECTION"] = connection
app.config['QUEUE'] = Queue(connection=connection)


socketio = SocketIO(app,message_queue='redis://redis:6379', async_mode="gevent")
mailer = Mail(app)

def create_app():
    app.config["SECRET_KEY"] = urandom(24)
    app.config["SQLALCHEMY_DATABASE_URI"] = env["DB_URI"]
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}  
    db.init_app(app)

    from views import views
    from auth import auth
    from client_page import client_page
    
    app.register_blueprint(views, url_prefix=r"/")
    app.register_blueprint(auth, url_prefix=r'/')
    app.register_blueprint(client_page, url_prefix=r'/')


    from models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

