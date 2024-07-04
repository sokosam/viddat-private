from worker.video_generator import web_gen
import os
import zipfile

params={
    "ID": "test",
    "TEXT": ' Trap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ RemixTrap Queen - Adriana Gomez | Eightfold X MKJ Remix',
    "TITLE": None,
    "PART": "3"
}

test= web_gen()
os.mkdir(path ="temp"+params["ID"])
test.generate_video(text=params['TEXT'], title=params['TITLE'], red_text=params['PART'], output_path="temp"+params["ID"], output_name="video.mp4",stock_footage=r"C:\Users\Samue\Documents\GitHub\viddat\worker\stock_footage\cooking.mp4")

