import datetime
import json
import math
from random import randint
import re
from webvtt import Caption, WebVTT


class VTT:
    def __init__(self, **kwargs):
        self.polly_response = kwargs.get("PollyResponse")
        self.filename = kwargs.get("Filename")
        self.audio_length_in_ms = kwargs.get("AudioLengthInMs")
        self.format = kwargs.get("Format", "vtt")
        self.maxChars = 4
        self.vtt = WebVTT()

    def remove_ssml_tags(self, text):
        return re.sub(r"\<[^>]*>", "", text)

    def to_sentences(self, response):
        return [
            json.loads(sentence.decode("utf8"))
            for sentence in response["AudioStream"].iter_lines()
        ]
    def format_vtt_time(self, msecs):
        minutes = math.floor(msecs / 60000)
        seconds = math.floor((msecs % 60000) / 1000)
        millis = int(msecs % 1000)
        return f"{minutes:02}:{seconds:02}.{millis:03}"
    

    def breakSentence(self):
        response = self.to_sentences(self.polly_response)
        sentences = [x['value'].split(" ") for x in response if x['type'] == 'sentence']

        s = []
        for i in sentences:
            for k in i:
                s.append(k)
        new = []

        index = 0
        while index < len(s):
            choice = randint(2,3)
            if index + choice >= len(s):
                new.append(s[index:])
            else:
                new.append(s[index: index + choice])
            index += choice
        return new




    def sentenceToVTT(self, sentence, words, startIndex):
        sentenceList = sentence['value'].split(" ")
        length = len(sentenceList)
        curr = 0
        new = []

        while curr < len(sentenceList):
            amt = randint(2,3)
            if curr + amt >= len(sentenceList): 
                new.append([(words[curr]["start"], words[-1]["end"]),sentenceList[curr:].join()])
            else: new.append([(words[curr]['start'],words[curr + amt]['end']),sentenceList[curr:amt+ curr].join()])
            curr += amt
        return new
            
    def test(self, **kwargs):
        response = self.to_sentences(self.polly_response)
        for i in response:
            if response['type'] == 'sentence':
                pass
            

    # def writeWithSentence(self, **kwargs):
    #     filename = f"{self.filename}.{self.format}"
    #     text = self.to_sentences(self.polly_response)
    #     curr = 0 
    #     index = 0
    #     for k in text:
    #         if k['type'] == 'sentence':
    #             curr+=1
                
    #             while text[curr]['type'] == 'word':

                
    

    #     pass

    def write(self, **kwargs):
        filename = f"{self.filename}.{self.format}"
        response = self.to_sentences(self.polly_response)
        sentences = [x for x in response if x['type'] == 'word' and self.remove_ssml_tags(x['value']) != ""]
        textWords = self.remove_ssml_tags(kwargs['t']).split()
        if len(sentences) == len(textWords):
            for i,sentence in enumerate(sentences):
                sentence['value'] = textWords[i]
        # print(self.breakSentence())
                
        phrase = []
        phraseCharCount = 0
        start = -1
        for index,word in enumerate(sentences):
            if start == -1: start = word['time']
    
            if index == len(sentences) -1:
                end = self.audio_length_in_ms - 200
            else:
                end = sentences[index + 1]['time']
            wordlen = len(self.remove_ssml_tags(word['value']))
            phraseCharCount += wordlen
            phrase.append(word['value'])

            if phraseCharCount >= self.maxChars or any(char in phrase[-1] for char in (",",".","?","!")):
                caption = Caption(
                self.format_vtt_time(start),
                self.format_vtt_time(end),
                [" ".join(phrase)],
                )
                phrase = []
                phraseCharCount = 0
                start = -1
                self.vtt.captions.append(caption)
            
        # for i in range(0, len(sentences)):
        #     start = sentences[i]["time"]
        #     if i == len(sentences) - 1:
        #         end = self.audio_length_in_ms - 200
        #     else:
        #         end = sentences[i + 1]["time"]
        #     sentence = self.remove_ssml_tags(sentences[i]["value"])
        #     caption = Caption(
        #         self.format_vtt_time(start),
        #         self.format_vtt_time(end),
        #         [sentence],
        #     )
        #     self.vtt.captions.append(caption)

        with open(filename, "w") as vf:
            if self.format == "srt":
                self.vtt.write(vf, format="srt")
            else:
                self.vtt.write(vf, format="vtt")
        print(
            f"{filename} written successfully.\nTotal Audio Length: {str(datetime.timedelta(seconds=self.audio_length_in_ms/1000))}\n# of Sentences: {len(sentences)}"
        )
