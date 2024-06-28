from flask import Blueprint, render_template, request, session, current_app
from flask_login import login_user, login_required, logout_user, current_user
from rq import Queue
from redis import Redis 
import time

import random
import string



client_page = Blueprint('client_page', __name__)

@client_page.route('/client', methods=['GET', 'POST'])
@login_required
def client():
    if request.method == "POST":
        text = request.form.get('text')
        title = request.form.get('title')
        part = request.form.get('part')
        if not part:print(part)

        user_id = current_user.get_id()
        print(user_id, flush=True)

        params = {
            'TEXT': text,
            'TITLE': title,
            'PART': part,
            "ID": generate_random_string(),
        }

        queue = current_app.config['QUEUE']

        job = queue.fetch_job(user_id)
        if job and job.get_status() == 'started':
            print(user_id, "attempted to start a job. \n STATUS: FAIL, user already has a job running", flush=True)
            return render_template('clientPage.html', user=current_user)

        queue.enqueue("worker.script_async", params,job_id=user_id)
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

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # Includes both letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))