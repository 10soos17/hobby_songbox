#!/usr/bin/python3
#-*- coding:utf-8 -*-
import csv
import os, shutil
import time


#nowDate =  time.strftime("%Y_%m_%d")#global workingDir,baseDir,mp3Dir,dataDir,userListDir,ignoreFile
baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록
#print(f"baseDir:{baseDir}\nmp3Dir:{mp3Dir}\ndataDir:{dataDir}\nuserListDir:{userListDir}\nsingerListDir:{singerListDir}")
#===============class ScreenSetting>def listMake_pressed(userlist dir 생성 시)====
def make_userlist(listName):
    try:
        os.makedirs(f'{userListDir}/{listName}')
        return True
    except Exception as msg:
            res = f"{msg}failed."
            return False

#===============class ScreenSetting>def listDelete_pressed(userlist dir 삭제 시)==
def delete_userlist(listName):

    userlist = show_userlist()

    for i in userlist:

        if userlist[i] == listName:
            startNum = int(i)
            try:
                shutil.rmtree(f'{userListDir}\\{startNum}. {userlist[i]}', ignore_errors=True) #강제삭제

                #renumbering
                userlist = show_userlist()

                for j in userlist:
                    print(userlist[j])
                    if int(j) > startNum:
                        os.rename(f'{userListDir}\\{int(j)}. {userlist[j]}', f'{userListDir}\\{int(j)-1}. {userlist[j]}')

                return True

            except Exception as msg:
                    res = f"{msg}failed."
                    return False

#===============3번 사용==========================================================
#===1,2.class ScreenSetting>def drawMylist, def press_settingBTN 3.class ScreenSong>def add_userlist
def show_userlist():
    myLists = {}
    for i in os.listdir(f"{userListDir}"):
        if i not in ignoreFile:
            numbering = i.split(". ")
            myLists[str(numbering[0])] = numbering[1]

    return myLists

#===============class ScreenSetting>def del_userlistSong(popup에서 userlist dir 삭제 시)
def show_oneUserlist(checkedOneUserlist):
    nowUserlist = show_userlist()
    thisOnesongList = ''
    for i in nowUserlist:
        if checkedOneUserlist == nowUserlist[i]:
            thisOnesongList = os.listdir(f"{userListDir}\\{i}. {nowUserlist[i]}")
            #print(thisOnesongList)
            break

    return thisOnesongList

#===class SettingScreen > def open_userTitlePopup>def res_touchTitle에서 호출됨====
#===============userlist title 변경==============================================
def touch_userTitle(before, new):
    newTitle = new.text
    beforeTitle = before

    nowUserlist = show_userlist()

    #os.chdir(f'{userListDir}')

    for i in nowUserlist:
        if nowUserlist[i] == beforeTitle:
            os.rename(f'{userListDir}\\{i}. {nowUserlist[i]}',f'{userListDir}\\{i}. {newTitle}')
            return True
    return False

#===============class ScreenSong>def add_pressed(체크된 곡 add한 것을 실제로 userlist dir안에 copy)
def copy_checkedsongTOuserlist(CHECKEDUSERLIST,CHECKEDSONGTITLE):
    nowUserlist = show_userlist()#os.listdir(f"{userListDir}")
    nowSonglist = os.listdir(f"{mp3Dir}")
    #print(nowUserlist,nowSonglist)
    #print(CHECKEDUSERLIST,CHECKEDSONGTITLE)
    for i in nowUserlist:
        if nowUserlist[i] in CHECKEDUSERLIST and nowUserlist[i] not in ignoreFile:
            print(i)
            for j in nowSonglist:
                if j in CHECKEDSONGTITLE and j not in ignoreFile:
                    print(j)
                    try:
                        shutil.copy(f"{mp3Dir}\\{j}",f"{userListDir}\\{i}. {nowUserlist[i]}")
                    except Exception as msg:
                        res = f"{msg} failed."
                        return False
