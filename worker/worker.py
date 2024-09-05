from gevent import monkey
monkey.patch_all()

from rq import Queue, Worker
from redis import Redis
from video_generator import web_gen
import os
import boto3
import botocore.exceptions
import shutil
from flask_socketio import SocketIO
from viddat_exceptions import *
from dotenv import load_dotenv
from os import environ as env, urandom
load_dotenv()


conn = Redis(host='redis', port=6379)
worker = Worker(map(Queue, ['default']), connection=conn)

socketio = SocketIO(message_queue='redis://redis:6379', async_mode="gevent")

viddat_access = env["AWS_ACCESS"]
viddat_secret = env["AWS_SECRET"]


if __name__ == '__main__':
    worker.work()

def remove_temp_viddat_dirs(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            if dir_name.endswith("tempViddat"):
                dir_path = os.path.join(root, dir_name)
                print(f"Removing directory: {dir_path}")
                shutil.rmtree(dir_path)


def script_async(params):
    remove_temp_viddat_dirs(base_dir= os.getcwd())
    job_id = params['USERID']  # Use USERID as the room ID
    try:
        socketio.emit('task_started', {'job_id': job_id}, room=job_id)
        client = web_gen()
        os.mkdir(path ="temp"+params["ID"] + "tempViddat")

        try:    
            client.generate_video(
                                text=params['TEXT'],
                                title=params['TITLE'],
                                red_text=params['PART'],
                                gender=params["GENDER"],
                                output_path="temp"+params["ID"]+"tempViddat",
                                stock_footage =params["VIDEO"],
                                output_name= params["ID"]+".mp4",
                                music =params["MUSIC"],
                                thumbnail_url = params["THUMBNAIL_URL"],
                                user_name= params["USERNAME"],
                                aws_access = params["AWS_ACCESS"],
                                aws_secret = params["AWS_SECRET"])
        except botocore.exceptions.ClientError as audio_error:
            print("Error Occured: " + str(audio_error),flush=True)
            raise AWS_error("Something went wrong connecting to the AWS Service, this might be due to improper/wrong security key inputs (Access key and Secret key).")

        except Exception as video_gen_exception:
            print("Error Occured: " + str(video_gen_exception),flush=True)
            raise vidGen_error("Something went wrong during the generation process of your video, try changing your inputs or contacting support!")

        try:
            put_session = boto3.Session(aws_access_key_id= viddat_access, aws_secret_access_key= viddat_secret)
            put = put_session.client("s3")

            session = boto3.Session(aws_access_key_id=params["AWS_ACCESS"], aws_secret_access_key=params["AWS_SECRET"])
            client = session.client("s3")
            with open("temp" + params["ID"] +"tempViddat" + "//" + params["ID"]+".mp4", "rb") as f:
                put.upload_fileobj(f, "tsbckt",  r"vids/"+ params["ID"]+".mp4")
                print("File: "+ params["ID"]+".mp4 " + "uploaded by user: " + params["USERID"], flush=True)

            shutil.rmtree("temp"+params["ID"] + "tempViddat")
            url = client.generate_presigned_url("get_object", Params=
                                            {'Bucket': "tsbckt",
                                            "Key": r"vids/" + params["ID"]+".mp4", "RequestPayer": "requester"},
                                            ExpiresIn = 1800)
        except Exception as upload_error:
            print( "Error Occured: " + str(upload_error), flush=True)
            raise video_upload_error("Something went wrong with the uploading of the video, this is most likely an AWS S3 service issue and not your fault!")
        socketio.emit('task_complete', {'job_id': job_id, 'url': url}, room=job_id)
        print(url,flush=True)
    except Exception as e:
        socketio.emit('task_error', {'job_id': job_id, 'error': str(e)}, room=job_id)
        print(e, flush=True)
        return ("Error!", str(e))

    return url

def update_pfp(pfp, filename, format):
    try:
        session = boto3.Session(aws_access_key_id=viddat_access, aws_secret_access_key= viddat_secret)
        client = session.client("s3")
        pfp.save(f"{filename}.{format}")
        with open(f"{filename}.{format}", "rb") as f:
            client.upload_fileobj(f, 'profilepictsbckt', r"pfp/" + f"{filename}.{format}")
        os.remove(f"{filename}.{format}")
        print("Uploaded profile picture: ", filename,".",format)
    except Exception as e:
        print(e, flush=True)