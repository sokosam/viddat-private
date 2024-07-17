from rq import Queue, Worker
from redis import Redis
from video_generator import web_gen
from PIL import Image
import os
import boto3
import shutil
from time import sleep
from flask_socketio import SocketIO


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
        
        socketio.emit('task_complete', {'job_id': job_id, 'url': url}, room=job_id)
        print(url,flush=True)
    except Exception as e:
        socketio.emit('task_error', {'job_id': job_id, 'error': str(e)}, room=job_id)
        print(e, flush=True)
        return "Error!"
    
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
