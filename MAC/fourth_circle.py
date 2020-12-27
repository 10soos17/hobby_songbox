#!/usr/bin/python3
#-*- coding:utf-8 -*-
import cgi, os
import time
import webbrowser
import random

baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "2_tts")#tts 폴더
ignoreFile = ['ffmpeg','.DS_Store','list_data','0_file_data','1_dir_userlist','2_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록

def get_randomFont():
    #fontList = os.listdir(f'{fontDir}')
    #todayfont = f'{fontDir}/{fontList[random.randint(0,len(fontList)-1)]}'
    todayfont = f'{fontDir}/NanumPen.otf'

    print(todayfont)
    return todayfont

def current_time():
    currentdate =  time.strftime("%Y / %m / %d")
    localtime =  time.strftime("%H:%M:%S")
    morning = 5<= int(time.strftime("%H")) <12
    afternoon = 12<=int(time.strftime("%H"))<19
    evening = 19<=int(time.strftime("%H"))<24 or 0<=int(time.strftime("%H"))<5
    if morning:
        return str(f"Good morning\n{currentdate} {localtime}")
    elif afternoon:
        return str(f"Good afternoon\n{currentdate} {localtime}")
    elif evening:
        return str(f"Good evening\n{currentdate} {localtime}")#"\n{test}")
    #first = 14 <= int(time.strftime("%H")) < 15 and 10 <= int(time.strftime("%M")) <= 40
    #second = 15 <= int(time.strftime("%H")) < 16 and 5 <= int(time.strftime("%M")) <= 35
    #third = 16 <= int(time.strftime("%H")) < 17 and 0 <= int(time.strftime("%M")) <= 30
    #fourth = (16 <= int(time.strftime("%H")) < 17 and 55 <= int(time.strftime("%M")) <= 59) or (17 <= int(time.strftime("%H")) < 18 and 0 <= int(time.strftime("%M")) <= 25)
    #middle = (18 <= int(time.strftime("%H")) < 19 and 30 <= int(time.strftime("%M")) <= 59) or (19 <= int(time.strftime("%H")) < 20 and 0 <= int(time.strftime("%M")) <= 15)
    #if first:
    #    return str(f"1 class\n{currentdate}\n{localtime}")
    #elif second:
    #    return str(f"2 class\n{currentdate}\n{localtime}")
    #elif third:
    #    return str(f"3 class\n{currentdate}\n{localtime}")
    #elif fourth:
    #    return str(f"4 class\n{currentdate}\n{localtime}")
    #elif middle:
    #    return str(f"M class\n{currentdate}\n{localtime}")
    #else:
    #    return str(f"Break time!\n{currentdate}\n{localtime}")
print(current_time())
