
# -*- coding:utf-8 -*-
#from kivy.core.audio import SoundLoader
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import time, os, sys, subprocess
import threading
import random
from pygame import mixer
import pyaudio
import playsound
import wave

import numpy as np
import struct
import matplotlib.pyplot as plt
import math
from math import sqrt
from scipy.fftpack import fft

import songBox_list as sbl

baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','youtube-dl.exe','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록

winColor =[211/255, 211/255, 211/255, 1]#[189/255,183/255,110/255,1]#[211/255,211/255,211/255,1]#
boxColor = [188/255, 143/255, 143/255, 1]#[110/255,0/255,0/255,1]#[105/255,105/255,105/255,1]#
textColor = [255/255, 255/255, 255/255, 1]#[255/255,255/255,255/255,1]#[255/255,255/255,255/255,1]#
stopColor = [105/255,105/255,105/255,1]#gold[189/255,183/255,110/255,1]#red[110/255,0/255,0/255,1]

RUN_NOW = "Ready"
PAUSE_FLAG = False
OUT_FLAG = False
DRAG_FLAG = False
SHUFFLE_FLAG = False

RUN_DURATION=0
RUN_T=0
POS=0
VOLUME=0
CHUNK=1024

CHANGE_playTitle = []
#===============5번 사용==========================================================
#===============곡 재생시간 계산->time.sleep 주기위해 사용==============================
def cal_duration(song):
    #song='/Users/soos/Desktop/py_song/list/Reuben and The Dark_Black Water.mp3'
    args=("ffprobe","-show_entries", "format=duration","-i",song)
    popen = subprocess.Popen(args, stdout = subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()

    textOutput = str(output)
    textOutput=textOutput.split('=')
    textOutput=textOutput[1].split('\\')

    return float(textOutput[0])

#===============1번 사용(class SoundBarMenu의 def start_newsong 함수)==============
#===============new song 배경음으로 재생============================================
def get_newsongNum():
    os.chdir(f'{mp3Dir}')
    count = 0
    for i in os.listdir(f'{mp3Dir}'):
        if i not in ignoreFile:
            now = int(time.time())
            downTime= int(os.stat(i).st_atime)#st_ctime(수정시간),st_atime(파일접근한(다운로드)날짜),st_mtime(파일만든날짜)
            period = (now - downTime)//3600
            if period <= 48:
                count+=1
    return count


def play_newsong():

    newNum = get_newsongNum()
    playTitle = []

    songList = os.listdir(f"{mp3Dir}")

    if newNum == 0:
        return playTitle

    for i in os.listdir(f"{mp3Dir}"):
        if i not in ignoreFile:
            now = int(time.time())
            downTime= int(os.stat(f'{mp3Dir}\\{i}').st_atime)#st_ctime(수정시간),st_atime(파일접근한(다운로드)날짜),st_mtime(파일만든날짜)
            period = (now - downTime)//3600
            if period <= 48:
                playTitle.append(i)
    return playTitle

#===============1번 사용(class SoundBarMenu의 def start_newsong 함수)==============
#===============new song 중의 10개만 random 배경음으로 재생===========================
def play_newsongRandom():

    newNum = get_newsongNum()
    playTitle = []

    limitNum = 10
    randomList = os.listdir(f"{mp3Dir}")

    if newNum == 0:
        print("There is no new song.")
        return playTitle

    elif newNum  < limitNum:
        limitNum = newNum

    while limitNum > 0:
        randomNum = random.randint(0,len(randomList)-1)
        if randomList[randomNum] not in ignoreFile and randomList[randomNum] not in playTitle:
            now = int(time.time())
            downTime= int(os.stat(f'{mp3Dir}\\{randomList[randomNum]}').st_atime)#st_ctime(수정시간),st_atime(파일접근한(다운로드)날짜),st_mtime(파일만든날짜)
            period = (now - downTime)//3600
            #print(period)
            if period <= 48:
                playTitle.append(randomList[randomNum])
                limitNum -= 1

    print(f'Random newsong playTitle:{playTitle}')
    return playTitle

#===============1번 사용(class SoundBarMenu의 def start_newsong 함수)==============
#===============total song 중의 정한 개수만 random 배경음으로 재생======================
def play_songRandom():

    playTitle = []

    randomList = os.listdir(f"{mp3Dir}")
    songNum = len(os.listdir(f"{mp3Dir}"))

    limitNum = 10
    if songNum  < limitNum:
        limitNum = songNum

    while limitNum > 0:
        randomNum = random.randint(0,songNum-1)
        if randomList[randomNum] not in ignoreFile and randomList[randomNum] not in playTitle:

            playTitle.append(randomList[randomNum])
            limitNum -= 1

    print(f'Random playTitle:{playTitle}')
    return playTitle

#===============1번 사용(class SoundBarMenu의 def start_newsong 함수)==============
#===============total song 중의 정한 개수만 random 배경음으로 재생======================
def play_allsong():
    playTitle = []

    for i in os.listdir(f"{mp3Dir}"):
        if i not in ignoreFile:
            playTitle.append(i)

    print(f'all song playTitle:{playTitle}')
    return playTitle

#===============1번 사용(class SoundBarMenu의 def shuffle_song 함수)===============
#=============== play 곡 shuffle=================================================
def shuffle_song():
    global CHANGE_playTitle

    shuffle_playTitle = CHANGE_playTitle[:]
    songNum = len(CHANGE_playTitle)
    numlist = []
    count = 0

    while count < songNum:
        randomNum = random.randint(0,songNum-1)

        if randomNum not in numlist:
            CHANGE_playTitle[randomNum] = shuffle_playTitle[count]
            numlist.append(randomNum)
            count+=1

    return CHANGE_playTitle#, CHANGE_playing

#===============12번 사용=========================================================
#===============노래재생은 thread 로 재생시키기=======================================
def get_playThread(playTitle,playing,playBtn,onesongBtn,playnum):
    global id, CHANGE_playTitle,CHANGE_playing,GET_playnum,GET_replay, GET_playBtn,GET_onesongBtn, RUN_DURATION,NOW,RUN_NOW, AUDIO,WFILE,CHANGE_stream#, VILIST

    AUDIO = pyaudio.PyAudio()

    print(f"1111111111_1111111111_____________________1_TH_id: {id}, 2_TH_id(current): {threading.currentThread().ident}\nENTER NEW thread, id!=current\n")
    print(f"=====NEW=====\nplayTitle:{playTitle}\nplaying{playing}")
    print(f"______________________________________________________________________________________________________")

    #=====get OBJ===============================================================
    GET_playBtn = playBtn #playBtn
    GET_onesongBtn = onesongBtn #titleBTN
    GET_replay = 3 #replay value

    #=====check thread id(second)===============================================
    if type(id) == int and id != str(threading.currentThread().ident):

        print(f"1111111111_2222222222_____________________1_TH_id: {id}, 2_TH_id(current): {threading.currentThread().ident}\nENTER SECOND thread, id!=current\n")
        print(f"=====NEW=====\nplayTitle: {playTitle}\nplaying: {playing}\n")
        print(f"=====BEFORE=====\nCHANGE_playTitle: {CHANGE_playTitle}\nCHANGE_playing: {CHANGE_playing}")
        print(f"______________________________________________________________________________________________________")

    #=====play버튼, playing 곡 버튼 색 변경(CHANGE_playing감지)=======================
    if GET_playBtn.text == ">":

        if GET_playBtn == GET_onesongBtn and GET_playBtn != playBtn:
            GET_playBtn.text = "="
            GET_playBtn.color=boxColor
            for i in playing: #지금
                i.color = textColor

        elif GET_playBtn != GET_onesongBtn: #play_oneSong or playUserlist에서 호출했을 때(play버튼 !=playing곡버튼)
            for i in CHANGE_playing: # 전 playing곡 색 변경
                i.color = textColor
            for i in playing: #지금
                i.color = stopColor
    else:
        GET_playBtn.text = ">"
        GET_playBtn.color=stopColor
        for i in playing:
            i.color = stopColor

    #=====context switching=====================================================
    CHANGE_playTitle = playTitle #before = new tiltelist
    CHANGE_playing = playing #before = new titleBTNlist
    GET_playnum = playnum
    id = threading.currentThread().ident
    print(f"2222222222________________________________id: {id}, current: {threading.currentThread().ident}\nCOMPLETE reset value and START, id=current\n")
    print(f"=====CHANGE=====\nCHANGE_playTitle: {CHANGE_playTitle}\nCHANGE_playing: {CHANGE_playing}")
    print(f"______________________________________________________________________________________________________")

    #==============play loop====================================================
    while GET_replay !=0:

        for i in range(GET_playnum, len(CHANGE_playTitle)):

            WFILE = wave.open(f'{mp3Dir}\\{CHANGE_playTitle[i]}','rb')
            stream = AUDIO.open(format=AUDIO.get_format_from_width(WFILE.getsampwidth()),channels=WFILE.getnchannels(),rate=WFILE.getframerate(),output=True)
            #stream=pyaudio.Stream(output=True,PA_manager=pyaudio.pa.paMacCoreStreamInfo,format=p.get_format_from_width(wf.getsampwidth()),channels=wf.getnchannels(),rate=wf.getframerate())

            RUN_DURATION = cal_duration(f'{mp3Dir}\\{CHANGE_playTitle[i]}')

            CHANGE_stream = stream #get stream
            NOW = CHANGE_playTitle[i]

            print(f"GET_replay:{GET_replay}")
            print(f"__________________________________________loop__________________________________________index number: {i}\n------RUNNING-----GET_playnum: {GET_playnum}, CHANGE_playTitle[GET_playnum]: {CHANGE_playTitle[i]}")

            get_running()

            if QUIT_FLAG == True:#id != threading.currentThread().ident
                print(f"4444444444________________________________1_TH_id: {id},2_TH_id(current): {threading.currentThread().ident}\nfor loop(playlist)_Break before thread, id!=current\n")
                print(f"______________________________________________________________________________________________________")
                break

        if QUIT_FLAG == True:#id != threading.currentThread().ident
            print(f"4444444444________________________________2_TH_id: {id},2_TH_id(current): {threading.currentThread().ident}\nwhile loop(replay)_Break before thread, id!=current\n")
            print(f"______________________________________________________________________________________________________")
            break

        #=============replay check==============================================
        GET_playnum = 0
        GET_replay-=1

        if GET_replay == 2: #GET_replay == 3일때, 무한재생시키기위해
            GET_replay +=1

    #=================result(stop or complete or break)=========================
    if GET_replay != True and id == threading.currentThread().ident:
        GET_playBtn.text = "="
        GET_playBtn.color=boxColor
        for i in playing:#playing곡 색 변경
            i.color = textColor

        #for i in range(len(VILIST)):
        #    VILIST[i].background_color = winColor
        #    VILIST[i].color = winColor

        RUN_NOW = f"Let the music play!"
        CHANGE_playTitle = []
        CHANGE_playing = []
        RUN_DURATION=0
        CHANGE_stream.close()
        AUDIO.terminate()

        print(f"5555555555_1111111111_____________________id: {id}, current:{threading.currentThread().ident}\nEND || STOP || COMPLETE(id=current)(1.stopBTN---checkedlist 2.stopBTN---userlist 3.complete)\n")
        print(f"=====END=====\nCHANGE_playTitle: {CHANGE_playTitle}\nCHANGE_playing: {CHANGE_playing}")
        print(f"______________________________________________________________________________________________________")
        return 0

    else:
        print(f"555555555_2222222222_____________________id: {id}, current:{threading.currentThread().ident}\nEND || STOP || COMPLETE(1.stopBTN---onesong2.thread---other onesongBTN 3.thread---userlistBTN)\n")
        print(f"=====NOW=====\nCHANGE_playTitle: {CHANGE_playTitle}\nCHANGE_playing: {CHANGE_playing}")
        print(f"______________________________________________________________________________________________________")
        return 0

#=================play song(wav file read and write) ===========================
def get_running():
    global id, RUN_T, GET_replay, GET_playBtn, GET_onesongBtn, RUN_DURATION, NOW, RUN_NOW, PAUSE_FLAG, DRAG_FLAG,OUT_FLAG,QUIT_FLAG, AUDIO, WFILE,CHUNK, CHANGE_stream, POS, VOLUME

    QUIT_FLAG = False
    #CHUNK = 1024*2# *
    CHUNK = 1024
    hz=WFILE.getframerate()
    CHANNELS = WFILE.getnchannels()
    div=int(hz//1000*CHUNK)
    data = WFILE.readframes(CHUNK)
#    print(f"data:{data}")

    check_btn = GET_onesongBtn

    start_T= CHANGE_stream.get_time()
    remain_T = RUN_DURATION

    #x = np.arange(0, CHUNK*2, 2)
    #x_fft = np.linspace(0, hz, CHUNK)

    while len(data) > 0:

        POS_T=WFILE.tell()

        RUN_T=int(POS_T//div)
        remain_T = int(RUN_DURATION - RUN_T)
    #    print(f'start_T:{start_T},duration:{RUN_DURATION}, run_T:{RUN_T}, remain_T:{remain_T},POS_T:{POS_T}')

        #CHANGE_stream.write(data)
        data = np.fromstring(data, dtype=np.int16)
        np.multiply(data, VOLUME, out=data, casting="unsafe")
        CHANGE_stream.write(data.tostring(), CHUNK, exception_on_underflow=False)

        """
        #=================visualizer test=======================================
        print(f"numpy_data:{numpy_data}numpy_data.tostring():{numpy_data.tostring()}")
        try:
            data= np.array(struct.unpack(str(2* CHUNK * CHANNELS) + 'B', data))
            data = np.array(data, dtype='b')[::2] + 128
            y_fft = fft(data)
            y_fft = np.abs(y_fft[:CHUNK]) * CHANNELS / (256 * CHUNK)
            draw = split_freq(y_fft)
            update_graph(draw)
            print(y_fft)#->그리고싶은 개수로 쪼개기-->그 개수에 좌표 주기
        except Exception as msg:
                print(f"{msg}retry.")
        """

        data = WFILE.readframes(CHUNK)

        #print(f"id:{threading.currentThread().ident}, 3333333333_0000000000_____________________streaming................")

        #=================stop =================================================
        if GET_playBtn.text == "=":
            RUN_NOW = f"Let the music play!"

            CHANGE_stream.stop_stream()
            CHANGE_stream.close()
            AUDIO.terminate()
            print(f"id:{threading.currentThread().ident}, 3333333333_1111111111_____________________GET_playBtn_____stop................close&terminate")


        elif GET_onesongBtn != check_btn and check_btn.text != "temp":
            GET_onesongBtn = check_btn
            print(f"id:{threading.currentThread().ident}, 3333333333_1111111111_____________________GET_onesongBtn_____stop................break")
            break

        #=================QUIT_FLAG=============================================
        if QUIT_FLAG == True:
            CHANGE_stream.stop_stream()
            CHANGE_stream.close()
            break

        #=================DRAG_FLAG(playbar dag -> pos변화 감지)===================
        if DRAG_FLAG == True:
            WFILE.setpos(POS)
            DRAG_FLAG=False
            print(f"DRAG_FLAG_TRUE:loop_POS:{POS}")

        #=================OUT_FLAG(PREV_BTN or NEXT_BTN)========================
        if OUT_FLAG == True:
            if GET_playnum == 0:
                RUN_NOW = "This is the first song."
            elif GET_playnum == len(CHANGE_playTitle)-1:
                RUN_NOW = "This is the last song."
            elif len(CHANGE_playTitle) == 1:
                RUN_NOW = "Only one song."
            time.sleep(1)
            OUT_FLAG=False
            print("Out of playlist range")

        #=================PAUSE_FLAG(PAUSE_BTN)=================================
        while PAUSE_FLAG == True:
            CHANGE_stream.stop_stream()

            if PAUSE_FLAG == False:
                CHANGE_stream.start_stream()

        #=================draw duration=========================================
        run_M=int((RUN_T)//60)
        run_S=int(round((RUN_T)%60,0))
        remain_M=int((remain_T)//60)
        remain_S=int(round((remain_T)%60,0))

        if remain_S == 60:
            remain_S = 0

        run_M=str(run_M).zfill(2)
        run_S=str(run_S).zfill(2)
        remain_M=str(remain_M).zfill(2)
        remain_S=str(remain_S).zfill(2)

        RUN_NOW = f"+{run_M}:{run_S}\
\
                                            -{remain_M}:{remain_S}\n{NOW[:-4]}"
    #    print(RUN_T,remain_T)

    print(f"id:{threading.currentThread().ident}, 3333333333_2222222222_____________________complete................return")

    """
    for i in range(len(VILIST)):
        VILIST[i].background_color = winColor
        VILIST[i].color = winColor
    """
    print("sound quit")
    return 0
"""
#===============visulizer test==================================================
def split_freq(freq): # splits given sound frequencies into groups of frequencies to feed into turtle
    freq_ranges = []
    for i in range(len(freq)): # split the frequencies into 32 groups
        if i % abs((len(freq)//32)) == 0:
            if len(freq_ranges) > 0:
                freq_ranges[len(freq_ranges)-2] = freq_ranges[len(freq_ranges)-2]
            freq_ranges.append(0)
        freq_ranges[len(freq_ranges)-1] = freq_ranges[len(freq_ranges)-1] + freq[i]
    for i in range(len(freq_ranges)):
        freq_ranges[i] = (freq_ranges[i] / np.array(freq_ranges).max())
#    print(f"freq_ranges:{freq_ranges}")

    return [i * 400 for i in freq_ranges]

def update_graph(frequencies):
    global VILIST
    for i in range(len(VILIST)):
        val = frequencies[i]/400
        strVal=f"{val}"
        floatVal = float(strVal)
    #    print(val, xval)
    #    VILIST[i].pos = [20*(i),floatVal]
        #VILIST[i].pos = [80*i,int(frequencies[i])]
        VILIST[i].background_color = boxColor
        VILIST[i].color = boxColor
        VILIST[i].pos = [int(frequencies[i])+800,48*i]
        #VILIST[i].pos_hint = {"x": .1*i, "top": .0, "y":.9*int(frequencies[i]),"bottom":.1}
        #VILIST[i].pos_hint = {"x": .1*i, "top": .0, "y":.9*floatVal,"bottom":.0}
        if i == 0:
            VILIST[i].pos_hint = {"x": .1*i, "top": .0, "y":.9*floatVal,"bottom":.0}
"""

#=2번 사용=1.ScreenSetting의 def press_settingpageBTN 2.ScreenSong의 press_songBTN=
#===============재생중인 곡 끝까지 끝났을 때, playing 안에 obj 없애기 위해 사용=============
def get_playResult():
    return CHANGE_playing
#===============1번 사용=ScreenMain의 def show_playList에서========================
#===============play 중인 곡 Label text 변경=======================================
def get_playTitle():
    global CHANGE_playTitle
    return CHANGE_playTitle
#===============1번 사용=ScreenMain의 def show_playLabel에서========================
#===============play 중인 곡 Label text 변경=======================================
def get_playLabel():
    return RUN_NOW
#===============SoundBarMenu의 volume_bar 변경====================================
def get_volume(volume):
    global VOLUME
    #VOLUME = pow(2, (sqrt(sqrt(sqrt(volume))) * 192 - 192)/6)
    VOLUME = volume
#===============1번 사용=class UpperMenu -> def color_pressed=====================
#===============color change 후 속성 값 유지=======================================
def set_color(win, box, text, stop):
    global winColor,boxColor,textColor, stopColor
    winColor = win
    boxColor = box
    textColor = text
    stopColor = stop
    return 0
#===============SoundBarMenu의 play_bar 이동->곡 위치 변경===========================
def get_pos(val):
    global DRAG_FLAG, POS, WFILE,CHUNK
    DRAG_FLAG = True
    length = WFILE.getnframes()#파일 총 길이
    hz= WFILE.getframerate()
    POS = val * (hz // 1000)* CHUNK
    POS = int(POS)
    if POS > length:
        POS = length
    #WFILE.setpos(POS)
    print(f"get_pos:POS:{POS}")
    return POS# , act_pos()
#===============SoundBarMenu의 play_bar 값 가져가기================================
def get_playtime():
    return (RUN_DURATION, RUN_T)
#===============SoundBarMenu의 replay_BTN=========================================
def get_replay(replay):
    global GET_replay
    GET_replay = replay
    print(f"GET_replay:{GET_replay}")
    return GET_replay
#===============SoundBarMenu의 PAUSE_BTN=========================================
def get_pause():
    global PAUSE_FLAG
    PAUSE_FLAG = True
    #mixer.music.pause()
    return PAUSE_FLAG
def get_restart():
    global PAUSE_FLAG
    PAUSE_FLAG = False
    #mixer.music.unpause()
    return PAUSE_FLAG
#===============QUIT============================================================
def get_quit():
    global QUIT_FLAG
    QUIT_FLAG = True
#===============SoundBarMenu의 self.prev_BTN=====================================
def get_prev():
    global GET_playnum, OUT_FLAG
    #mixer.music.stop()
    GET_playnum -=1
    if GET_playnum <0:
        GET_playnum =0
        OUT_FLAG = True
    print(f"___________________________________________________get_prev__________________________________________________________________GET_playnum{GET_playnum}")
    return GET_playnum
#===============SoundBarMenu의 self.next_BTN=====================================
def get_next():
    global GET_playnum, OUT_FLAG
    #mixer.music.stop()
    GET_playnum +=1
    if GET_playnum >len(CHANGE_playTitle)-1:
        GET_playnum =len(CHANGE_playTitle)-1
        OUT_FLAG = True
    print(f"___________________________________________________get_next__________________________________________________________________GET_playnum{GET_playnum}")
    return GET_playnum
