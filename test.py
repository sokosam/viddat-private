# from worker.video_generator import web_gen
# import os
# import zipfile

# params={
#     "ID": "test",
#     "TEXT": ' dqdqwdq qwdqw as as sa das sdasaad a',
#     "TITLE": "dad a da",
#     "PART": "3"
# }

# test= web_gen()
# os.mkdir(path ="temp"+params["ID"])
# test.generate_video(text=params['TEXT'], title=params['TITLE'], red_text=params['PART'], output_path="temp"+params["ID"], output_name="video.mp4",stock_footage=r"/home/samuel/Project/worker/stock_footage/cooking.mp4")
# with zipfile.ZipFile(params["ID"]+".zip", "w") as zfile:
#     zfile.write(os.path.join("temp"+params["ID"], "video.mp4"), arcname="video.mp4")

