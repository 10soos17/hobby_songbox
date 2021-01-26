#!/usr/bin/python3
#-*- coding:utf-8 -*-
import csv
import os, shutil
import time

import pymysql as sql

import songBox_singerlist as sbs

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

#===============youtube down받고 sql db songbox->song table 에 저장================
def down_song(song, singer, filetype):
    singerlist = sbs.show_singer();

    #sql연결
    conn = sql.connect(host='', user='', password='', charset='utf8', db='')

    # server에 연결에 성공하면, connection객체로부터 cursor()메소드를 통해 cursor 객체를 가져올 수 있음.
    cursor = conn.cursor()

    sql_query = "insert into song(song,filetype,singer,created) values(%s,%s,%s,NOW())"
    #cursor 객체의 execute 메서드를 이용해서 sql  문장을 실행할 수 있음.
    cursor.execute(sql_query,(song,filetype,singer))

    # 실행한 sql 결과를 서버에 확정 반영하기
    conn.commit()

    print("test_:", song, singer, filetype)

    if singer.lower() not in singerlist:
        print("test_singerlist:", singerlist)
        print("singer_", singer.lower(),singer)

        sql_query = "insert into singer(name,created) values(%s,NOW())"

        cursor.execute(sql_query,(singer))

        conn.commit()

    conn.close()

#down_song("Stairway To Heaven","The OJays", "wav")
#save_song(song,filetype,genre,feat,lyrics,singer,year,created)
#save_singer(name,country,year,created)
