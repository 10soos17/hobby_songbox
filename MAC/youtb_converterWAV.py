#!/usr/bin/python3
#-*- coding:utf-8 -*-
from kivy.core.audio import SoundLoader

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, os

import songBox_list as sbl
import songBox_singerlist as sbs
import songBox_sql as sb_sql

baseDir = os.getcwd()#os.path.abspath('py_song')#workging 폴더
mp3Dir = os.path.join(baseDir, "songBox_list")#노래 폴더
fontDir = os.path.join(baseDir, "songBox_font")#글자 폴더
imgDir = os.path.join(baseDir, "songBox_img")#그림 폴더
dataDir = os.path.join(mp3Dir, "0_file_data")#데이터목록 csv 저장폴더
userListDir = os.path.join(mp3Dir, "1_dir_userlist")#userlist 폴더
singerListDir = os.path.join(mp3Dir, "2_dir_singerlist")#userlist 폴더
ttsDir = os.path.join(mp3Dir, "3_tts")#tts 폴더
ignoreFile = ['ffmpeg','.DS_Store','list_data','0_file_data','1_dir_userlist','2_dir_singerlist','3_tts']#dir 안에 존재해야만하는 파일 but mp3 아닌 파일 목록
filetype = "wav"

#===============get chrome driver===============================================
def get_driver():
   try:
      print(f"get_try")
      driver = webdriver.Chrome(f'{baseDir}/chromedriver')
   except:
      print(f"get_tryerror")
      driver = webdriver.Chrome(f'{baseDir}/chromedriver.exe')
   return driver

#===============song select 할 때 사용 - 검색하고 list 폴더 안에 mp3 저장 ==============
#===============class UpperMenu>def songBox_pressed(팝업에서 add버튼 클릭시, thread)=
def change_Song(song, singer):
    #song = input("song?")
    os.chdir(f'{baseDir}')
    myDriver = get_driver() # os 고려하기
    myDriver.get(f'https://www.youtube.com/results?search_query={song} {singer}')
    print(f"getsong_try")
    #myDriver.find_element_by_id('img').click()
    url = myDriver.find_element_by_xpath('//*[@id="video-title"]')
    urlAddress=url.get_attribute('href')
    urlSplit=list(urlAddress.split("="))
    songAddress=urlSplit[1]

    shareAddress = f'https://youtu.be/{songAddress}'
    shareAddressTwo = f'https://www.youtube.com/watch?v={songAddress}'
    print(urlAddress,songAddress, shareAddress)
    #youtube-dl -x --audio-format mp3 <동영상 주소> or <재생목록 주소>
    #youtube-dl -x --audio-format mp3 https://youtu.be/75fEhQlc9h4

    #===============다운로드 시도==================================================
    try:
        os.chdir(f'{mp3Dir}')
        beforeDown = os.listdir(f'{mp3Dir}')
        res = os.system(f'youtube-dl -x --audio-format wav {shareAddress}')

        print(f"1 try:{res}")
        time.sleep(3)
        if res != 0:
            res = os.system(f'youtube-dl -x --audio-format wav {shareAddressTwo}')
            print(f"2 try:{res}")

        afterDown = os.listdir(f'{mp3Dir}')

        #===============다운로드 후에, 동기화 등의 결과 처리=============================
        for i in os.listdir(f'{mp3Dir}'):
            if i not in beforeDown:
                os.rename(i, f'{song}_{singer}.wav')
                sb_sql.down_song(song, singer, filetype) #save mysql
                sbl.sync_song() #song
                sbs.make_singerDic() #singer


        time.sleep(20)

        os.chdir(f'{baseDir}')
        if res != 0: #mp3 다운받지 못함
            myDriver.quit()
            myDriver.close()
            return f"res:{res}"
        else:
            myDriver.quit()
            myDriver.close()
            return f"res:{res}"

    #===============try,except 다운로드 시도 실패 시=================================
    except Exception as msg:
            os.chdir(f'{baseDir}')
            myDriver.quit()
            myDriver.close()
            return f"res:{res}"
