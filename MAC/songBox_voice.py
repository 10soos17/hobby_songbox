#!/usr/bin/python3
#-*- coding:utf-8 -*-
#import csv
import os, shutil
import time
#import threading

#from kivy.uix.label import Label
#from kivy.uix.button import Button

#import pyaudio
#import wave
import playsound as pls

from gtts import gTTS
import speech_recognition as sr

import songBox_playerPyaudio as sbp

nowDate =  time.strftime("%Y_%m_%d")

baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록

winColor =[211/255, 211/255, 211/255, 1]#[189/255,183/255,110/255,1]#[211/255,211/255,211/255,1]#
boxColor = [188/255, 143/255, 143/255, 1]#[110/255,0/255,0/255,1]#[105/255,105/255,105/255,1]#
textColor = [255/255, 255/255, 255/255, 1]
stopColor = [105/255,105/255,105/255,1]#gold[189/255,183/255,110/255,1]#red[110/255,0/255,0/255,1]

bartextColor =[189/255,183/255,110/255,1]#deepblue+green[30/255,160/255,180/255,1]#grey[105/255,105/255,105/255,1]#red[110/255,0/255,0/255,1]

soundbar_fontsize="22sp"
menu_fontsize="20sp"
text_fontsize="17sp"

#tempObj = Label(text='1')
#tempLabel=Label(text='ready')
#tempBtn=Button(text='temp')

#==============first msg========================================================
def play_msg(msg):
    print(f"play_msg:{play_msg}")
    get_msg = msg
    flag = False

    if msg == 'Tell me the song title':
        pls.playsound(f'{ttsDir}/startmsg.mp3', False)
        duration = sbp.cal_duration(f"{ttsDir}/startmsg.mp3")
        time.sleep(duration)
    else:
        tts = gTTS(text=f"{get_msg}",lang="en",tld="com")
        tts.save(f"{ttsDir}/msg.mp3")

        pls.playsound(f'{ttsDir}/msg.mp3', False)
        duration = sbp.cal_duration(f"{ttsDir}/msg.mp3")
        time.sleep(duration)
        os.remove(f"{ttsDir}/msg.mp3")

    if msg != 'Tell me the song title':
        flag = True

    return flag

#==============yes or no========================================================
def yesno_voice():
    print(f"start_yesno_voice")
    start = time.time()
    r = sr.Recognizer()
    m = sr.Microphone()
    audio=False

    while audio == False:
        try:
            with m as source:
                print(f'yes or no:')
                audio = r.listen(source)

        except Exception as errmsg:
                yesno_msg = f"{errmsg}retry."
                print(f"{errmsg}retry.")

                return yesno_msg

    try:
        yesno_msg=r.recognize_google(audio)
        print(f'answer_yes or no:{yesno_msg}')

        return yesno_msg.lower()

    except Exception as errmsg:
        yesno_msg=errmsg
        return yesno_msg

#==============start voice conversation=========================================
def searchsong_voice():
    print(f"start_searchsong_voice")
    msg = 'Tell me the song title'
    yesno_msg = ""
    yesno_msg_sec = ""
    flag = play_msg(msg)
    flag = False
    audio = False

    start = time.time()
    r = sr.Recognizer()
    m = sr.Microphone()

    #==============소리 감지할 때까지 ===============================================
    while audio == False:

        try:
            with m as source:
                print(f'speak:')
                audio = r.listen(source)
                flag=True

            #==============time check===========================================
            if time.time()-start > 10:
                print(f"I waited {time.time()-start} seconds")
                msg = f"I waited {int(time.time()-start)} seconds. Will I wait for you to speak?"
                flag = play_msg(msg)

                while yesno_msg !="no" and yesno_msg !="yes":
                    yesno_msg = yesno_voice()

                    if yesno_msg == "no":
                        msg = f"Ok. Bye"
                        flag = play_msg(msg)
                        print(f"wait_no{yesno_msg}")
                        return False, msg

                    elif yesno_msg == "yes":
                        print(f"wait_yes{yesno_msg}")
                        return searchsong_voice()

                    else:
                        msg = f"I can't understand your answer. Tell me one more time."
                        flag = play_msg(msg)

        #==============exception check==========================================
        except Exception as errmsg:
                print(f"{errmsg}")
                flag = play_msg(msg)

                while yesno_msg !="no" and yesno_msg !="yes":
                    yesno_msg = yesno_voice()

                    if yesno_msg == "no":
                        msg = f"Ok. Bye"
                        flag = play_msg(msg)
                        print(f"first_except_no{yesno_msg}")
                        return False, msg

                    elif yesno_msg == "yes":
                        print(f"first_except_yes{yesno_msg}")
                        return searchsong_voice()
                    else:
                        msg = f"I can't understand your answer. Tell me one more time."
                        flag = play_msg(msg)

    #==============소리 감지 & flag == True=======================================
    if flag == True and audio != False:
        try:
            speechSong=r.recognize_google(audio)
            print(f'You said:{speechSong}')
            msg = f'You said:{speechSong}. Did you say this song title?'
            play_msg(msg)

            while yesno_msg !="no" and yesno_msg !="yes":

                yesno_msg = yesno_voice()

                if yesno_msg == "no":
                    msg = f'Would you like to try again?'
                    print(f"second_no{yesno_msg}")
                    play_msg(msg)
                    yesno_msg_sec

                elif yesno_msg == "yes":
                    print(f"second_yes{yesno_msg}")
                    return search_song(speechSong)

                else:
                    msg = f"I can't understand your answer. Tell me one more time."
                    play_msg(msg)

            if yesno_msg == "no":
                while yesno_msg_sec !="no" or yesno_msg_sec !="yes":
                    yesno_msg_sec = yesno_voice()

                    if yesno_msg_sec == "no":
                        msg = f"Ok. Bye"
                        flag = play_msg(msg)
                        print(f"second_no_no{yesno_msg_sec}")
                        return False, msg

                    elif yesno_msg_sec == "yes":
                        print(f"second_no_yes{yesno_msg_sec}")
                        return searchsong_voice()
                    else:
                        msg = f"I can't understand your answer. Tell me one more time."
                        flag = play_msg(msg)


        except Exception as errmsg:
                print(f"I can't recognize the voice.{errmsg}")
                msg = f"I can't recognize the voice. Would you like to try again?"
                flag = play_msg(msg)

                while yesno_msg !="no" and yesno_msg !="yes":
                    yesno_msg = yesno_voice()

                    if yesno_msg == "no":
                        msg = f"Ok. Bye"
                        flag = play_msg(msg)
                        print(f"second_except_no{yesno_msg}")
                        return False, msg

                    elif yesno_msg == "yes":
                        print(f"second_except_yes{yesno_msg}")
                        return searchsong_voice()

                    else:
                        msg = f"I can't understand your answer. Tell me one more time."
                        flag = play_msg(msg)

