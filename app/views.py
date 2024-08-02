from flask import Blueprint, render_template, redirect, url_for


views = Blueprint('views', __name__)    

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/terms_of_service')
def tos():
    return render_template("terms_of_service.html")

@views.route("/privacy")
def privacy():
    return render_template("privacy.html")

# @views.route('/pricing')
# def pricing():
#     return render_template("home.html")

@views.route('/emailVerified')
def emailVerified():
    return render_template("emailVerified.html")

# @views.route('/test')
# def test():
#     return render_template("checkEmail.html")

# @views.route("/tutorial")
# def tutorial():
#     return render_template("how_to.html")

@views.route('/tutorial/<int:step>')
def tutorial(step):
    if step < 1 or step > 13:
        return redirect(url_for('client_page.client'))
    return render_template(f'vid-dat_tutorial-{step}.html')