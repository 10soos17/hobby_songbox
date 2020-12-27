#!/usr/bin/python3
#-*- coding:utf-8 -*-
import csv
import os, shutil
import time

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

#===============class ScreenSong 내부...layout 사용===============================
def show_Song():
    mySongs = []
    for i in os.listdir(f"{mp3Dir}"):
        if i not in ignoreFile:
            now = int(time.time())
            downTime= int(os.stat(f'{mp3Dir}\\{i}').st_atime)#st_ctime(수정시간),st_atime(파일접근한(다운로드)날짜),st_mtime(파일만든날짜)
            period = (now - downTime)//3600
            if period <= 48:
                mySongs.append(f"*NEW* {i}")
            else:
                mySongs.append(i)
    return mySongs

#===============class UpperMenu > def delete_pressed 사용========================
def delete_Song(song, singer):
    reSong = song.lower()
    reSinger = singer.lower()

    for i in os.listdir(f'{mp3Dir}'):
        if i not in ignoreFile:
            newNameDir = i[:-4]
            newNameDir = newNameDir.lower()
            splitNameDir=list(newNameDir.split('_'))
            newSongDir=splitNameDir[0]
            newSingerDir=splitNameDir[1]

            if reSong == newSongDir and reSinger == newSingerDir:
                os.remove(f'{mp3Dir}\\{song}_{singer}.wav')
                sync_song()
                return True
    return False #곡이 존재하지않음

#===============class SongScreen > def open_titlePopup의 edit 버튼 클릭 시 호출됨====
#===============song title 변경==================================================
def touch_title(beforeTitle, song, singer):
    song =song.text
    singer = singer.text
    print(f"beforeTitle:{beforeTitle},Song:{song},Singer:{singer}")

    beforeTitle = beforeTitle.split('+')
    beforeTitle = beforeTitle[0].split('* ')
    beforeTitle = beforeTitle[1].split('_')

    beforeSong=beforeTitle[0]
    beforeSinger=beforeTitle[1].split('.wav')
    beforeSinger = beforeSinger[0]

    beforeTitle = f"{beforeSong}_{beforeSinger}.wav"
    newTitle = f"{song}_{singer}.wav"

    #songdir and singerdir change
    for i in os.listdir(f'{mp3Dir}'):
        if i == beforeTitle:
            os.rename(f'{mp3Dir}\\{i}',f'{mp3Dir}\\{newTitle}')

            sync_song()
            sbs.make_singerDic()

            print(f"newTitle:{newTitle}")
            return True


#===============tempList에 기존 csv 노래 저장 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>현재 List에 있는 노래와 비교하며 동기화(추가, 삭제) >>>>
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>최종 csv 파일 업데이트=====
#1.App 시작 2.youtb_converter>def change_Song(다운로드 받은 후, 동기화) 3.class UpperMenu>def callSyncSong(img버튼클릭시,동기화)
def sync_song():
    tempList=[]
    #==========가장 최근 csv datalist 읽기:  tempList에 저장=========
    songReadFile = open(f'{dataDir}\\songBox_data.csv','r',encoding='UTF-8')
    for i in songReadFile:
        i =i[:-1]
        #print(f'{i}\n', end='')
        tempList.append(i)

    songReadFile.close()

    #======List폴더에 있으나, 기존 csv(=tempList)에 없는 곡 추가: newTemPList에 추가=====
    newTempList=list(tempList) #oldlist복사
    addList=[] #추가될data저장
    subList=[] #지울data저장
    newList=[]
    for i in os.listdir(f'{mp3Dir}'):
        if i not in ignoreFile:

            if i not in newTempList:
                newTempList.append(i)
                addList.append(i)

    addNum =  len(addList)
    print(f'Old List:\n{tempList}\n\nNew List:\n{newTempList}\n')

    #======List 폴더에 없는데,기존 csv(=tempList)에 있는 곡 삭제: newTempList에서 삭제====
    count = 0
    dirLength = len(os.listdir(f'{mp3Dir}'))
    for i in newTempList:
        if i in os.listdir(f'{mp3Dir}'):
            for j in os.listdir(f'{mp3Dir}'):
                if i == j:
                    break
                else:
                    count+=1
            if dirLength == count:
                newTempList.remove(i)
                subList.append(i)
            count=0
        elif i not in os.listdir(f'{mp3Dir}'):
            newTempList.remove(i)
            subList.append(i)

    subNum = len(subList)
    totalNum = len(newTempList)
    newTempList.sort()

    #==========list폴더 내 목록(=newTempList)의 업데이트된 내용으로 csv파일 새로 쓰기=======
    songWriteFile = open(f'{dataDir}\\songBox_data_{nowDate}.csv','w',encoding='UTF-8')
    for i in newTempList:
        songWriteFile.write(f'{i}\n')
    songWriteFile.close()
    #===========해당날짜 csv파일 복사해두기==========================================
    shutil.copy(f'{dataDir}\\songBox_data_{nowDate}.csv', f'{dataDir}\\songBox_data.csv')

    print(f'{addNum} add.\n{subNum} delete.\nTotal: {totalNum}\n')
    print(f'Added song:\n{addList},\n\nDeleted song:\n\n{subList}\n')

    os.chdir(f'{baseDir}')

    return newTempList