#==============search song > return result =====================================
def search_song(speechSong):
    global GET_PLAY_BTN

    yesno_msg=''
    print(f'start search_song:{speechSong}')

    try:
        songList=os.listdir(f'{mp3Dir}')

        for i in songList:
            if i not in ignoreFile:

                title=i.split('_')

                if speechSong.lower() == title[0].lower():
                    print(f"find {i}")

                    return True, i

        msg = f"This song title {speechSong} could not be found. Would you like to try again?"
        res = play_msg(msg)

        while yesno_msg !="no" and yesno_msg !="yes":
            yesno_msg = yesno_voice()

            if yesno_msg == "no":
                msg = f"Ok. Bye"
                flag = play_msg(msg)
                print(f'search_song__no:{yesno_msg}')
                return False, msg

            elif yesno_msg == "yes":
                print(f'search_song__yes:{yesno_msg}')
                return searchsong_voice()

            else:
                msg = f"I can't understand your answer. Tell me one more time."
                flag = play_msg(msg)


    except Exception as errmsg:
            print(f"I can't find this song {speechSong}. {errmsg}")
            msg = f"I can't find this song {speechSong}. Would you like to try again?"
            flag = play_msg(msg)

            while yesno_msg !="no" and yesno_msg !="yes":
                yesno_msg = yesno_voice()

                if yesno_msg == "no":
                    msg = f"Ok. Bye"
                    flag = play_msg(msg)
                    print(f'search_song_except_no:{yesno_msg}')
                    return False, msg

                elif yesno_msg == "yes":
                    print(f'search_song_except_yes:{yesno_msg}')
                    return searchsong_voice()

                else:
                    msg = f"I can't understand your answer. Tell me one more time."
                    flag = play_msg(msg)

"""
def recognize_test(play_btn):
    #print(play_btn,pause_btn)
    get_PLAY_BTN = play_btn
    #get_PAUSE_BTN = pause_btn
    #os.system(f"open {baseDir}/searhsong.mp3")
    #searchsong = SoundLoader.load(f"{baseDir}/searchsong.mp3")
    #searchsong.play()
    #searchsong.volume = 1.0
    #searchsong.loop = False
    audio = False
    start = time.time()
    r = sr.Recognizer()
    m = sr.Microphone()


    while audio == False:
        try:
            with m as source:
                print(f'speak:')
                audio = r.listen(source)
            if time.time()-start > 10:
                sbp.get_restart()
                print("Waited 10 seconds")
                return 0
        except Exception as msg:
                print(f"{msg}retry.")
                return 0

    try:
        speechText=r.recognize_google(audio)
        print(f'You said:{speechText}')

    except Exception as msg:
            sbp.get_restart()
            print(f"can't recognize the voice. {msg}")
            return 0

    if audio != False:

        songList=os.listdir(f'{mp3Dir}')
        for i in songList:
            if i not in ignoreFile:
                title=i.split('_')
                if speechText.lower() == title[0].lower():
                    print(f"find {i}")

                    #get_PAUSE_BTN.text = "|||"
                    #get_PAUSE_BTN.color = boxColor
                    playTitle = [i]
                    playing = [tempObj,]
                    replay=True
                    playnum=0

                    sbp.get_restart()
                    thread_one = threading.Thread(target = sbp.get_playThread, args = (playTitle,replay,playing,get_PLAY_BTN,tempBtn,tempLabel,playnum), daemon=True)
                    thread_one.start()
                    return 0

        #nosong = SoundLoader.load(f"{baseDir}/nosong.mp3")
        #nosong.play()
        #nosong.loop = False
        #os.system(f"open {baseDir}/nosong.mp3")
        sbp.get_restart()
        print(f"can't find {speechText}")
        return 0
"""
