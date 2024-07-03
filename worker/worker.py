from rq import Queue, Worker
from redis import Redis
from video_generator import web_gen
import os
import zipfile
import boto3
import shutil
from time import sleep
conn = Redis(host='redis', port=6379)
worker = Worker(map(Queue, ['default']), connection=conn)



if __name__ == '__main__':
    worker.work()

def script_async(params):
    try:
        client = web_gen()
        os.mkdir(path ="temp"+params["ID"])
        client.generate_video(text=params['TEXT'], title=params['TITLE'], red_text=params['PART'], output_path="temp"+params["ID"], stock_footage =params["VIDEO"],output_name="video.mp4")
        with zipfile.ZipFile(params["ID"]+".zip", "w") as zfile:
            zfile.write(os.path.join("temp"+params["ID"], "video.mp4"), arcname="video.mp4")

        
        session = boto3.Session(aws_access_key_id="AKIAZQ3DTVZZEIHYE4HL", aws_secret_access_key="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")
        client = session.client("s3")
        with open(params["ID"]+".zip", "rb") as f:
            client.upload_fileobj(f, "tsbckt", params["ID"]+".zip")
            print("File: "+ params["ID"]+".zip " + "uploaded by user: " + params["USERID"], flush=True)
        
        shutil.rmtree("temp"+params["ID"])
        os.remove(params["ID"]+".zip")
        url = client.generate_presigned_url("get_object", Params=
                                        {'Bucket': "tsbckt",
                                        "Key": params["ID"]+".zip"},
                                        ExpiresIn = 600)
        print(url,flush=True)
    except Exception as e:
        print(e)
    return url