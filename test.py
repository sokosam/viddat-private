# from worker.video_generator import web_gen
# import os
# import zipfile

# params={
#     "ID": "test",
#     "TEXT": ' Trap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ Remix',
#     "TITLE": None,
#     "PART": "3"
# }

# test= web_gen()
# os.mkdir(path ="temp"+params["ID"])
# test.generate_video(text=params['TEXT'], title=params['TITLE'], red_text=params['PART'], output_path="temp"+params["ID"], output_name="video.mp4",stock_footage=r"C:\Users\Samue\Documents\GitHub\viddat\worker\stock_footage\cooking.mp4")


from worker.title_page_gen import thumbnail_generator
thumbnail_generator(text="hi", output_path="", url=r"https://tsbckt.s3.amazonaws.com/pfp/7WiYW4MZ2VjSZqZseoF4ajIkI1.png")

# import requests
# import json
# import boto3
# viddat_access = "AKIAZQ3DTVZZLEBKP5Z7"
# viddat_secret = "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"

# put_session = boto3.Session(aws_access_key_id= viddat_access, aws_secret_access_key= viddat_secret)
# put = put_session.client("s3")

# res = put.head_object(Bucket="tsbckt", Key="vids/nowKSwy4.mp4")

# print(res)
# print(list(res.keys()))
# print(res["ContentLength"])
# # print(requests.head("https://tsbckt.s3.amazonaws.com/vids/8IdL91QM.mp4"))