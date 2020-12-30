
#-*- coding:utf-8 -*-
import csv
import os, shutil
import time

import songBox_list as sbl

nowDate =  time.strftime("%Y_%m_%d")

baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','youtube-dl.exe','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록

#===============1번 사용 class ScreenSinger > singer 개수 체크 시====================
#===============return all singerList===========================================
def show_singer():
    singerList = os.listdir(f"{singerListDir}")
    for i in ignoreFile:
        if i in singerList:
            singerList.remove(i)
    return singerList

#===============1번 사용 class ScreenSinger > def open_singerSongPopup============
#===============return singer의 songlist=========================================
def show_onerSinger(singer):
    singerSongList = os.listdir(f"{singerSongList}\\{singer}")

    for i in ignoreFile:
        if i in singerSongList:
            singerSongList.remove(i)
    return singerSongList

#===============1번 사용 def make_singerDic 에서 호출===============================
#===============return singerDic->{singer:[곡명]}================================
def sort_singer():
    totalList = os.listdir(f"{mp3Dir}")
    singerDic = {}
    songList = []
    print("sort_singer")

    for i in totalList:
        if i not in ignoreFile:
            division = i.split(".wav")
            division = division[0].split("_")
            song = division[0].lower()
            singer = division[1].lower()

            if singer not in singerDic:
                songList.append(i)
                singerDic[singer] = songList
                songList = []
            else:
                songList = singerDic[singer]
                songList.append(i)
                singerDic[singer] = songList
                songList=[]

    for i in singerDic:
        print(f"{i}:{singerDic[i]}\n")

    return singerDic

#===============4번 사용 1.app 시작 2.UpperMenu>def callSyncSong 3.곡다운로드받은후
#4. songBox_list > def touch_title==============================================
#===============def make_singerDic > def copy_song > 동기화 ======================
def make_singerDic():
    singerDic = sort_singer()
    print(singerDic)
    nowList = os.listdir(f"{singerListDir}")
    totalList = os.listdir(f"{mp3Dir}")

    newSingerDic = {}
    newSongList = []

    wrongDic = {}
    wrongList = []

    #지워진 가수 폴더 식별해서 삭제
    for i in nowList:
        if i not in ignoreFile and i not in singerDic:
            shutil.rmtree(f"{singerListDir}\\{i}", ignore_errors=True)
            #print(f"remove dir:{i}")

    nowList = os.listdir(f"{singerListDir}")

    #새로 추가된 가수 폴더 생성
    for i in singerDic:
        if i not in nowList:
            #없는 가수 폴더 만들기
            try:
                os.mkdir(f"{singerListDir}\\{i}")
                newSingerDic[i]=singerDic[i]#new
                #print(f"{i} exist")
            except Exception as msg:
                print(f"{i} not exist")

        #가수 폴더 안에 없는 곡이나 있는 곡 동기화(전체 곡 기준으로)
        if i in nowList:

            thisSingerDir = os.listdir(f"{singerListDir}\\{i}")
            nowNum= len(thisSingerDir)

            #가수 폴더 안에 곡이 하나도 없고 폴더만 남아있는 경우 파악
            if nowNum == 0:
                newSingerDic[i]=singerDic[i]

            elif nowNum !=0:

                #가수 폴더 안에 없는 곡 파악해서 추가
                for j in singerDic[i]:
                    if j not in thisSingerDir:
                        newSongList.append(j)
                        newSingerDic[i]= newSongList
                        #print(f"add new song{newSingerDic[i]}")

                newSongList = []
                #가수 폴더 안에 있는데, 없어진 곡 파악해서 삭제

                for k in thisSingerDir:

                    if k not in ignoreFile and k not in singerDic[i]:
                        division = k.split(".wav")
                        division = division[0].split("_")
                        song = division[0].lower()
                        singer = division[1].lower()

                        #다른 가수의 곡이 들어가있는 경우 -> 해당 폴더에서 삭제 & singerDic에 추가
                        if singer != i:
                            shutil.copy(f"{singerListDir}\\{i}\\{k}",f"{mp3Dir}")
                            os.remove(f"{singerListDir}\\{i}\\{k}")
                            wrongList.append(k)
                            wrongDic[singer] = wrongList

                        else:
                            #shutil.copy(f"{singerListDir}\\{i}\\{k}",f"{mp3Dir}") #전체 곡에 추가하는 방법
                            os.remove(f"{singerListDir}/{i}/{k}") #전체 곡에서도 지우는 방법
                #print(f"wrongList:{wrongList}")
                wrongList = []

    for i in wrongDic:
        wrong = wrongDic[i]
        newSingerDic[i] = wrong
        os.mkdir(f"{singerListDir}\\{i}")

    #print(f"newSingerDic{newSingerDic}")

    return copy_song(newSingerDic)

#===============1번 사용 def make_singerDic 처리 후, 호출 ===========================
#===============실제로 wav 곡을 singerlist dir 로 copy==============================
def copy_song(newSingerDic):

    get_newSingerDic = newSingerDic
    totalList = os.listdir(f"{mp3Dir}")

    for i in get_newSingerDic:
        for j in get_newSingerDic[i]:
            try:
                shutil.copy(f"{mp3Dir}\\{j}",f"{singerListDir}\\{i}")
                print(f"{msg}.{j}in mp3Dir")
            except Exception as msg:
                print(f"{msg}.{j} not in mp3Dir")

    return get_newSingerDic
"""
def show_newSong():
    singerDic = sort_singer()
    nowList = os.listdir(f"{singerListDir}")
    os.chdir(f"{singerListDir}")
    newSinger = []

    for i in singerDic:
        if i not in nowList:
            os.mkdir(i)
            newSinger.append(i)

    return newSinger
"""
