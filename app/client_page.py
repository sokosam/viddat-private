from flask import Blueprint, render_template, request, session, current_app, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
import time
from __init__ import db
from PIL import Image

import random
import string



client_page = Blueprint('client_page', __name__)

@client_page.route('/client', methods=['GET', 'POST'])
@login_required
def client():
    if request.method == "POST":
        text = request.form.get('text')
        if len(text) < 100:
            flash("Content must be atleast 100 characters", category="error")
        elif len(text) >5000:
            flash("Content cannot be greater than 5000 characters, try splitting it into parts!", category="error")
        else:
            title = request.form.get('title')
            part = request.form.get('part')
            video = request.form.get('videos')
            if not video: video = random.choice([r"stock_footage/minecraft/",
                                                 r"stock_footage/cooking/"])

            if request.form.get("gender"):
                gender = int(request.form.get('gender'))
            else:
                gender = 0

            user_id = current_user.get_id() 

            params = {
                'TEXT': text,
                'TITLE': title,
                'PART': part,
                "ID": generate_random_string(),
                "USERID": user_id,
                "VIDEO": video,
                "GENDER": gender,
            }

            queue = current_app.config['QUEUE']

            job = queue.fetch_job(user_id)
            if job and job.get_status() == 'started':
                print(user_id, "attempted to start a job. \n STATUS: FAIL, user already has a job running", flush=True)
                flash("You already have a video generating!", category="error")
                return redirect(url_for('client_page.client'))

            current_user.current_video = params["ID"]
            queue.enqueue("worker.script_async", params,job_id=user_id)
            print(user_id, "attempted to start a job. \n STATUS: SUCCESS", flush=True)
            flash("Your videos now generating! Head over to Video Status to retrieve it!",category="success")
    return render_template('clientPage.html', user=current_user)

@client_page.route('/client/accountSettings', methods=["GET","POST"])
@login_required
def accountSettings():
    if request.method == "POST":
        aws_secret = request.form.get("secret")
        aws_access =request.form.get('access')
        user_name = request.form.get('username')
        profile_picture = request.files['pfp']

        if aws_secret and len(aws_secret) > 128:
            flash("bad")
        elif aws_access and len(aws_access) >128:
            flash("trash")
        elif user_name and len(user_name) > 50:
            flash("dookiebutter")

        else:
            current_user.aws_secret = aws_secret
            current_user.aws_access = aws_access
            current_user.username = user_name
            print("hello",flush=True)
            try:
                pil_image = Image.open(profile_picture)
                if pil_image.format not in ("PNG", "JPEG", "JPG"):
                    raise TypeError("Trash extension")
                queue = current_app.config['QUEUE']
                filename = generate_random_string(25) + current_user.get_id()
                current_user.profile_picture=r"https://tsbckt.s3.amazonaws.com/pfp/" + filename + "." +pil_image.format.lower()
                queue.enqueue("worker.update_pfp", pfp=pil_image, filename=filename, format = pil_image.format.lower())
            except Exception as e:
                print(e, flush=True)

            db.session.commit()
            flash("we did it!")
    return render_template('accountSettings.html', user=current_user)

@client_page.route('/premiumSubscriptions')
@login_required
def premiumSubscriptions():
    return render_template('premiumSubscriptions.html', user=current_user)

@client_page.route('/billingHistory')
@login_required
def billingHistory():
    return render_template('billingHistory.html', user=current_user)

@client_page.route('/client/status', methods=["GET"])
@login_required
def status():
    if request.method =="GET":
        # try:
        queue = current_app.config['QUEUE']
        user = current_user.get_id()
        job = queue.fetch_job(user)

        videos = {
            r"stock_footage/cooking/": ("Cooking","cooking.webp"),
            r"stock_footage/minecraft/": ("Minecraft", "minecraft_cover.png"),
        }

        if job:
            params = job.fetch(id= user, connection = current_app.config["CONNECTION"]).args[0]

            video_status = job.get_status()
            if video_status == "finished":
                video = job.fetch(id= user, connection = current_app.config["CONNECTION"]).result
                print(video,flush=True)
            else:
                video = "Video Not Done Proccessing!"
        else:
            video = "No Video Currently Generating!"
            video_status = "nothing"
            return render_template("status.html",
                            user=current_user,
                            video_status=video_status,
                            video=video)
        # except Exception as e:
        #     print(e, flush=True)
    return render_template("status.html",
                            user=current_user,
                            video_status=video_status,
                            video=video,
                            stock_footage = videos[params["VIDEO"]][0],
                            cover=  videos[params["VIDEO"]][1],
                            characters=  len(params["TEXT"])
                            )

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # Includes both letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))