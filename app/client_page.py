from flask import Blueprint, render_template, request, session, current_app, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
import time

import random
import string



client_page = Blueprint('client_page', __name__)

@client_page.route('/client', methods=['GET', 'POST'])
@login_required
def client():
    if request.method == "POST":
        text = request.form.get('text')
        if len(text) < 100:
            flash("Content must be atleast 100 characters")
        elif len(text) >5000:
            flash("Content cannot be greater than 5000 characters, try splitting it into parts!")
        else:
            title = request.form.get('title')
            part = request.form.get('part')
            video = request.form.get('videos')
            if not part:print(part)

            user_id = current_user.get_id()

            params = {
                'TEXT': text,
                'TITLE': title,
                'PART': part,
                "ID": generate_random_string(),
                "USERID": user_id,
                "VIDEO": video
            }

            queue = current_app.config['QUEUE']

            job = queue.fetch_job(user_id)
            if job and job.get_status() == 'started':
                print(user_id, "attempted to start a job. \n STATUS: FAIL, user already has a job running", flush=True)
                return redirect(url_for('client_page.client'))

            current_user.current_video = params["ID"]
            queue.enqueue("worker.script_async", params,job_id=user_id)
            print(user_id, "attempted to start a job. \n STATUS: SUCCESS", flush=True)
    return render_template('clientPage.html', user=current_user)

@client_page.route('/accountSettings')
@login_required
def accountSettings():
    return render_template('accountSettings.html', user=current_user)

@client_page.route('/premiumSubscriptions')
@login_required
def premiumSubscriptions():
    return render_template('premiumSubscriptions.html', user=current_user)

@client_page.route('/billingHistory')
@login_required
def billingHistory():
    return render_template('billingHistory.html', user=current_user)

@client_page.route('/status', methods=["GET"])
@login_required
def status():
    if request.method =="GET":
        # try:
        queue = current_app.config['QUEUE']
        user = current_user.get_id()
        job = queue.fetch_job(user)

        if job:
            video_status = job.get_status()
            if video_status == "finished":
                video = job.fetch(id= user, connection = current_app.config["CONNECTION"]).result
                print(video,flush=True)
            else:
                video = "Video Not Done Proccessing!"
        else:
            video = "No Video Currently Generating!"
            video_status = "nothing"
        # except Exception as e:
        #     print(e, flush=True)
    return render_template("status.html", user=current_user, video_status=video_status, video=video)

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # Includes both letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))