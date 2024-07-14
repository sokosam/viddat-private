import os
from pollyFiles.polly_vtt import PollyVTT
from random import choice
import ffmpeg
import pysrt
import subprocess
from random import randint
from title_page_gen import thumbnail_generator
import text_scripts as textProcessing

class web_gen:
    def __init__(self):
        pass
    
    def concat_audio_string(self, concatList):
        concatStr = ""
        for i in concatList:
            if i == concatList[0]: concatStr = i
            else: concatStr += "|" + i
        return concatStr
    
    def srtConcat(self, fileList, output_path, output_name = r"body.srt"):
        end = 0
        for file in fileList:
            subs = pysrt.open(file)
            if end == 0: 
                end = [subs[-1].end.hours,  subs[-1].end.minutes ,  subs[-1].end.seconds , subs[-1].end.milliseconds]
                numSubs = len(subs)
                continue
            subs.shift(hours = end[0], minutes = end[1] , seconds = end[2] , milliseconds = end[3])
            end = [subs[-1].end.hours,  subs[-1].end.minutes ,  subs[-1].end.seconds , subs[-1].end.milliseconds] 
            subs.save(file, encoding='utf-8')

            with open(file, 'r') as input_file:
                with open(file[0:-4] + "TEMP" + file[-4:], 'w') as output_file:
                    prev = "\n"
                    for line in input_file:
                        if line.strip().isdigit() and prev == '\n':
                            number = int(line)
                            number += numSubs
                            output_file.write(str(number) + '\n')
                        else:
                            output_file.write(line)       
                        prev = line
            numSubs += len(subs)
            os.remove(file)
            os.rename(file[0:-4] + "TEMP" + file[-4:], file)
        with open(os.path.join(output_path, output_name), 'w') as outfile:
            for fname in fileList:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)

    def generate_audio(self, output_path, text, title, gender, aws_access, aws_secret,speed = "120"):
        time = 0

        if gender < 0: gender = "Joanna"
        else: gender =  "Matthew"

        #Make sure the title does disallowed words\
        if title:
            temp = ""
            for i in title.split(): temp+= textProcessing.changeAcro(i) +" "
            title = temp[0: -1]

        #As Polly only accepts text < 3000 characters, we must first slice the text.
        text_list = textProcessing.pollySplicer(text)
        concat_audio = []
        concat_SRT = []

        polly = PollyVTT(params = {"AWS_ACCESS_KEY": aws_access, "AWS_SECRET_KEY": aws_secret})

        if title:
            time += polly.generate(
                                    filename = os.path.join(output_path, "title"),
                                    format = "srt",
                                    Text = f"<speak><prosody rate='{speed}%'>" + title + '<break time ="1s"/></prosody></speak>',
                                    VoiceId = gender,
                                    OutputFormat = "mp3")
            title_time = time
            concat_audio = [os.path.join(output_path,'title.mp3')]
        else:
            title_time = 0

        for index,pollyText in enumerate(text_list):
            if index == len(text_list) -1:
                time += polly.generate(
                                        filename = os.path.join(output_path, f'body{index}'),
                                        format = "srt",
                                        Text = f"<speak><prosody rate='{speed}%'>" + pollyText + '<break time = "1s"/></prosody></speak>',
                                        VoiceId = gender,
                                        OutputFormat = "mp3")
            else:
                time += polly.generate(
                                        filename = os.path.join(output_path, f'body{index}'),
                                        format = "srt",
                                        Text = f"<speak><prosody rate='{speed}%'>" + pollyText + '</prosody></speak>',
                                        VoiceId = gender,
                                        OutputFormat = "mp3")
                
            concat_audio.append(os.path.join(output_path,f'body{index}.mp3'))
            concat_SRT.append(os.path.join(output_path,f'body{index}.mp3.srt')) 
        self.srtConcat(fileList = concat_SRT, output_path= output_path)
        return [title_time, time, self.concat_audio_string(concat_audio)]

    def fit_dimensions(self, w, h, video_path,output_path, output_name = "temp.mp4"):
        output = os.path.join(output_path, output_name)
        command = fr'ffmpeg -i {video_path} -vf "crop={w + 1}:{h}:{w}:0" {output} -y'
        subprocess.run(command, shell=True)
        os.remove(video_path)
        os.rename(output, video_path)
        


    def generate_video(self, text, title, red_text, output_path, output_name, thumbnail_url, aws_access, aws_secret, user_name="VIDDAT.CA",start_time= randint(1,100), stock_footage = r'stock_footage/cooking.mp4', music_choice= None, delay= 0,gender = None, style= "FontName=OPTIGranby-ElephantAgency,FontSize=20,Alignment=10,Shadow=1,Spacing=-1"):

        if not gender: gender = textProcessing.getGender(text) 
        if title: gender += textProcessing.getGender(title)

        if not stock_footage or stock_footage=="":
            drive = choice(os.listdir("stock_footage"))
            stock_video = choice(os.listdir(os.path.join("stock_footage", drive)))
            combined = os.path.join(drive, stock_video)
            stock_footage = os.path.join('stock_footage',combined)
        else:
            stock_footage = os.path.join(stock_footage, choice(os.listdir(stock_footage)))


        title_end, end, audio_str = self.generate_audio(output_path, text, title, gender, aws_secret=aws_secret, aws_access=aws_access)
        
        print(stock_footage)

        try:
            probe = ffmpeg.probe(stock_footage)
        except ffmpeg.Error as e:
            print(e.stderr, flush=True)

        video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
        w,h = int(video_streams[0]['width']), int(video_streams[0]['height'])

        newW, newH = None, None
        if round(w/h, 2) > round(9/16,2):
            newW = int(h * (9/16))
            newH = h
            self.fit_dimensions(newW,newH, video_path=stock_footage,output_path = output_path)
        elif round(w/h,2) < round(9/16,2):
            newH = int(w*16/9)
            newW = w
            self.fit_dimensions(newW,newH, video_path=stock_footage,output_path = output_path)
        else: newW, newH = w,h

        subs = pysrt.open(os.path.join(output_path, 'body.srt'))
        subs.shift(seconds = title_end)
        subs.save(os.path.join(output_path, 'body.srt'), encoding='utf-8')


        
        subtitle_body_path = os.path.join(output_path, 'body.srt').replace("\\", r"\\")

        out = os.path.join(output_path, output_name)    

        if title:
            try:
                thumbnail_generator(text= title,red_text=red_text, output_path = output_path, file_name ='title.mp3',newSize=newH, url=thumbnail_url,user_name=user_name)
            except Exception as e:
                raise Exception("Error generating title picture! Probably an issue with the profile picture.")
            command = fr"""ffmpeg -stream_loop -1 -ss {start_time} -to {end + start_time} -i {stock_footage} -i {os.path.join(output_path,"title.mp3.png")} -i "concat:{audio_str}" -filter_complex "[0:v][1:v] overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='between(t,0,{title_end})',subtitles={subtitle_body_path}:force_style='{style}'" -shortest -map 2:a:0 {out} -preset fast -y""" #-hide_banner -loglevel error 
        else:
            command = fr"""ffmpeg -stream_loop -1 -ss {start_time} -to {end + start_time} -i {stock_footage} -i "concat:{audio_str}" -filter_complex "[0:v] subtitles={subtitle_body_path}:force_style='{style}'" -shortest -map 1:a:0 {out} -preset fast -y""" # -hide_banner -loglevel error 
        # command = (
        #     "ffmpeg",
        #     "-stream_loop", "-1",
        #     "-ss", start_time,
        #     "-i", stock_footage,
        #     "-i", os.path.join(output_path,"title.mp3.png"),
        #     "-i", f"concat:{audio_str}",
        #     "-filter_complex", fr"[0:v][1:v] overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2:enable='between(t,0,{title_end})',subtitles={subtitle_body_path}:force_style='{style}'",
        #     "-shortest",
        #     "-map", "2:a:0",
        #     "-to", end,
        #     out,
        #     "-y"
        # )
        subprocess.run(command, shell = True)

        remove = [file for file in os.listdir(output_path) if not file.endswith(".mp4")]
        for file in remove:
            os.remove(os.path.join(output_path,file))