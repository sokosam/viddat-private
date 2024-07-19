from rq import Queue, Worker
from redis import Redis
from video_generator import web_gen
from PIL import Image
import os
import boto3
import botocore.exceptions
import shutil
from time import sleep
from flask_socketio import SocketIO
from viddat_exceptions import *

conn = Redis(host='redis', port=6379)
worker = Worker(map(Queue, ['default']), connection=conn)

socketio = SocketIO(message_queue='redis://redis:6379')


if __name__ == '__main__':
    worker.work()

def script_async(params):
    job_id = params['USERID']  # Use USERID as the room ID
    try:
        socketio.emit('task_started', {'job_id': job_id}, room=job_id)
        client = web_gen()
        os.mkdir(path ="temp"+params["ID"])

        try:
            client.generate_video(
                                text=params['TEXT'],
                                title=params['TITLE'],
                                red_text=params['PART'],
                                gender=params["GENDER"],
                                output_path="temp"+params["ID"],
                                stock_footage =params["VIDEO"],
                                output_name= params["ID"]+".mp4",
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
            session = boto3.Session(aws_access_key_id=params["AWS_ACCESS"], aws_secret_access_key=params["AWS_SECRET"])
            client = session.client("s3")
            with open("temp" + params["ID"] + "//" + params["ID"]+".mp4", "rb") as f:
                client.upload_fileobj(f, "tsbckt",  r"vids/"+ params["ID"]+".mp4")
                print("File: "+ params["ID"]+".mp4 " + "uploaded by user: " + params["USERID"], flush=True)
            
            shutil.rmtree("temp"+params["ID"])
            url = client.generate_presigned_url("get_object", Params=
                                            {'Bucket': "tsbckt",
                                            "Key": r"vids/" + params["ID"]+".mp4"},
                                            ExpiresIn = 600)
        except Exception as upload_error:
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
        session = boto3.Session(aws_access_key_id="AKIAZQ3DTVZZEIHYE4HL", aws_secret_access_key="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")
        client = session.client("s3")
        pfp.save(f"{filename}.{format}")
        with open(f"{filename}.{format}", "rb") as f:
            client.upload_fileobj(f, 'profilepictsbckt', r"pfp/" + f"{filename}.{format}")
        os.remove(f"{filename}.{format}")
        print("Uploaded profile picture: ", filename,".",format)
    except Exception as e:
        print(e, flush=True)
