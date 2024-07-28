from flask_mail import Mail, Message
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import User
from __init__ import db, mailer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import string, random

auth = Blueprint('auth', __name__)

s = URLSafeTimedSerializer('testSecret')

@auth.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('client_page.client'))  

    if request.method == "POST":
        email = request.form.get('email').lower()
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
        email = request.form.get("email").lower()
        password = request.form.get('password')
        password_confirm = request.form.get('confirm')
        session['email'] = obfuscate_email(email)
        user = User.query.filter_by(email=email).first()
        token = s.dumps(email,  salt='email_confirm')

        if user:
            if not user.emailConfirm:
                link = url_for('auth.confirm_email', token=token, _external=True)
                try:
                    msg = Message(subject='Confirm Your Account', body=f'Please confirm your email: ' +link ,sender="viddatconfirm@gmail.com",recipients=[email])
                    mailer.send(msg)
                except Exception as e:
                    print("Error: " + str(e), flush=True)
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
            new_user = User(email=email, emailConfirm=False, password = generate_password_hash(password, method='pbkdf2:sha256'), username="default", aws_secret="", aws_access="", profile_picture="../static/userProfile.png", password_reset="")
            db.session.add(new_user)
            db.session.commit()
            link = url_for('auth.confirm_email', token=token, _external=True)
            msg = Message(subject='Confirm Your Account', body=f'Please confirm your email: ' +link +" (This link is only valid for 10 minutes)." ,sender="viddatconfirm@gmail.com",recipients=[email])
            mailer.send(msg)
            return redirect(url_for("auth.verifyEmail"))

    return render_template("signUp.html", user=current_user)


@auth.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email_confirm', max_age=600)
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

@auth.route('/recover/', methods=['GET', 'POST'])
def recover():
    if request.method == "POST":
        email = request.form.get("email").lower()
        try:
            token = s.dumps(email, "reset_pwd")
            link = url_for('auth.forgot', token=token, _external=True)
            msg = Message(subject="Viddat Password Reset", body="You have requested to change your password, please follow this link to do so: "+link+" (This link is only valid for 10 mintues)",sender="viddatconfirm@gmail.com",recipients=[email])
            mailer.send(msg)
            user = User.query.filter_by(email=email).first()
            user.password_reset = token
            db.session.commit()
            flash("Password reset sent successfully!", category="success")
        except Exception as e:
            flash("Something went wrong!", category="error")
            print("Error: " +str(e),flush=True)
    return render_template("recover.html")


@auth.route('/forgot/<token>', methods =["GET","POST"])
def forgot(token):
    try:
        email = s.loads(token, salt="reset_pwd",max_age=600)
    except Exception as e:
        return render_template("forgot.html")
    
    if request.method == "POST":
        password = request.form.get('password')
        password_confirm = request.form.get('confirm')
        if len(password) < 7:
            flash("Password must be atleast 8 characters!", category="error")
        elif password != password_confirm:
            flash("Passwords do not match!", category="error")
        else:
            try:
                user = User.query.filter_by(email=email).first()
                if user.password_reset != token:
                    raise Exception("Wrong token")
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                db.session.commit()
                flash("Your password has updated successfully", category="success")
                user.password_reset = generate_random_string(6)
                db.session.commit()
            except Exception as e:
                flash("Something went wrong!", category="error")
    return render_template("forgot.html")


def obfuscate_email(email : str):
    i = len(email) -1
    while email[i] != "@":
        i-=1
    chars_before = i//2
    return email[0 :chars_before + 1] + "*"*(i-chars_before) + email[i:]

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # Includes both letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))