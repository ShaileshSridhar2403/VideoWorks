#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 09:10:01 2019

@author: shailesh
"""
video_path = "source/test.mp4"
#audio_path = "source/test.wav"
audio_path = video_path.strip(".mp4")+".wav"
segment_time = "30"                #in seconds
from subprocess import call

call(("ffmpeg -i "+video_path+" -ab 160k -ac 2 -ar 44100 -vn "+audio_path).split())
call(["rm","-rf","parts"])
call(["mkdir","parts"])
call(("ffmpeg -i "+audio_path+" -f segment -segment_time "+segment_time+" -c copy parts/out%09d.wav").split())


##########################transcription begins here########################################


import os
import speech_recognition as sr
from tqdm import tqdm
from multiprocessing.dummy import Pool
pool = Pool(8) # Number of concurrent threads

with open("api-key.json") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

r = sr.Recognizer()
files = sorted(os.listdir('parts/'))

def transcribe(data):
    idx, file = data
    name = "parts/" + file
    print(name + " started")
    # Load audio file
    with sr.AudioFile(name) as source:
        audio = r.record(source)
    # Transcribe audio file
    text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
    print(name + " done")
    
    return {
        "idx": idx,
        "text": text
    }

all_text = pool.map(transcribe, enumerate(files[:-1]))
pool.close()                                         #threaded approach(faster)
pool.join()
#all_text = []
#for i in range(len(files)-1):
#    all_text.append(transcribe([i,files[i]]))      #iterative approach(slower but works)
#    

transcript = ""
for t in sorted(all_text, key=lambda x: x['idx']):
    total_seconds = t['idx'] * 30
    # Cool shortcut from:
    # https://stackoverflow.com/questions/775049/python-time-seconds-to-hms
    # to get hours, minutes and seconds
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)

    # Format time as h:m:s - 30 seconds of text
    transcript = transcript + "{:0>2d}:{:0>2d}:{:0>2d} {}\n".format(h, m, s, t['text'])

print(transcript)

with open("transcript.txt", "w") as f:
    f.write(transcript)
