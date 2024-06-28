from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from instance.secrets import getAppKey, getSQL, getEmailPWD
from flask_mail import Mail, Message
from rq import Queue
from redis import Redis

db = SQLAlchemy()
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465 
app.config['MAIL_USERNAME'] = 'viddatconfirm@gmail.com'
app.config['MAIL_PASSWORD'] = getEmailPWD()
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

connection = Redis(host='redis', port =6379)
app.config['QUEUE'] = Queue(connection=connection)
mailer = Mail(app)

def create_app():
    app.config["SECRET_KEY"] = getAppKey()
    app.config["SQLALCHEMY_DATABASE_URI"] = getSQL()
    db.init_app(app)

    from views import views
    from auth import auth
    from client_page import client_page
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(client_page, url_prefix='/')


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

