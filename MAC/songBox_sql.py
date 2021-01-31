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

songDir = "/Users/soos/Desktop/git/4.web_song/hobby_songbox_web/song/" #songBox_web song 폴더

#==============sql db song, singer 값 가져오기=====================================
def get_data():
    sql_singerlist = []
    sql_songlist = []
    new=""

    conn = sql.connect(host='localhost', user='', password='', charset='utf8', db='songbox')
    cursor = conn.cursor()

    sql_singer = "SELECT name FROM singer;"
    cursor.execute(sql_singer)
    res = cursor.fetchall() #fetchone()은 열 하나만

    for i in res:
        for j in i:
            if j != ",":
                new+=j

        sql_singerlist.append(new)
        new=""

    sql_song = "SELECT song FROM song;"
    cursor.execute(sql_song)
    res = cursor.fetchall()

    for i in res:
        for j in i:
            if j != ",":
                new+=j

        sql_songlist.append(new)
        new=""

    conn.close()

    return sql_singerlist, sql_songlist

#==============한번에 데어터 넣을 때만 사용하기=========================================
#==============sql db와 현재 songDir안에 곡 비교해서 데이터 넣기->======================
#저장되어있지 않는 것만 song, singer table 에 저장=====================================

def sync_sqlWebsong():

    sql_singerlist, sql_songlist = get_data()
    print(f"{sql_singerlist}\n{sql_songlist}")

    conn = sql.connect(host='localhost', user='', password='', charset='utf8', db='songbox')
    cursor = conn.cursor()

    for i in os.listdir(f"{songDir}"):
        temp = i.split("_")
        song = temp[0]

        temp = temp[1].split(".")
        singer = temp[0]
        filetype = temp[1]

        if (song in sql_songlist and singer not in sql_singerlist) or song not in sql_songlist:
            sql_query = "insert into song(song,filetype,singer,created) values(%s,%s,%s,NOW())"
            cursor.execute(sql_query,(song,filetype,singer))
            conn.commit()
            sql_songlist.append(song)
            print(f"song:{song}\nfile:{filetype}")
            time.sleep(1)

        if singer not in sql_singerlist:
            sql_query = "insert into singer(name,created) values(%s,NOW())"
            cursor.execute(sql_query,(singer))
            conn.commit()
            sql_singerlist.append(singer)
            print(f"singer:{singer}")
            time.sleep(1)

    conn.close()

#===============youtube down받고 sql db songbox->song table 에 저장 ->webSongdir로 파일 복사===
def down_song(song, singer, filetype):

    singerlist = sbs.show_singer();

    #sql연결
    conn = sql.connect(host='localhost', user='', password='', charset='utf8', db='songbox')

    # server에 연결에 성공하면, connection객체로부터 cursor()메소드를 통해 cursor 객체를 가져올 수 있음.
    cursor = conn.cursor()

    sql_query = "insert into song(song,filetype,singer,created) values(%s,%s,%s,NOW())"
    #cursor 객체의 execute 메서드를 이용해서 sql  문장을 실행할 수 있음.
    cursor.execute(sql_query,(song,filetype,singer))

    # 실행한 sql 결과를 서버에 확정 반영하기
    conn.commit()

    print("test_:", song, singer, filetype)

    if singer.lower() not in singerlist:
        print("singerlist:", singerlist)
        print("singer_", singer.lower(),singer)

        sql_query = "insert into singer(name,created) values(%s,NOW())"

        cursor.execute(sql_query,(singer))

        conn.commit()

    move_websong(song, singer, filetype)

    conn.close()

#===============webSongdir로 파일 복사=============================================
def move_websong(song, singer, filetype):
    src = f"{song}_{singer}.{filetype}"
    shutil.copy(f"{mp3Dir}/{src}",f"{songDir}/{src}")


#sync_sqlWebsong();
