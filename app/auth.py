from flask_mail import Mail, Message
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import User
from __init__ import db, mailer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

auth = Blueprint('auth', __name__)

s = URLSafeTimedSerializer('testSecret')

@auth.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('client_page.client'))  

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password) and user.emailConfirm:
                login_user(user, remember=True)
                session['email'] = email
                return redirect(url_for('client_page.client'))
            else:
                flash('Wrong email or password!', category='error')
        else:
            flash("No such email registered!", category='error')
    return render_template('logIn.html', user=current_user)


@auth.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route('/sign_up',methods=["GET","POST"])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('client_page.client'))  

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get('password')
        password_confirm = request.form.get('confirm')
        session['email'] = obfuscate_email(email)
        user = User.query.filter_by(email=email).first()
        token = s.dumps(email,  salt='email_confirm')

        if user:
            if not user.emailConfirm:
                link = url_for('auth.confirm_email', token=token, _external=True)
                msg = Message(subject='Confirm Your Account', body=f'Please confirm your email: ' +link ,sender="viddatconfirm@gmail.com",recipients=[email])
                mailer.send(msg)
                return redirect(url_for("auth.verifyEmail"))
            else:
                    flash("An account is already registered with this email!", category="error")
        elif len(email) < 5:
            flash("Email must be atleast 6 characters!", category="error")
        elif len(password) < 7:
            flash("Password must be atleast 8 characters!", category="error")
        elif password != password_confirm:
            flash("Passwords do not match!", category="error")
        else:
            new_user = User(email=email, emailConfirm=False, password = generate_password_hash(password, method='pbkdf2:sha256'), username="default", aws_secret="", aws_access="", profile_picture="../static/userProfile.png")
            db.session.add(new_user)
            db.session.commit()
            link = url_for('auth.confirm_email', token=token, _external=True)
            msg = Message(subject='Confirm Your Account', body=f'Please confirm your email: ' +link ,sender="viddatconfirm@gmail.com",recipients=[email])
            mailer.send(msg)
            return redirect(url_for("auth.verifyEmail"))

    return render_template("signUp.html", user=current_user)


@auth.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email_confirm', max_age=30)
    except SignatureExpired:
        return render_template("emailExpired.html")
    user = User.query.filter_by(email = email).first()
    user.emailConfirm = True
    db.session.commit()
    login_user(user, remember=True)
    return render_template('emailVerified.html', user=current_user)

@auth.route('/confirm_email/verify')
def verifyEmail():
    return  render_template('checkEmail.html')

def obfuscate_email(email : str):
    i = len(email) -1
    while email[i] != "@":
        i-=1
    chars_before = i//2
    return email[0 :chars_before + 1] + "*"* (i -chars_before) + email[i:]